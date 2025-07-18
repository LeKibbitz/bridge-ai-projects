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
from selenium.webdriver.chrome.service import Service
import os
import traceback

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
        print("Starting from main FFB website...")
        self.driver.get("https://www.ffbridge.fr/")
        print("Waiting for site to load...")
        time.sleep(5)
        current_url = self.driver.current_url
        print(f"Current URL after loading: {current_url}")
        if "auth/login" in current_url:
            print("Redirected to login page, proceeding with login...")
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
    
    def scrape_entites(self):
        import pandas as pd
        print("Navigating to Entités dashboard...")
        self.driver.get("https://metier.ffbridge.fr/#/entites/tableau-de-bord")
        time.sleep(3)
        print("Looking for the entités dropdown...")
        dropdown = self.driver.find_element(By.CSS_SELECTOR, "select[ng-model='searchOrganizationCtrl.currentOrganization']")
        options = dropdown.find_elements(By.TAG_NAME, "option")
        print(f"Found {len(options)} options in the entités dropdown.")
        # Extract all club info first to avoid stale element reference
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
            clubs_to_process.append({'id': club_id, 'code': club_code, 'nom': club_name, 'region': 'Lorraine'})
        print(f"Total clubs to process: {len(clubs_to_process)}")
        clubs = []
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'FFB_Scraped_Data')
        clubs_file = os.path.join(output_dir, 'clubs.csv')
        for club in clubs_to_process:
            print(f"Processing club option: {club['code']} - {club['nom']}")
            info_url = f"https://metier.ffbridge.fr/#/entites/{club['id']}/informations"
            print(f"Visiting club info page: {info_url}")
            self.driver.get(info_url)
            time.sleep(2)
            # TODO: Scrape all data except excluded sections
            clubs.append(club)
            # Save after each club
            clubs_df = pd.DataFrame(clubs)
            clubs_df.to_csv(clubs_file, index=False, sep='\t')
            print(f"[Progress] Saved {len(clubs_df)} clubs to {clubs_file} after {club['nom']}")
        print(f"Total clubs found: {len(clubs)}")
        return clubs
    
    def scrape_licensees(self, club_id, club_name, players_file):
        members = []
        # Scrape current members
        self.driver.get(f"{METIER_URL}#/entites/{club_id}/membres/consultation")
        members.extend(self._scrape_members_list(club_id, club_name))
        # Scrape renewal members
        self.driver.get(f"{METIER_URL}#/entites/{club_id}/membres/renouvellement")
        members.extend(self._scrape_members_list(club_id, club_name))
        # Save after each club
        if members:
            import pandas as pd
            players_df = pd.DataFrame(members)
            players_df.to_csv(players_file, index=False, sep='\t')
            print(f"[Progress] Saved {len(players_df)} players to {players_file} after club {club_name}")
        return members

    def _scrape_members_list(self, club_id, club_name):
        members = []
        try:
            members_table = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "members-table"))
            )
            rows = members_table.find_elements(By.TAG_NAME, "tr")
            for row in rows[1:]:  # Skip header
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) > 0:
                    licence = cells[2].text.strip()
                    member_type = 'Membre'
                    if licence.endswith('s'):
                        licence = licence[:-1]
                        member_type = 'Sympathisant'
                    member_data = {
                        "nom": cells[0].text,
                        "prenom": cells[1].text,
                        "numero_licence": licence,
                        "statut": cells[3].text,
                        "club_id": club_id,
                        "club_nom": club_name,
                        "member_type": member_type
                    }
                    members.append(member_data)
        except Exception as e:
            print(f"Error scraping members list for club {club_name}: {e}")
        return members
    
    def close(self):
        self.driver.quit()

def main():
    scraper = FFBScraper()
    try:
        # Create the output directory if it doesn't exist
        import os
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'FFB_Scraped_Data')
        os.makedirs(output_dir, exist_ok=True)
        players_file = os.path.join(output_dir, 'players.csv')
        
        scraper.login()
        print("Scraping entities...")
        entites = scraper.scrape_entites()
        print(f"DEBUG: entites type: {type(entites)}, value: {entites}")
        if not isinstance(entites, list):
            print(f"ERROR: entites is not a list! It is: {type(entites)} with value: {entites}")
            entites = []
        if entites:
            # Convert entity dicts to DataFrame
            clubs_df = pd.DataFrame(entites)
            clubs_file = os.path.join(output_dir, 'clubs.csv')
            clubs_df.to_csv(clubs_file, index=False, sep='\t')
            print(f"Saved {len(clubs_df)} clubs to {clubs_file}")
            
            print("Scraping members...")
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
                players_df.to_csv(players_file, index=False, sep='\t')
                print(f"[Final] Saved {len(players_df)} players to {players_file}")
            else:
                print("No members found")
        else:
            print("No entities found")
            # Create empty CSV files
            empty_clubs_df = pd.DataFrame(columns=['id', 'nom', 'region'])
            clubs_file = os.path.join(output_dir, 'clubs.csv')
            empty_clubs_df.to_csv(clubs_file, index=False, sep='\t')
            empty_players_df = pd.DataFrame(columns=['nom', 'prenom', 'numero_licence', 'statut', 'club_id', 'club_nom', 'member_type'])
            players_file = os.path.join(output_dir, 'players.csv')
            empty_players_df.to_csv(players_file, index=False, sep='\t')
            print(f"Created empty CSV files in {output_dir}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
