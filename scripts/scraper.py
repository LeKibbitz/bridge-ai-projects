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
        # Go directly to the login page
        print("Navigating directly to login page...")
        self.driver.get(LOGIN_URL)
        time.sleep(2)
        current_url = self.driver.current_url
        print(f"Current URL after navigating to login: {current_url}")
        if "auth/login" in current_url:
            print("On login page, proceeding with login...")
            self._perform_login()
        else:
            print("Not on login page, checking if we can access metier...")
            self.driver.get("https://metier.ffbridge.fr/#/home")
            time.sleep(3)
            print(f"Metier URL: {self.driver.current_url}")
            if "auth/login" in self.driver.current_url:
                print("Metier redirected to login, proceeding with login...")
                self._perform_login()
            else:
                print("Successfully accessed metier without login!")
        # Always ensure we are in the metier environment before proceeding
        if not ("metier.ffbridge.fr" in self.driver.current_url):
            print("Not in metier environment after login attempts. Aborting scrape_entites.")
            return []
    
    def _perform_login(self):
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
        submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Se connecter')]")
        print("Submit button found, clicking...")
        submit_button.click()
        
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
    
    def scrape_entites(self):
        # We should now be in the licencie environment after clicking "Accéder"
        print("Scraping entities from licencie environment...")
        
        # Defensive: If not in metier environment, return empty list
        if not ("metier.ffbridge.fr" in self.driver.current_url):
            print("Not in metier environment. Returning empty list.")
            return []
        
        # First, let's explore what's available in the current environment
        print("Exploring current licencie environment...")
        print(f"Current URL: {self.driver.current_url}")
        print(f"Page title: {self.driver.title}")
        
        # Debug: Show page source to understand the structure
        print("Page source preview (first 1000 chars):")
        page_source = self.driver.page_source
        print(page_source[:1000])
        
        # Look for any navigation elements or links that might lead to entities
        print("Looking for navigation elements...")
        nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, .nav, .navigation, .menu, .sidebar")
        print(f"Found {len(nav_elements)} navigation elements")
        
        # Look for any links that might contain "entite", "club", or "entity"
        print("Looking for entity-related links...")
        links = self.driver.find_elements(By.TAG_NAME, "a")
        entity_links = []
        for link in links:
            href = link.get_attribute('href')
            text = link.text.lower()
            if href and ('entite' in href.lower() or 'club' in href.lower() or 'entity' in href.lower() or
                        'entite' in text or 'club' in text or 'entity' in text):
                entity_links.append((href, text))
                print(f"Found entity link: {href} - {text}")
        
        # Also look for buttons that might lead to entities
        print("Looking for entity-related buttons...")
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        entity_buttons = []
        for button in buttons:
            text = button.text.lower()
            if 'entite' in text or 'club' in text or 'entity' in text:
                entity_buttons.append(text)
                print(f"Found entity button: {text}")
        
        # Try to navigate to entities if we found any links
        if entity_links:
            print("Found entity links, trying to navigate...")
            for href, text in entity_links:
                print(f"Trying to navigate to: {href}")
                self.driver.get(href)
                time.sleep(3)
                print(f"Current URL: {self.driver.current_url}")
                print(f"Page title: {self.driver.title}")
                
                if "auth/login" not in self.driver.current_url:
                    print(f"Successfully navigated to: {href}")
                    break
            else:
                print("All entity links redirected to login")
                return []
        else:
            print("No entity links found, trying direct URLs...")
            # Try some common URLs in the licencie environment
            possible_urls = [
                "https://licencie.ffbridge.fr/#/entites",
                "https://licencie.ffbridge.fr/#/clubs", 
                "https://licencie.ffbridge.fr/#/mes-clubs",
                "https://licencie.ffbridge.fr/#/dashboard"
            ]
            
            for url in possible_urls:
                print(f"Trying URL: {url}")
                self.driver.get(url)
                time.sleep(3)
                print(f"Current URL: {self.driver.current_url}")
                print(f"Page title: {self.driver.title}")
                
                if "auth/login" not in self.driver.current_url:
                    print(f"Found working URL: {url}")
                    break
            else:
                print("No working URLs found in licencie environment")
                return []
        
        # If we're still in licencie environment and haven't found entities, 
        # let's try to access the actual metier environment
        print("Trying to access metier environment directly...")
        metier_urls = [
            "https://metier.ffbridge.fr/#/entites/tableau-de-bord",
            "https://metier.ffbridge.fr/#/entites",
            "https://metier.ffbridge.fr/#/clubs",
            "https://metier.ffbridge.fr/#/home"
        ]
        
        for url in metier_urls:
            print(f"Trying metier URL: {url}")
            self.driver.get(url)
            time.sleep(3)
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")
            
            if "auth/login" not in self.driver.current_url and "Page introuvable" not in self.driver.title:
                print(f"Found working metier URL: {url}")
                break
        else:
            print("No working metier URLs found, staying in licencie environment")
            
        # We're now in the metier environment! Let's explore it for entities data
        print("Exploring metier environment for entities data...")
        print(f"Current URL: {self.driver.current_url}")
        print(f"Page title: {self.driver.title}")
        
        # Look for any data that might be available in the metier environment
        print("Looking for available data in metier dashboard...")
        page_source = self.driver.page_source
        print("Page source preview (first 2000 chars):")
        print(page_source[:2000])
        
        # Look for any tables, lists, or data containers
        print("Looking for data containers...")
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        lists = self.driver.find_elements(By.TAG_NAME, "ul")
        cards = self.driver.find_elements(By.CSS_SELECTOR, ".card, .tile, .panel, .widget")
        
        print(f"Found {len(tables)} tables, {len(lists)} lists, {len(cards)} cards")
        
        # Look for any text that might contain club or entity information
        print("Looking for club/entity related text...")
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        if "club" in body_text.lower() or "entite" in body_text.lower() or "42" in body_text:
            print("Found potential club/entity data in page text")
            # Extract lines containing relevant information
            lines = body_text.split('\n')
            relevant_lines = [line for line in lines if any(keyword in line.lower() for keyword in ['club', 'entite', '42', 'lorraine'])]
            print("Relevant lines found:")
            for line in relevant_lines[:10]:  # Show first 10
                print(f"  - {line.strip()}")
            
            # Extract entity data, filtering out entity 4200000 (Comité de Lorraine)
            print("Extracting entity data...")
            entities = []
            for line in relevant_lines:
                line = line.strip()
                # Look for lines that match the pattern "4200XXX - Club Name"
                if line.startswith('42') and ' - ' in line:
                    parts = line.split(' - ', 1)
                    if len(parts) == 2:
                        entity_id = parts[0].strip()
                        entity_name = parts[1].strip()
                        
                        # Skip entity 4200000 (Comité de Lorraine)
                        if entity_id == '4200000':
                            print(f"Skipping entity {entity_id} - {entity_name} (regional committee)")
                            continue
                        
                        # Only include entities that start with 42 (Lorraine region)
                        if entity_id.startswith('42'):
                            entity_data = {
                                "id": int(entity_id),
                                "nom": entity_name,
                                "region": "Lorraine"
                            }
                            entities.append(entity_data)
                            print(f"Found entity: {entity_id} - {entity_name}")
            
            print(f"Total entities found (excluding 4200000): {len(entities)}")
            return entities
        else:
            print("No obvious club/entity data found in page text")
            return []
        
        # Look for any navigation or menu items that might lead to entities
        print("Looking for navigation elements...")
        nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, .nav, .navigation, .menu, .sidebar")
        print(f"Found {len(nav_elements)} navigation elements")
        
        # Look for any links that might contain "entite", "club", or "entity"
        print("Looking for entity-related links...")
        links = self.driver.find_elements(By.TAG_NAME, "a")
        entity_links = []
        for link in links:
            href = link.get_attribute('href')
            text = link.text.lower()
            if href and ('entite' in href.lower() or 'club' in href.lower() or 'entity' in href.lower() or
                        'entite' in text or 'club' in text or 'entity' in text):
                entity_links.append((href, text))
                print(f"Found entity link: {href} - {text}")
        
        # Also look for buttons that might lead to entities
        print("Looking for entity-related buttons...")
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        entity_buttons = []
        for button in buttons:
            text = button.text.lower()
            if 'entite' in text or 'club' in text or 'entity' in text:
                entity_buttons.append(text)
                print(f"Found entity button: {text}")
        
        # Try to navigate to entities if we found any links
        if entity_links:
            print("Found entity links, trying to navigate...")
            for href, text in entity_links:
                print(f"Trying to navigate to: {href}")
                self.driver.get(href)
                time.sleep(3)
                print(f"Current URL: {self.driver.current_url}")
                print(f"Page title: {self.driver.title}")
                
                if "auth/login" not in self.driver.current_url:
                    print(f"Successfully navigated to: {href}")
                    break
            else:
                print("All entity links redirected to login")
                return []
        else:
            print("No entity links found, trying direct URLs...")
            # Try some common URLs in the metier environment
            possible_urls = [
                "https://metier.ffbridge.fr/#/entites",
                "https://metier.ffbridge.fr/#/clubs", 
                "https://metier.ffbridge.fr/#/mes-clubs",
                "https://metier.ffbridge.fr/#/dashboard"
            ]
            
            for url in possible_urls:
                print(f"Trying URL: {url}")
                self.driver.get(url)
                time.sleep(3)
                print(f"Current URL: {self.driver.current_url}")
                print(f"Page title: {self.driver.title}")
                
                if "auth/login" not in self.driver.current_url:
                    print(f"Found working URL: {url}")
                    break
            else:
                print("No working URLs found in metier environment")
                return []
        
        print(f"Final URL: {self.driver.current_url}")
        print(f"Final title: {self.driver.title}")
        
        # Debug: Show page source to understand the structure
        print("Page source preview (first 500 chars):")
        page_source = self.driver.page_source
        print(page_source[:500])
        
        # Debug: List all elements with class containing "entity"
        print("Looking for entity elements...")
        entity_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='entity']")
        print(f"Found {len(entity_elements)} elements with 'entity' in class name:")
        for i, elem in enumerate(entity_elements[:5]):  # Show first 5
            print(f"  {i}: class='{elem.get_attribute('class')}', text='{elem.text[:50]}...'")
        
        # Also try looking for any list items or table rows
        print("Looking for list items and table rows...")
        list_items = self.driver.find_elements(By.TAG_NAME, "li")
        table_rows = self.driver.find_elements(By.TAG_NAME, "tr")
        print(f"Found {len(list_items)} list items and {len(table_rows)} table rows")
        
        # Look for any div elements that might contain content
        print("Looking for div elements...")
        divs = self.driver.find_elements(By.TAG_NAME, "div")
        print(f"Found {len(divs)} div elements")
        for i, div in enumerate(divs[:10]):  # Show first 10
            class_attr = div.get_attribute('class')
            text_content = div.text.strip()
            if text_content:
                print(f"  {i}: class='{class_attr}', text='{text_content[:100]}...'")
        
        # Wait for entities list to load (try multiple possible selectors)
        print("Waiting for entities list...")
        try:
            entities_list = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "entities-list-item"))
            )
        except TimeoutException:
            print("entities-list-item not found, trying alternative selectors...")
            # Try alternative selectors
            entities_list = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".entity, [class*='entity'], .club, [class*='club']"))
            )
        
        entites = []
        for entity in entities_list:
            if entity.text.startswith("42"):  # Only keep Lorraine clubs
                entite_data = {
                    "id": int(entity.get_attribute("id")),
                    "nom": entity.find_element(By.CLASS_NAME, "entity-name").text,
                    "region": "Lorraine"
                }
                entites.append(Entite(**entite_data))
        
        # At the end of scrape_entites, always return a list
        if 'entites' in locals():
            return entites
        else:
            return []
    
    def scrape_licensees(self, club_id):
        # Scrape both current and renewal members
        members = []
        
        # Scrape current members
        self.driver.get(f"{METIER_URL}#/entites/{club_id}/membres/consultation")
        members.extend(self._scrape_members_list())
        
        # Scrape renewal members
        self.driver.get(f"{METIER_URL}#/entites/{club_id}/membres/renouvellement")
        members.extend(self._scrape_members_list())
        
        return members
    
    def _scrape_members_list(self):
        # Wait for members table
        members_table = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "members-table"))
        )
        
        members = []
        rows = members_table.find_elements(By.TAG_NAME, "tr")
        
        for row in rows[1:]:  # Skip header
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 0:
                member_data = {
                    "nom": cells[0].text,
                    "prenom": cells[1].text,
                    "numero_licence": cells[2].text,
                    "statut": cells[3].text
                }
                members.append(member_data)
        
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
            clubs_df.to_csv(clubs_file, index=False)
            print(f"Saved {len(clubs_df)} clubs to {clubs_file}")
            
            print("Scraping members...")
            all_members = []
            for entite in entites:
                try:
                    members = scraper.scrape_licensees(entite['id'])
                    print(f"Found {len(members)} members for club {entite['nom']}")
                    for member in members:
                        member['club_id'] = entite['id']
                        all_members.append(member)
                except Exception as e:
                    print(f"Error scraping members for club {entite['nom']}: {e}")
                    continue
            
            # Convert members to DataFrame and save
            if all_members:
                players_df = pd.DataFrame(all_members)
                players_file = os.path.join(output_dir, 'players.csv')
                players_df.to_csv(players_file, index=False)
                print(f"Saved {len(players_df)} players to {players_file}")
            else:
                print("No members found")
        else:
            print("No entities found")
            # Create empty CSV files
            empty_clubs_df = pd.DataFrame(columns=['id', 'nom', 'region'])
            clubs_file = os.path.join(output_dir, 'clubs.csv')
            empty_clubs_df.to_csv(clubs_file, index=False)
            empty_players_df = pd.DataFrame(columns=['nom', 'prenom', 'numero_licence', 'statut', 'club_id'])
            players_file = os.path.join(output_dir, 'players.csv')
            empty_players_df.to_csv(players_file, index=False)
            print(f"Created empty CSV files in {output_dir}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
