from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from scripts.config import FFB_USERNAME, FFB_PASSWORD, LOGIN_URL, METIER_URL
from scripts.models import Entite, Licensee
import time
from datetime import datetime
import json
import pandas as pd
import csv
import io
from selenium.webdriver.chrome.service import Service
import os
import traceback

# === SCRAPER REFACTOR PLAN IMPLEMENTATION ===
# See README.md for detailed plan and rationale
#
# - Batch-first scraping: clubs/entities, then members
# - Section-by-section deep scraping (TODOs for each tab/section)
# - Dynamic DataFrame handling: add columns as new fields are found
# - Robust progress/error handling and data safety
#
# ============================================

class FFBScraper:
    def __init__(self):
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, 10)
        
    def _setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Use the manually downloaded ChromeDriver for Mac ARM64
        driver_path = "/Users/lekibbitz/chromedriver_arm64"
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    
    def login(self):
        # Start from the main FFB website
        print("Starting from FFB Login Page...")
        self.driver.get("https://www.ffbridge.fr/auth/login")
        print("Waiting for site to load...")
        time.sleep(5)
        current_url = self.driver.current_url
        print(f"Current URL after loading: {current_url}")
        if "auth/login" in current_url:
            print("Proceeding with login...")
            self._perform_login()
        else:
            print("Not redirected to login, checking if we can access metier...")
            self.driver.get("https://metier.ffbridge.fr/#/home")
            time.sleep(3)
            print(f"Metier URL: {self.driver.current_url}")
            if "auth/login" in self.driver.current_url:
                print("Metier redirected to login, proceeding with login...")
                self._perform_login()
            else:
                print("Successfully accessed metier without login!")
                return
        # Always ensure we are in the metier environment before proceeding
        if not ("metier.ffbridge.fr" in self.driver.current_url):
            print("Not in metier environment after login attempts. Aborting scrape_entites.")
            return []
    
    def _perform_login(self):
        try:
            # Wait a moment for page to load
            time.sleep(3)
            print(f"Page title: {self.driver.title}")
            
            # Debug: List all input elements on the page
            print("Looking for input elements...")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"Found {len(inputs)} input elements:")
            for i, inp in enumerate(inputs):
                print(f"  {i}: id='{inp.get_attribute('id')}', type='{inp.get_attribute('type')}', name='{inp.get_attribute('name')}'")
            
            # Wait for login form - find elements by type instead of ID (since IDs are dynamic)
            print("Waiting for email input...")
            email_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
            print("Email input found")
            
            print("Waiting for password input...")
            password_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
            print("Password input found")
            
            # Fill login form
            print("Filling login form...")
            email_input.send_keys(FFB_USERNAME)
            password_input.send_keys(FFB_PASSWORD)
            
            # Submit form
            print("Looking for submit button...")
            submit_button = None
            try:
                # Try exact match, all caps
                submit_button = self.driver.find_element(By.XPATH, "//button[translate(normalize-space(text()), 'abcdefghijklmnopqrstuvwxyzéèêëàâäîïôöùûüç', 'ABCDEFGHIJKLMNOPQRSTUVWXYZÉÈÊËÀÂÄÎÏÔÖÙÛÜÇ') = 'SE CONNECTER']")
                print("Submit button found (all caps), clicking...")
            except Exception as e:
                print(f"Submit button not found with all-caps selector: {e}")
                # Try contains (case-insensitive)
                try:
                    submit_button = self.driver.find_element(By.XPATH, "//button[contains(translate(normalize-space(text()), 'abcdefghijklmnopqrstuvwxyzéèêëàâäîïôöùûüç', 'ABCDEFGHIJKLMNOPQRSTUVWXYZÉÈÊËÀÂÄÎÏÔÖÙÛÜÇ'), 'SE CONNECTER')]")
                    print("Submit button found (contains, case-insensitive), clicking...")
                except Exception as e2:
                    print(f"Submit button not found with contains selector: {e2}")
                    # Print all button texts and HTML for debugging
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    print("All button texts and HTML on page:")
                    for i, btn in enumerate(buttons):
                        outer_html = btn.get_attribute('outerHTML')
                        if outer_html is None:
                            outer_html = 'None'
                        else:
                            outer_html = outer_html[:200]
                        print(f"  {i}: text='{btn.text}' type='{btn.get_attribute('type')}' class='{btn.get_attribute('class')}' html='{outer_html}'")
                    # Fallback: click the first submit-type button
                    for btn in buttons:
                        if btn.get_attribute('type') == 'submit':
                            submit_button = btn
                            print("Fallback: clicking first submit-type button.")
                            break
            if submit_button:
                try:
                    submit_button.click()
                    print("Clicked the submit button successfully.")
                except Exception as click_exc:
                    print(f"ERROR: Exception occurred while clicking submit button: {click_exc}")
                    return
            else:
                print("ERROR: Could not find a submit button to click! Aborting login.")
                return
            
            # Wait a moment and check what happened
            print("Waiting a moment after submit...")
            time.sleep(3)
            print(f"Current URL after submit: {self.driver.current_url}")
            print(f"Page title after submit: {self.driver.title}")
            
            # Wait for redirect to dashboard
            print("Waiting for redirect to dashboard...")
            self.wait.until(EC.url_contains("ffbridge.fr/user/dashboard"))
            print("Successfully logged in!")
            
            # Now click the correct 'ACCÉDER' button to access the Métier environment
            print("Looking for 'ACCÉDER' button to access Métier environment...")
            time.sleep(3)
            acceder_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Accéder')]")
            print(f"Found {len(acceder_buttons)} 'Accéder' buttons")
            target_button = None
            for i, button in enumerate(acceder_buttons):
                try:
                    parent = button.find_element(By.XPATH, "./..")
                    parent_text = parent.text.lower()
                    print(f"Button {i+1} parent text: {parent_text[:100]}...")
                    if "mon espace métier" in parent_text or "espace métier" in parent_text:
                        target_button = button
                        print("Found 'Accéder' button under 'Mon espace métier'")
                        break
                except Exception as e:
                    print(f"Error checking button {i+1}: {e}")
                    continue
            if target_button:
                print("Clicking the correct 'Accéder' button...")
                target_button.click()
            else:
                print("Could not find 'Accéder' button under 'Mon espace métier', clicking the first one if available...")
                if acceder_buttons:
                    acceder_buttons[0].click()
                else:
                    print("No 'Accéder' buttons found! Aborting login.")
                    return
            # Wait for the new tab to open
            print("Waiting for new tab to open...")
            time.sleep(3)
            print(f"Window handles: {self.driver.window_handles}")
            if len(self.driver.window_handles) > 1:
                print("Switching to new tab (Métier environment)...")
                self.driver.switch_to.window(self.driver.window_handles[-1])
            else:
                print("Only one window handle, staying on current tab.")
            # Wait for the metier page to load
            print("Waiting for metier page to load...")
            time.sleep(5)
            print(f"Current URL in new tab: {self.driver.current_url}")
            print(f"Page title in new tab: {self.driver.title}")
            # Fail early if not in the Métier environment
            if not ("metier.ffbridge.fr" in self.driver.current_url):
                print("ERROR: Not in Métier environment after login and navigation! Aborting.")
                return []
        except Exception as e:
            print(f"EXCEPTION in _perform_login: {e}")
            traceback.print_exc()
            return
    
    def get_output_dir(self):
        # Always use the correct path relative to the script location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, '..', 'FFB_Scraped_Data')
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def scrape_entites(self):
        """
        Batch-first scraping of all clubs/entities.
        Dynamically adds columns as new fields are found.
        Saves clubs.csv only after all entities are processed.
        """
        print("Navigating to Entités dashboard...")
        self.driver.get("https://metier.ffbridge.fr/#/entites/tableau-de-bord")
        time.sleep(3)
        print("Looking for the entités dropdown...")
        dropdown = self.driver.find_element(By.CSS_SELECTOR, "select[ng-model='searchOrganizationCtrl.currentOrganization']")
        options = dropdown.find_elements(By.TAG_NAME, "option")
        print(f"Found {len(options)} options in the entités dropdown.")
        clubs_to_process = []
        for i, option in enumerate(options):
            code_label = option.text.strip()
            if i < 3 or not code_label.startswith("42"):
                continue
            if code_label.startswith("4200000"):
                print(f"Skipping Comité de Lorraine: {code_label}")
                continue
            if ' - ' in code_label:
                club_code, club_name = code_label.split(' - ', 1)
            else:
                club_code, club_name = code_label, ''
            club_id = option.get_attribute('value')
            clubs_to_process.append({'FFB Id': club_id, 'N°': club_code, 'Nom': club_name, 'Comité': 'Lorraine'})
        print(f"Total clubs to process: {len(clubs_to_process)}")
        clubs = []
        output_dir = self.get_output_dir()
        clubs_file = os.path.join(output_dir, 'clubs.csv')
        all_columns = set(['FFB Id', 'N°', 'Nom', 'Comité'])
        for idx, club in enumerate(clubs_to_process, 1):
            print(f"[Batch] ({idx}/{len(clubs_to_process)}) Processing club: {club['code']} - {club['nom']}")
            info_url = f"https://metier.ffbridge.fr/#/entites/{club['id']}/informations"
            self.driver.get(info_url)
            time.sleep(0.5)
            club_data = dict(club)
            # --- Scrape all visible fields in the main info section ---
            info_fields = self.driver.find_elements(By.CSS_SELECTOR, ".block-content .row")
            for field in info_fields:
                try:
                    label = field.find_element(By.CSS_SELECTOR, ".label").text.strip()
                    value = field.find_element(By.CSS_SELECTOR, ".value").text.strip()
                    if label and value:
                        col_name = label.replace(' ', '_').replace(':', '').lower()
                        club_data[col_name] = value
                        all_columns.add(col_name)
                except Exception:
                    continue
            # --- Section-by-section deep scraping (TODOs for each tab) ---
            # TODO: Scrape 'Acteurs' tab
            # TODO: Scrape 'Rôles' tab
            # TODO: Scrape other relevant tabs/sections
            clubs.append(club_data)
        # --- Dynamic DataFrame handling ---
        clubs_df = pd.DataFrame(clubs)
        for col in all_columns:
            if col not in clubs_df.columns:
                clubs_df[col] = ''
        # Reorder columns without passing as 'columns' parameter
        ordered_columns = [str(col) for col in all_columns if col in clubs_df.columns]
        clubs_df = clubs_df.loc[:, ordered_columns]
        clubs_df.to_csv(clubs_file, index=False, sep='\t')
        print(f"[Batch] Saved {len(clubs_df)} clubs to {clubs_file}")
        return clubs
    
    def scrape_licensees(self, club_id, club_name, players_file):
        """
        Dual-URL scraping for all members and their statuses.
        1. Scrape full member list from /facturation/encaissement
        2. Scrape renewed/consultation list from /membres/consultation
        3. Merge on license number, updating member_type/status
        4. Save merged DataFrame
        """
        all_columns = set(["numero_licence", "nom", "prenom", "club_nom", "club_id", "member_type", "statut"])
        # Step 1: Scrape full member list
        url_full = f"{METIER_URL}#/entites/{club_id}/facturation/encaissement"
        print(f"[Full List] Navigating to: {url_full}")
        self.driver.get(url_full)
        full_list = self._scrape_members_list_encaissement(club_id, club_name, all_columns)
        # Step 2: Scrape consultation/renewed list
        url_consult = f"{METIER_URL}#/entites/{club_id}/membres/consultation"
        print(f"[Consultation List] Navigating to: {url_consult}")
        self.driver.get(url_consult)
        consult_list = self._scrape_members_list_consultation(club_id, club_name, all_columns)
        # Step 3: Merge and update statuses
        full_df = pd.DataFrame(full_list)
        consult_df = pd.DataFrame(consult_list)
        if not full_df.empty and not consult_df.empty:
            merged_df = full_df.merge(consult_df[["numero_licence", "member_type"]], on="numero_licence", how="left", suffixes=("", "_consult"))
            # Fix: ensure both columns are Series before combine_first
            if "member_type_consult" in merged_df.columns and "member_type" in merged_df.columns:
                merged_df["member_type"] = pd.Series(merged_df["member_type_consult"]).combine_first(pd.Series(merged_df["member_type"]))
            elif "member_type_consult" in merged_df.columns:
                merged_df["member_type"] = merged_df["member_type_consult"]
            merged_df.drop(columns=["member_type_consult"], inplace=True, errors='ignore')
        else:
            merged_df = full_df if not full_df.empty else consult_df
        # Step 4: Save merged DataFrame
        for col in all_columns:
            if col not in merged_df.columns:
                merged_df[col] = ''
        ordered_columns = [str(col) for col in all_columns if col in merged_df.columns]
        merged_df = merged_df.loc[:, ordered_columns]
        merged_df.to_csv(players_file, index=False, sep='\t')
        print(f"[Dual-URL] Saved {len(merged_df)} players to {players_file} for club {club_name}")
        return merged_df.to_dict('records')

    def _scrape_members_list_encaissement(self, club_id, club_name, all_columns):
        members = []
        try:
            # Click the 'Tous les membres' OPGButton to ensure full list is displayed
            button_clicked = False
            wait = WebDriverWait(self.driver, 2)  # Further reduced timeout
            try:
                tous_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'option-group')]//button[contains(., 'Tous les membres')]"))
                )
                tous_button.click()
                print(f"Bouton 'Tous les membres' cliqué pour club {club_name} (ID: {club_id})")
                time.sleep(0.5)
                button_clicked = True
            except Exception as e:
                print(f"Impossible de cliquer sur 'Tous les membres' : {e}")
                # Fallback: try 'Licenciés' with a shorter wait
                try:
                    short_wait = WebDriverWait(self.driver, 1)
                    licencies_button = short_wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'option-group')]//button[contains(., 'Licenciés')]"))
                    )
                    licencies_button.click()
                    print(f"Bouton 'Licenciés' cliqué pour club {club_name} (ID: {club_id})")
                    time.sleep(0.5)
                    button_clicked = True
                except Exception as e2:
                    print(f"Impossible de cliquer sur 'Licenciés' non plus : {e2}")
            if not button_clicked:
                print(f"Aucun bouton OPGButton cliquable trouvé pour club {club_name} (ID: {club_id})")
            
            # Check for 'no members' message first
            try:
                no_members_msg = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Aucun membre') or contains(text(), 'Aucun résultat') or contains(text(), 'Aucune donnée')]")
                if no_members_msg:
                    print(f"Aucun membre trouvé pour club {club_name} (ID: {club_id})")
                    return []
            except Exception:
                pass  # No such message, proceed
            
            # Scrape current page only (removed while True loop to prevent hanging)
            try:
                # Wait for members table with timeout
                table_wait = WebDriverWait(self.driver, 2)
                table = table_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "members-table")))
                
                rows = table.find_elements(By.TAG_NAME, 'tr')
                if len(rows) <= 1:  # Only header or empty
                    print(f"Table vide pour club {club_name} (ID: {club_id})")
                    return []
                    
                csv_lines = []
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    csv_line = '\t'.join([cell.text.strip() for cell in cells])
                    csv_lines.append(csv_line)
                csv_text = '\n'.join(csv_lines)
                
                # Parse the CSV data
                csv_reader = csv.reader(io.StringIO(csv_text), delimiter='\t')
                
                # Skip header row
                headers = next(csv_reader)
                print(f"DEBUG - CSV Headers for {club_name}: {headers}")
                
                # Process data rows
                for row in csv_reader:
                    if len(row) >= 6:  # Ensure we have enough columns
                        member_data = {
                            'numero_licence': row[0],
                            'nom_complet': row[1], 
                            'type_licence': row[2],
                            'date_encaissement': row[3],
                            'montant': row[4],
                            'actions': row[5],
                            'club_id': club_id,
                            'club_nom': club_name
                        }
                        # Determine member status based on payment
                        if member_data['montant'] == '0,00€':
                            member_data['member_type'] = 'Non payé'
                        elif member_data['actions'] == 'Compte FFB':
                            member_data['member_type'] = 'Payé'
                        else:
                            member_data['member_type'] = 'En attente'
                        
                        all_columns.update(member_data.keys())
                        members.append(member_data)
                
            except Exception as e:
                print(f"Error parsing CSV data for club {club_name}: {e}")
                print(f"Current URL: {self.driver.current_url}")
                
        except Exception as e:
            print(f"Error scraping encaissement layout for club {club_name}: {e}")
        return members

    def _scrape_members_list_consultation(self, club_id, club_name, all_columns):
        # TODO: Implement scraping logic for /membres/consultation layout
        # For now, return an empty list as a placeholder
        print(f"Scraping consultation layout for club {club_name} (ID: {club_id})")
        return []
    
    def close(self):
        self.driver.quit()

