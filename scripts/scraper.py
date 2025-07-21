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
    
    def scrape_ffb_entity(self, entity_id=1):
        """
        Scrape all required data for the FFB entity (ID: 1) as per the detailed spec.
        Returns a dictionary with all extracted data.
        """
        data = {}
        # 1. Go to the main informations page
        self.driver.get(f"https://metier.ffbridge.fr/#/entites/{entity_id}/informations")
        time.sleep(1)
        # --- Tab INFORMATIONS PRINCIPALES ---
        data.update(self.scrape_informations_principales())
        # --- Tab ACTEURS (Onglet Actifs) ---
        data['acteurs'] = self.scrape_acteurs_actifs()
        # --- Tab TABLEAU DE BORD (Onglet Licences et Tournois) ---
        data['stats'] = self.scrape_tableau_de_bord_stats()
        return data

    def scrape_informations_principales(self):
        """
        Scrape the 'Informations principales' tab for the FFB entity.
        Returns a dictionary with all required fields.
        """
        info = {}
        # Section Identification
        # - Nom de l’entité
        # - Numéro d’entité
        # - Type
        # - 4 checkboxes (with checked/not checked)
        # Section Subordination
        # - Entité de subordination
        # - Entité de regroupement
        # Section Coordonnées
        # - E-mail
        # - Site internet
        # - Téléphone principal
        # - Téléphone secondaire
        # - Commentaires
        # - Infos complémentaires (3 checkboxes with their status)
        # - Nombre de tables
        # - Horaires d’ouverture
        # - Saisonnier
        # - Organisme de tutelle
        # - Dates de fermeture
        # - Les plus du club
        # Section Photo de l’entité
        # - Texte, image, recommandations à droite de l’image
        # Section Adresse
        # - Jeu: all fields + Google map link
        # - Courrier: OPGButton (first option), 6 text boxes
        # - Facturation: same as Courrier
        # (Add code to extract each field here)
        return info

    def scrape_acteurs_actifs(self):
        """
        Scrape the 'Acteurs' tab, 'Actifs' sub-tab for the FFB entity.
        Returns a list of dictionaries, one per actor.
        """
        acteurs = []
        # Extract all rows from the Actifs list (handle pagination if needed)
        # (Add code to extract each actor here)
        return acteurs

    def scrape_tableau_de_bord_stats(self):
        """
        Scrape the 'Tableau de bord' tab, 'Licences et Tournois' sub-tab for the FFB entity.
        Returns a dictionary of stats tables, keyed by their title.
        """
        stats = {}
        # For each table in the section, extract the title and the table data
        # (Add code to extract each table here)
        return stats

    def scrape_zone_entity(self, entity_id=2):
        """
        Scrape all required data for a Zone entity as per the detailed spec.
        Returns a dictionary with all extracted data.
        """
        print(f"Scraping Zone entity (ID: {entity_id})...")
        data = {'entity_type': 'Zone', 'entity_id': entity_id}
        
        # 1. Go to the main informations page
        self.driver.get(f"https://metier.ffbridge.fr/#/entites/{entity_id}/informations")
        time.sleep(2)
        
        # --- Tab INFORMATIONS PRINCIPALES ---
        data.update(self.scrape_zone_informations_principales())
        
        # --- Tab ACTEURS ---
        data['acteurs'] = self.scrape_acteurs_tab()
        
        # --- Tab TOURNOIS ---
        data['tournois'] = self.scrape_zone_tournois_tab()
        
        return data

    def scrape_zone_informations_principales(self):
        """
        Scrape the 'Informations principales' tab for Zone entities.
        Returns a dictionary with all required fields.
        """
        info = {}
        
        # Section Identification (same as FFB)
        info.update(self.scrape_identification_section())
        
        # Section Subordination (only Entité de regroupement)
        try:
            reg_element = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Entité de regroupement')]/following-sibling::div")
            info['entite_regroupement'] = reg_element.text.strip()
        except:
            info['entite_regroupement'] = ''
        
        # Section Coordonnées (title present but no text block)
        info['coordonnees_titre_present'] = True
        info['coordonnees_bloc_texte'] = False
        
        # Section Adresse(s) mails de notifications de factures (same as Coordonnées)
        info['notification_factures_titre_present'] = True
        info['notification_factures_bloc_texte'] = False
        
        return info

    def scrape_zone_tournois_tab(self):
        """
        Scrape the 'Tournois' tab for Zone entities.
        Returns a dictionary with available options.
        """
        tournois = {}
        
        try:
            # Click on Tournois tab
            tournois_tab = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Tournois')]")
            tournois_tab.click()
            time.sleep(2)
            
            # Check for vertical banner with 3 choices
            try:
                organisation_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Organisation')]")
                tournois['organisation_clickable'] = True
            except:
                tournois['organisation_clickable'] = False
                
            try:
                livret_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Livret')]")
                tournois['livret_clickable'] = True
            except:
                tournois['livret_clickable'] = False
                
            try:
                calendrier_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Calendrier')]")
                tournois['calendrier_disponible'] = False  # Option indisponible
            except:
                tournois['calendrier_disponible'] = False
                
        except Exception as e:
            print(f"Error scraping Zone tournois tab: {e}")
            
        return tournois

    def scrape_ligue_entity(self, entity_id=18):
        """
        Scrape all required data for a Ligue entity as per the detailed spec.
        Returns a dictionary with all extracted data.
        """
        print(f"Scraping Ligue entity (ID: {entity_id})...")
        data = {'entity_type': 'Ligue', 'entity_id': entity_id}
        
        # 1. Go to the main informations page
        self.driver.get(f"https://metier.ffbridge.fr/#/entites/{entity_id}/informations")
        time.sleep(2)
        
        # --- Tab INFORMATIONS PRINCIPALES ---
        data.update(self.scrape_ligue_informations_principales())
        
        # --- Tab ACTEURS ---
        data['acteurs'] = self.scrape_acteurs_tab()
        
        # --- Tab TOURNOIS ---
        data['tournois'] = self.scrape_zone_tournois_tab()  # Same as Zone
        
        return data

    def scrape_ligue_informations_principales(self):
        """
        Scrape the 'Informations principales' tab for Ligue entities.
        Returns a dictionary with all required fields.
        """
        info = {}
        
        # Section Identification (same as FFB)
        info.update(self.scrape_identification_section())
        
        # Section Subordination (same as Zone)
        try:
            reg_element = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Entité de regroupement')]/following-sibling::div")
            info['entite_regroupement'] = reg_element.text.strip()
        except:
            info['entite_regroupement'] = ''
        
        # Section Coordonnées (only E-mail Compétitions)
        try:
            email_comp_element = self.driver.find_element(By.XPATH, "//label[contains(text(), 'E-mail Compétitions')]/following-sibling::div")
            info['email_competitions'] = email_comp_element.text.strip()
        except:
            info['email_competitions'] = ''
        
        # Section Adresse(s) email de notification des factures (title but no text block)
        info['notification_factures_titre_present'] = True
        info['notification_factures_bloc_texte'] = False
        
        return info

    def scrape_comite_entity(self, entity_id=38):
        """
        Scrape all required data for a Comité entity as per the detailed spec.
        Returns a dictionary with all extracted data.
        """
        print(f"Scraping Comité entity (ID: {entity_id})...")
        data = {'entity_type': 'Comité', 'entity_id': entity_id}
        
        # 1. Go to the main informations page
        self.driver.get(f"https://metier.ffbridge.fr/#/entites/{entity_id}/informations")
        time.sleep(2)
        
        # --- Tab INFORMATIONS PRINCIPALES ---
        data.update(self.scrape_comite_informations_principales())
        
        # --- Tab ACTEURS ---
        data['acteurs'] = self.scrape_acteurs_tab()
        
        # --- Tab RÔLES ---
        data['roles'] = self.scrape_roles_tab()
        
        # --- Tab TOURNOIS ---
        data['tournois'] = self.scrape_comite_tournois_tab()
        
        # --- Tab FACTURATION ---
        data['facturation'] = self.scrape_comite_facturation_tab()
        
        # --- Tab TABLEAU DE BORD ---
        data['tableau_de_bord'] = self.scrape_tableau_de_bord_tab()
        
        # --- Tab CLUBS ACTIFS INACTIFS ---
        data['clubs_actifs_inactifs'] = self.scrape_clubs_actifs_inactifs_tab()
        
        return data

    def scrape_comite_informations_principales(self):
        """
        Scrape the 'Informations principales' tab for Comité entities.
        Returns a dictionary with all required fields.
        """
        info = {}
        
        # Section Identification (same as FFB)
        info.update(self.scrape_identification_section())
        
        # Section Subordination (same as Zone, but with multiple Entités de regroupement)
        try:
            reg_elements = self.driver.find_elements(By.XPATH, "//label[contains(text(), 'Entité de regroupement')]/following-sibling::div")
            info['entites_regroupement'] = [elem.text.strip() for elem in reg_elements]
        except:
            info['entites_regroupement'] = []
        
        # Section Coordonnées (same as FFB)
        info.update(self.scrape_coordonnees_section())
        
        # Section Adresse(s) email de notification des factures
        info.update(self.scrape_notification_factures_section())
        
        # Section Infos complémentaires (3 checkboxes + 6 empty text blocks)
        info.update(self.scrape_comite_infos_complementaires())
        
        # Section Photo de l'entité
        info.update(self.scrape_comite_photo_entite())
        
        # Section Adresse (same as FFB)
        info.update(self.scrape_adresse_section())
        
        return info

    def scrape_comite_infos_complementaires(self):
        """Scrape the Infos complémentaires section for Comité"""
        section = {}
        
        # 3 checkboxes
        for i in range(1, 4):
            try:
                checkbox = self.driver.find_element(By.XPATH, f"//div[contains(@class, 'infos-complementaires')]//input[@type='checkbox'][{i}]")
                section[f'info_checkbox_{i}'] = checkbox.is_selected()
            except:
                section[f'info_checkbox_{i}'] = False
        
        # 6 empty text blocks
        for i in range(1, 7):
            section[f'info_texte_{i}'] = ''
            
        return section

    def scrape_comite_photo_entite(self):
        """Scrape the Photo de l'entité section for Comité"""
        section = {}
        
        try:
            # Texte
            texte_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'photo-entite')]//div[contains(@class, 'texte')]")
            section['photo_texte'] = texte_element.text.strip()
        except:
            section['photo_texte'] = ''
        
        # Bloc photo but empty
        section['photo_url'] = ''
        
        try:
            # Consigne à côté, en bas à droite de l'image
            consigne_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'photo-entite')]//div[contains(@class, 'consigne')]")
            section['photo_consigne'] = consigne_element.text.strip()
        except:
            section['photo_consigne'] = ''
            
        return section

    def scrape_roles_tab(self):
        """Scrape the RÔLES tab (list with headers, without Actions column)"""
        roles = []
        
        try:
            # Click on RÔLES tab
            roles_tab = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Rôles')]")
            roles_tab.click()
            time.sleep(2)
            
            # Find the table
            table = self.driver.find_element(By.XPATH, "//table[contains(@class, 'roles-table')]")
            rows = table.find_elements(By.TAG_NAME, 'tr')
            
            # Get headers (excluding Actions column)
            headers = []
            header_cells = rows[0].find_elements(By.TAG_NAME, 'th')
            for cell in header_cells:
                if 'Actions' not in cell.text:
                    headers.append(cell.text.strip())
            
            # Get data rows (excluding Actions column)
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, 'td')
                role_data = {}
                cell_index = 0
                for i, cell in enumerate(cells):
                    if i < len(headers):  # Skip Actions column
                        role_data[headers[i]] = cell.text.strip()
                        cell_index += 1
                roles.append(role_data)
                
        except Exception as e:
            print(f"Error scraping Rôles tab: {e}")
            
        return roles

    def scrape_comite_tournois_tab(self):
        """Scrape the TOURNOIS tab for Comité (vertical banner with Calendrier)"""
        tournois = {}
        
        try:
            # Click on Tournois tab
            tournois_tab = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Tournois')]")
            tournois_tab.click()
            time.sleep(2)
            
            # Check Organisation (on ne peut s'inscrire ni voir qui est inscrit, on passe)
            tournois['organisation_accessible'] = False
            
            # Check Livret (Sans intérêt, c'est gérer en amont par les organisateurs)
            tournois['livret_interet'] = False
            
            # Check Calendrier (On scrap le tableau et la légende)
            try:
                calendrier_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Calendrier')]")
                calendrier_btn.click()
                time.sleep(2)
                
                # Scrape table and legend
                tournois['calendrier'] = self.scrape_calendrier_table()
                
            except Exception as e:
                print(f"Error scraping Calendrier: {e}")
                tournois['calendrier'] = {}
                
        except Exception as e:
            print(f"Error scraping Comité tournois tab: {e}")
            
        return tournois

    def scrape_calendrier_table(self):
        """Scrape the Calendrier table and legend"""
        calendrier = {}
        
        try:
            # Find the table
            table = self.driver.find_element(By.XPATH, "//table[contains(@class, 'calendrier-table')]")
            rows = table.find_elements(By.TAG_NAME, 'tr')
            
            # Extract table data
            table_data = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if cells:
                    row_data = [cell.text.strip() for cell in cells]
                    table_data.append(row_data)
            
            calendrier['tableau'] = table_data
            
            # Find legend
            try:
                legend_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'calendrier-legend')]")
                calendrier['legende'] = legend_element.text.strip()
            except:
                calendrier['legende'] = ''
                
        except Exception as e:
            print(f"Error scraping calendrier table: {e}")
            
        return calendrier

    def scrape_comite_facturation_tab(self):
        """Scrape the FACTURATION tab for Comité (vertical banner with multiple options)"""
        facturation = {}
        
        try:
            # Click on Facturation tab
            facturation_tab = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Facturation')]")
            facturation_tab.click()
            time.sleep(2)
            
            # Barèmes
            facturation['baremes'] = self.scrape_baremes_section()
            
            # Montants FFB
            facturation['montants_ffb'] = self.scrape_montants_ffb_section()
            
            # 5 séance Découverte
            facturation['seance_decouverte'] = self.scrape_seance_decouverte_section()
            
        except Exception as e:
            print(f"Error scraping Comité facturation tab: {e}")
            
        return facturation

    def scrape_baremes_section(self):
        """Scrape the Barèmes section"""
        baremes = {}
        
        try:
            # AFFILIATION DU CLUB
            try:
                part_ffb_element = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Part FFB')]/following-sibling::td")
                baremes['part_ffb'] = part_ffb_element.text.strip()
            except:
                baremes['part_ffb'] = ''
                
            try:
                part_comite_element = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Part comité')]/following-sibling::td")
                baremes['part_comite'] = part_comite_element.text.strip()
            except:
                baremes['part_comite'] = ''
                
            try:
                total_element = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Total')]/following-sibling::td")
                baremes['total'] = total_element.text.strip()
            except:
                baremes['total'] = ''
            
            # PRIX DES LICENCES (list with headers, without Action column)
            baremes['prix_licences'] = self.scrape_prix_licences_table()
            
        except Exception as e:
            print(f"Error scraping Barèmes section: {e}")
            
        return baremes

    def scrape_prix_licences_table(self):
        """Scrape the PRIX DES LICENCES table"""
        prix_licences = []
        
        try:
            # Find the table
            table = self.driver.find_element(By.XPATH, "//table[contains(@class, 'prix-licences-table')]")
            rows = table.find_elements(By.TAG_NAME, 'tr')
            
            # Get headers (excluding Action column)
            headers = []
            header_cells = rows[0].find_elements(By.TAG_NAME, 'th')
            for cell in header_cells:
                if 'Action' not in cell.text:
                    headers.append(cell.text.strip())
            
            # Get data rows (excluding Action column)
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, 'td')
                row_data = {}
                cell_index = 0
                for i, cell in enumerate(cells):
                    if i < len(headers):  # Skip Action column
                        row_data[headers[i]] = cell.text.strip()
                        cell_index += 1
                prix_licences.append(row_data)
                
        except Exception as e:
            print(f"Error scraping prix licences table: {e}")
            
        return prix_licences

    def scrape_montants_ffb_section(self):
        """Scrape the Montants FFB section"""
        montants = {}
        
        try:
            # Bloc texte TOTAL
            try:
                total_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'montants-ffb')]//div[contains(@class, 'total')]")
                montants['total'] = total_element.text.strip()
            except:
                montants['total'] = ''
            
            # SOMME DUE AU COMITÉ (list with headers, without Action column)
            montants['somme_due_comite'] = self.scrape_somme_due_comite_table()
            
        except Exception as e:
            print(f"Error scraping Montants FFB section: {e}")
            
        return montants

    def scrape_somme_due_comite_table(self):
        """Scrape the SOMME DUE AU COMITÉ table"""
        somme_due = []
        
        try:
            # Find the table
            table = self.driver.find_element(By.XPATH, "//table[contains(@class, 'somme-due-table')]")
            rows = table.find_elements(By.TAG_NAME, 'tr')
            
            # Get headers (excluding Action column)
            headers = []
            header_cells = rows[0].find_elements(By.TAG_NAME, 'th')
            for cell in header_cells:
                if 'Action' not in cell.text:
                    headers.append(cell.text.strip())
            
            # Get data rows (excluding Action column)
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, 'td')
                row_data = {}
                cell_index = 0
                for i, cell in enumerate(cells):
                    if i < len(headers):  # Skip Action column
                        row_data[headers[i]] = cell.text.strip()
                        cell_index += 1
                somme_due.append(row_data)
                
        except Exception as e:
            print(f"Error scraping somme due comité table: {e}")
            
        return somme_due

    def scrape_seance_decouverte_section(self):
        """Scrape the 5 séance Découverte section"""
        seance = {}
        
        try:
            # Titre + Liste (même vide)
            try:
                titre_element = self.driver.find_element(By.XPATH, "//h4[contains(text(), '5 séance Découverte')]")
                seance['titre'] = titre_element.text.strip()
            except:
                seance['titre'] = ''
            
            # Find the list/table
            try:
                table = self.driver.find_element(By.XPATH, "//table[contains(@class, 'seance-decouverte-table')]")
                rows = table.find_elements(By.TAG_NAME, 'tr')
                
                liste = []
                for row in rows[1:]:  # Skip header
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if cells:
                        row_data = [cell.text.strip() for cell in cells]
                        liste.append(row_data)
                
                seance['liste'] = liste
            except:
                seance['liste'] = []
                
        except Exception as e:
            print(f"Error scraping séance découverte section: {e}")
            
        return seance

    def scrape_clubs_actifs_inactifs_tab(self):
        """Scrape the CLUBS ACTIFS INACTIFS tab"""
        clubs = {}
        
        try:
            # Click on CLUBS ACTIFS INACTIFS tab
            clubs_tab = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Clubs actifs inactifs')]")
            clubs_tab.click()
            time.sleep(2)
            
            # Titre + Liste (même vide), Dernière colonne : RadioButton Actif / Inactif
            try:
                titre_element = self.driver.find_element(By.XPATH, "//h3[contains(text(), 'Clubs')]")
                clubs['titre'] = titre_element.text.strip()
            except:
                clubs['titre'] = ''
            
            # Find the table
            try:
                table = self.driver.find_element(By.XPATH, "//table[contains(@class, 'clubs-table')]")
                rows = table.find_elements(By.TAG_NAME, 'tr')
                
                clubs_list = []
                for row in rows[1:]:  # Skip header
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if cells:
                        club_data = {}
                        for i, cell in enumerate(cells[:-1]):  # Exclude last column (RadioButton)
                            club_data[f'col_{i+1}'] = cell.text.strip()
                        
                        # Check RadioButton status in last column
                        try:
                            radio_actif = cells[-1].find_element(By.XPATH, ".//input[@type='radio' and @value='actif']")
                            club_data['statut'] = 'Actif' if radio_actif.is_selected() else 'Inactif'
                        except:
                            club_data['statut'] = 'Inconnu'
                        
                        clubs_list.append(club_data)
                
                clubs['liste'] = clubs_list
            except:
                clubs['liste'] = []
                
        except Exception as e:
            print(f"Error scraping clubs actifs inactifs tab: {e}")
            
        return clubs

    def scrape_club_entity(self, entity_id=850):
        """
        Scrape all required data for a Club entity as per the detailed spec.
        Returns a dictionary with all extracted data.
        """
        print(f"Scraping Club entity (ID: {entity_id})...")
        data = {'entity_type': 'Club', 'entity_id': entity_id}
        
        # 1. Go to the main informations page
        self.driver.get(f"https://metier.ffbridge.fr/#/entites/{entity_id}/informations")
        time.sleep(2)
        
        # --- Tab INFORMATIONS PRINCIPALES ---
        data.update(self.scrape_club_informations_principales())
        
        # --- Tab ACTEURS ---
        data['acteurs'] = self.scrape_acteurs_tab()
        
        # --- Tab RÔLES ---
        data['roles'] = self.scrape_roles_tab()
        
        # --- Tab TOURNOIS ---
        data['tournois'] = self.scrape_comite_tournois_tab()  # Same as Comité
        
        # --- Tab COURS ---
        data['cours'] = self.scrape_cours_tab()
        
        # --- Tab FACTURATION ---
        data['facturation'] = self.scrape_club_facturation_tab()
        
        return data

    def scrape_club_informations_principales(self):
        """
        Scrape the 'Informations principales' tab for Club entities.
        Returns a dictionary with all required fields.
        """
        info = {}
        
        # Section Identification (same as FFB)
        info.update(self.scrape_identification_section())
        
        # Section Subordination (1 seul bloc de texte vide)
        info['subordination'] = ''
        
        # Section Coordonnées (same as Comité, without E-mail Compétitions)
        coordonnees = self.scrape_coordonnees_section()
        if 'email_competitions' in coordonnees:
            del coordonnees['email_competitions']
        info.update(coordonnees)
        
        # Section Adresse(s) email de notification des factures (same as Comité)
        info.update(self.scrape_notification_factures_section())
        
        # Section Infos complémentaires (same as Comité + "5 séances Découverte")
        info.update(self.scrape_club_infos_complementaires())
        
        # Section Photo de l'entité (same as Comité but with photo)
        info.update(self.scrape_club_photo_entite())
        
        # Section Écoles de bridge + Logo
        info.update(self.scrape_ecoles_bridge_section())
        
        # Section Liste des enseignants actifs
        info.update(self.scrape_enseignants_actifs_section())
        
        # Section Adresse (same as Comité)
        info.update(self.scrape_adresse_section())
        
        return info

    def scrape_club_infos_complementaires(self):
        """Scrape the Infos complémentaires section for Club"""
        section = {}
        
        # "Votre club participe aux opérations '5 séances Découverte'" + RadioButton
        try:
            radio_element = self.driver.find_element(By.XPATH, "//input[@type='radio' and contains(@name, 'seances-decouverte')]")
            section['participe_seances_decouverte'] = radio_element.is_selected()
        except:
            section['participe_seances_decouverte'] = False
        
        # 3 checkboxes
        for i in range(1, 4):
            try:
                checkbox = self.driver.find_element(By.XPATH, f"//div[contains(@class, 'infos-complementaires')]//input[@type='checkbox'][{i}]")
                section[f'info_checkbox_{i}'] = checkbox.is_selected()
            except:
                section[f'info_checkbox_{i}'] = False
        
        # 6 empty text blocks
        for i in range(1, 7):
            section[f'info_texte_{i}'] = ''
            
        return section

    def scrape_club_photo_entite(self):
        """Scrape the Photo de l'entité section for Club (with photo)"""
        section = {}
        
        try:
            # Texte
            texte_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'photo-entite')]//div[contains(@class, 'texte')]")
            section['photo_texte'] = texte_element.text.strip()
        except:
            section['photo_texte'] = ''
        
        # Bloc photo renseigné
        try:
            img_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'photo-entite')]//img")
            section['photo_url'] = img_element.get_attribute('src')
        except:
            section['photo_url'] = ''
        
        try:
            # Consigne à côté, en bas à droite de l'image
            consigne_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'photo-entite')]//div[contains(@class, 'consigne')]")
            section['photo_consigne'] = consigne_element.text.strip()
        except:
            section['photo_consigne'] = ''
            
        return section

    def scrape_ecoles_bridge_section(self):
        """Scrape the Écoles de bridge + Logo section"""
        section = {}
        
        try:
            # Texte
            texte_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ecoles-bridge')]//div[contains(@class, 'texte')]")
            section['ecoles_texte'] = texte_element.text.strip()
        except:
            section['ecoles_texte'] = ''
        
        # Logo
        try:
            logo_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ecoles-bridge')]//img")
            section['ecoles_logo_url'] = logo_element.get_attribute('src')
        except:
            section['ecoles_logo_url'] = ''
            
        return section

    def scrape_enseignants_actifs_section(self):
        """Scrape the Liste des enseignants actifs section"""
        section = {}
        
        try:
            # En-tête + Liste
            titre_element = self.driver.find_element(By.XPATH, "//h4[contains(text(), 'enseignants actifs')]")
            section['enseignants_titre'] = titre_element.text.strip()
        except:
            section['enseignants_titre'] = ''
        
        # Find the table
        try:
            table = self.driver.find_element(By.XPATH, "//table[contains(@class, 'enseignants-table')]")
            rows = table.find_elements(By.TAG_NAME, 'tr')
            
            enseignants = []
            for row in rows[1:]:  # Skip header
                cells = row.find_elements(By.TAG_NAME, 'td')
                if cells:
                    enseignant = {
                        'nom': cells[0].text.strip() if len(cells) > 0 else '',
                        'prenom': cells[1].text.strip() if len(cells) > 1 else '',
                        'agrement': cells[2].text.strip() if len(cells) > 2 else ''
                    }
                    enseignants.append(enseignant)
            
            section['enseignants_liste'] = enseignants
        except:
            section['enseignants_liste'] = []
            
        return section

    def scrape_cours_tab(self):
        """Scrape the COURS tab (table without last column)"""
        cours = []
        
        try:
            # Click on COURS tab
            cours_tab = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Cours')]")
            cours_tab.click()
            time.sleep(2)
            
            # Find the table
            table = self.driver.find_element(By.XPATH, "//table[contains(@class, 'cours-table')]")
            rows = table.find_elements(By.TAG_NAME, 'tr')
            
            # Get headers (excluding last column)
            headers = []
            header_cells = rows[0].find_elements(By.TAG_NAME, 'th')
            for i, cell in enumerate(header_cells[:-1]):  # Exclude last column
                headers.append(cell.text.strip())
            
            # Get data rows (excluding last column)
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, 'td')
                cours_data = {}
                for i, cell in enumerate(cells[:-1]):  # Exclude last column
                    if i < len(headers):
                        cours_data[headers[i]] = cell.text.strip()
                cours.append(cours_data)
                
        except Exception as e:
            print(f"Error scraping Cours tab: {e}")
            
        return cours

    def scrape_club_facturation_tab(self):
        """Scrape the FACTURATION tab for Club (similar to Comité but with additional sections)"""
        facturation = {}
        
        try:
            # Click on Facturation tab
            facturation_tab = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Facturation')]")
            facturation_tab.click()
            time.sleep(2)
            
            # Barèmes (same as Comité but different amounts)
            facturation['baremes'] = self.scrape_club_baremes_section()
            
            # Montants Comité/FFB (additional section for Club)
            facturation['montants_comite_ffb'] = self.scrape_montants_comite_ffb_section()
            
            # 5 séance Découverte (if present)
            facturation['seance_decouverte'] = self.scrape_seance_decouverte_section()
            
        except Exception as e:
            print(f"Error scraping Club facturation tab: {e}")
            
        return facturation

    def scrape_club_baremes_section(self):
        """Scrape the Barèmes section for Club (different amounts)"""
        baremes = {}
        
        try:
            # AFFILIATION DU CLUB (different amounts: 57,50€, 10€, 67,50€)
            try:
                part_ffb_element = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Part FFB')]/following-sibling::td")
                baremes['part_ffb'] = part_ffb_element.text.strip()
            except:
                baremes['part_ffb'] = ''
                
            try:
                part_comite_element = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Part comité')]/following-sibling::td")
                baremes['part_comite'] = part_comite_element.text.strip()
            except:
                baremes['part_comite'] = ''
                
            try:
                total_element = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Total')]/following-sibling::td")
                baremes['total'] = total_element.text.strip()
            except:
                baremes['total'] = ''
            
            # PRIX DES LICENCES (same as Comité)
            baremes['prix_licences'] = self.scrape_prix_licences_table()
            
        except Exception as e:
            print(f"Error scraping Club Barèmes section: {e}")
            
        return baremes

    def scrape_montants_comite_ffb_section(self):
        """Scrape the Montants Comité/FFB section (additional for Club)"""
        montants = {}
        
        try:
            # Titre + Tableau + Warning sous le tableau
            try:
                titre_element = self.driver.find_element(By.XPATH, "//h4[contains(text(), 'Montants Comité/FFB')]")
                montants['titre'] = titre_element.text.strip()
            except:
                montants['titre'] = ''
            
            # Find the table
            try:
                table = self.driver.find_element(By.XPATH, "//table[contains(@class, 'montants-comite-ffb-table')]")
                rows = table.find_elements(By.TAG_NAME, 'tr')
                
                table_data = []
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if cells:
                        row_data = [cell.text.strip() for cell in cells]
                        table_data.append(row_data)
                
                montants['tableau'] = table_data
            except:
                montants['tableau'] = []
            
            # Warning sous le tableau
            try:
                warning_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'warning')]")
                montants['warning'] = warning_element.text.strip()
            except:
                montants['warning'] = ''
            
            # TRANSFERTS DE LICENCES
            montants['transfers_licences'] = self.scrape_transfers_licences_table()
            
            # SOMME DUE AU COMITÉ (same as Comité)
            montants['somme_due_comite'] = self.scrape_somme_due_comite_table()
            
        except Exception as e:
            print(f"Error scraping Montants Comité/FFB section: {e}")
            
        return montants

    def scrape_transfers_licences_table(self):
        """Scrape the TRANSFERTS DE LICENCES table"""
        transfers = []
        
        try:
            # Find the table
            table = self.driver.find_element(By.XPATH, "//table[contains(@class, 'transfers-licences-table')]")
            rows = table.find_elements(By.TAG_NAME, 'tr')
            
            # Get headers
            headers = []
            header_cells = rows[0].find_elements(By.TAG_NAME, 'th')
            for cell in header_cells:
                headers.append(cell.text.strip())
            
            # Get data rows
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, 'td')
                transfer_data = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        transfer_data[headers[i]] = cell.text.strip()
                transfers.append(transfer_data)
                
        except Exception as e:
            print(f"Error scraping transfers licences table: {e}")
            
                return transfers

    def scrape_entity_by_type(self, entity_id, entity_type=None):
        """
        Main function to scrape an entity based on its type.
        Automatically detects entity type from breadcrumb if not provided.
        """
        print(f"Starting to scrape entity ID: {entity_id}")
        
        # First, navigate to the entity to detect its type
        self.driver.get(f"https://metier.ffbridge.fr/#/entites/{entity_id}/informations")
        time.sleep(2)
        
        # Detect entity type from breadcrumb if not provided
        if not entity_type:
            try:
                breadcrumb = self.driver.find_element(By.CSS_SELECTOR, ".breadcrumb")
                breadcrumb_text = breadcrumb.text.lower()
                
                if "ffb" in breadcrumb_text:
                    entity_type = "FFB"
                elif "zone" in breadcrumb_text:
                    entity_type = "Zone"
                elif "ligue" in breadcrumb_text:
                    entity_type = "Ligue"
                elif "comité" in breadcrumb_text or "comite" in breadcrumb_text:
                    entity_type = "Comité"
                elif "club" in breadcrumb_text:
                    entity_type = "Club"
                else:
                    entity_type = "Unknown"
                    
                print(f"Detected entity type: {entity_type}")
            except Exception as e:
                print(f"Error detecting entity type: {e}")
                entity_type = "Unknown"
        
        # Scrape based on entity type
        if entity_type == "FFB":
            return self.scrape_ffb_entity(entity_id)
        elif entity_type == "Zone":
            return self.scrape_zone_entity(entity_id)
        elif entity_type == "Ligue":
            return self.scrape_ligue_entity(entity_id)
        elif entity_type == "Comité":
            return self.scrape_comite_entity(entity_id)
        elif entity_type == "Club":
            return self.scrape_club_entity(entity_id)
        else:
            print(f"Unknown entity type: {entity_type}")
            return {}

    def scrape_all_entities(self, start_id=1, end_id=5000):
        """
        Scrape all entities from start_id to end_id.
        Saves progress frequently and can resume from interruptions.
        """
        output_dir = self.get_output_dir()
        progress_file = os.path.join(output_dir, 'scraping_progress.json')
        
        # Load progress if exists
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                progress = json.load(f)
            last_processed = progress.get('last_processed_id', start_id - 1)
            print(f"Resuming from entity ID: {last_processed + 1}")
        else:
            last_processed = start_id - 1
            progress = {'last_processed_id': last_processed, 'entities': {}}
        
        entities_data = []
        
        for entity_id in range(last_processed + 1, end_id + 1):
            try:
                print(f"\n--- Processing Entity ID: {entity_id} ---")
                
                # Scrape the entity
                entity_data = self.scrape_entity_by_type(entity_id)
                
                if entity_data:
                    entities_data.append(entity_data)
                    
                    # Save progress after each entity
                    progress['last_processed_id'] = entity_id
                    progress['entities'][str(entity_id)] = entity_data
                    
                    with open(progress_file, 'w') as f:
                        json.dump(progress, f, indent=2, ensure_ascii=False)
                    
                    print(f"✓ Entity {entity_id} processed and saved")
                else:
                    print(f"✗ No data found for entity {entity_id}")
                
                # Small delay between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"✗ Error processing entity {entity_id}: {e}")
                # Save progress even on error
                progress['last_processed_id'] = entity_id
                with open(progress_file, 'w') as f:
                    json.dump(progress, f, indent=2, ensure_ascii=False)
                continue
        
        # Save final results
        entities_file = os.path.join(output_dir, 'entities_data.json')
        with open(entities_file, 'w') as f:
            json.dump(entities_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== Scraping completed ===")
        print(f"Total entities processed: {len(entities_data)}")
        print(f"Results saved to: {entities_file}")
        print(f"Progress saved to: {progress_file}")
        
        return entities_data
     
     def close(self):
         self.driver.quit()

def main():
    scraper = FFBScraper()
    try:
        print("=== FFB Database Scraper ===")
        print("Starting login process...")
        scraper.login()
        
        print("\n=== Entity Scraping Options ===")
        print("1. Scrape specific entity by ID")
        print("2. Scrape all entities (1-5000)")
        print("3. Scrape FFB entity (ID: 1)")
        print("4. Scrape Zone entity (ID: 2)")
        print("5. Scrape Ligue entity (ID: 18)")
        print("6. Scrape Comité entity (ID: 38)")
        print("7. Scrape Club entity (ID: 850)")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            entity_id = int(input("Enter entity ID: "))
            entity_type = input("Enter entity type (optional, will auto-detect if empty): ").strip()
            if not entity_type:
                entity_type = None
            
            print(f"\nScraping entity ID: {entity_id}")
            entity_data = scraper.scrape_entity_by_type(entity_id, entity_type)
            
            if entity_data:
                output_dir = scraper.get_output_dir()
                entity_file = os.path.join(output_dir, f'entity_{entity_id}.json')
                with open(entity_file, 'w') as f:
                    json.dump(entity_data, f, indent=2, ensure_ascii=False)
                print(f"✓ Entity data saved to: {entity_file}")
            else:
                print("✗ No data found for this entity")
                
        elif choice == "2":
            start_id = int(input("Enter start ID (default: 1): ") or "1")
            end_id = int(input("Enter end ID (default: 5000): ") or "5000")
            
            print(f"\nStarting batch scraping from ID {start_id} to {end_id}")
            entities_data = scraper.scrape_all_entities(start_id, end_id)
            
        elif choice == "3":
            print("\nScraping FFB entity (ID: 1)")
            entity_data = scraper.scrape_ffb_entity(1)
            if entity_data:
                output_dir = scraper.get_output_dir()
                entity_file = os.path.join(output_dir, 'ffb_entity.json')
                with open(entity_file, 'w') as f:
                    json.dump(entity_data, f, indent=2, ensure_ascii=False)
                print(f"✓ FFB entity data saved to: {entity_file}")
                
        elif choice == "4":
            print("\nScraping Zone entity (ID: 2)")
            entity_data = scraper.scrape_zone_entity(2)
            if entity_data:
                output_dir = scraper.get_output_dir()
                entity_file = os.path.join(output_dir, 'zone_entity.json')
                with open(entity_file, 'w') as f:
                    json.dump(entity_data, f, indent=2, ensure_ascii=False)
                print(f"✓ Zone entity data saved to: {entity_file}")
                
        elif choice == "5":
            print("\nScraping Ligue entity (ID: 18)")
            entity_data = scraper.scrape_ligue_entity(18)
            if entity_data:
                output_dir = scraper.get_output_dir()
                entity_file = os.path.join(output_dir, 'ligue_entity.json')
                with open(entity_file, 'w') as f:
                    json.dump(entity_data, f, indent=2, ensure_ascii=False)
                print(f"✓ Ligue entity data saved to: {entity_file}")
                
        elif choice == "6":
            print("\nScraping Comité entity (ID: 38)")
            entity_data = scraper.scrape_comite_entity(38)
            if entity_data:
                output_dir = scraper.get_output_dir()
                entity_file = os.path.join(output_dir, 'comite_entity.json')
                with open(entity_file, 'w') as f:
                    json.dump(entity_data, f, indent=2, ensure_ascii=False)
                print(f"✓ Comité entity data saved to: {entity_file}")
                
        elif choice == "7":
            print("\nScraping Club entity (ID: 850)")
            entity_data = scraper.scrape_club_entity(850)
            if entity_data:
                output_dir = scraper.get_output_dir()
                entity_file = os.path.join(output_dir, 'club_entity.json')
                with open(entity_file, 'w') as f:
                    json.dump(entity_data, f, indent=2, ensure_ascii=False)
                print(f"✓ Club entity data saved to: {entity_file}")
                
        else:
            print("Invalid choice. Exiting.")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