def main():
    scraper = FFBScraper()
    try:
        output_dir = scraper.get_output_dir()
        clubs_file = os.path.join(output_dir, 'clubs.csv')
        players_file = os.path.join(output_dir, 'players.csv')
        all_columns = set([ "numero_licence", "nom", "prenom", "club_nom", "club_id", "member_type", "statut"])
        scraper.login()
        # Optimization: load clubs from CSV if it exists
        if os.path.exists(clubs_file):
            print(f"Loading clubs from {clubs_file}")
            clubs_df = pd.read_csv(clubs_file, sep='\t')
            entites = clubs_df.to_dict('records')
        else:
            print("Clubs CSV not found, scraping entities...")
            entites = scraper.scrape_entites()
            clubs_df = pd.DataFrame(entites)
            clubs_df.to_csv(clubs_file, index=False, sep='\t')
        if entites:
            print(f"Loaded {len(entites)} clubs. Starting member scraping...")
            all_members = []
            for entite in entites:
                try:
                    members = scraper.scrape_licensees(entite['id'], entite['nom'], players_file)
                    print(f"Found {len(members)} members for club {entite['nom']}")
                    all_members.extend(members)
                except Exception as e:
                    print(f"Error scraping members for club {entite['nom']}: {e}")
                    continue
            # Final save (redundant, but ensures all data is written)
            if all_members:
                players_df = pd.DataFrame(all_members)
                for col in all_columns:
                    if col not in players_df.columns:
                        players_df[col] = ''
                ordered_columns = [str(col) for col in all_columns if col in players_df.columns]
                players_df = players_df.loc[:, ordered_columns]
                players_df.to_csv(players_file, index=False, sep='\t')
                print(f"[Final] Saved {len(players_df)} players to {players_file}")
            else:
                print("No members found")
        else:
            print("No entities found")
            empty_clubs_df = pd.DataFrame([{"id": "", "nom": "", "region": ""}])
            clubs_file = os.path.join(output_dir, 'clubs.csv')
            empty_clubs_df.to_csv(clubs_file, index=False, sep='\t')
            empty_players_df = pd.DataFrame([{col: "" for col in all_columns}])
            players_file = os.path.join(output_dir, 'players.csv')
            empty_players_df.to_csv(players_file, index=False, sep='\t')
            print(f"Created empty CSV files in {output_dir}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
