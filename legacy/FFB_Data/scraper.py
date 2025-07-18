from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from config import FFB_USERNAME, FFB_PASSWORD, LOGIN_URL, METIER_URL
from models import Entite, Licensee
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
        # Start from the main FFB website
        print("Starting from main FFB website...")
        self.driver.get("https://www.ffbridge.fr/")
        
        # Wait for the site to load (it's slow)
        print("Waiting for site to load...")
        time.sleep(5)
        
        # Check if we got redirected to login
        current_url = self.driver.current_url
        print(f"Current URL after loading: {current_url}")
        
        if "auth/login" in current_url:
            print("Redirected to login page, proceeding with login...")
            # We're on the login page, proceed with login
            self._perform_login()
        else:
            print("Not redirected to login, checking if we can access metier...")
            # Try to go to metier URL
            self.driver.get("https://metier.ffbridge.fr/#/home")
            time.sleep(3)
            print(f"Metier URL: {self.driver.current_url}")
            
            # Check if we got redirected to login from metier
            if "auth/login" in self.driver.current_url:
                print("Metier redirected to login, proceeding with login...")
                self._perform_login()
            else:
                print("Successfully accessed metier without login!")
                return
    
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
        
        # Check if there are any error messages
        try:
            error_elements = self.driver.find_elements(By.CLASS_NAME, "error")
            if error_elements:
                print("Error messages found:")
                for error in error_elements:
                    print(f"  - {error.text}")
        except:
            pass
        
        # Wait for redirect to dashboard (login now redirects to user dashboard)
        print("Waiting for redirect to dashboard...")
        self.wait.until(EC.url_contains("ffbridge.fr/user/dashboard"))
        print("Successfully logged in!")
        
        # Now navigate to the metier URL
        print("Navigating to metier URL...")
        self.driver.get("https://metier.ffbridge.fr/#/home")
        print("Navigated to metier URL")
    
    def scrape_entites(self):
        # Try to find entities data on the main domain after successful login
        print("Looking for entities data on main domain...")
        
        # Try different possible URLs on the main domain
        possible_urls = [
            "https://www.ffbridge.fr/user/dashboard",
            "https://www.ffbridge.fr/user/clubs",
            "https://www.ffbridge.fr/user/entites", 
            "https://www.ffbridge.fr/user/entities",
            "https://www.ffbridge.fr/clubs",
            "https://www.ffbridge.fr/entites",
            "https://www.ffbridge.fr/entities"
        ]
        
        for url in possible_urls:
            print(f"Trying URL: {url}")
            self.driver.get(url)
            time.sleep(3)
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")
            
            # Check if we got redirected to login (which means URL doesn't exist or requires auth)
            if "auth/login" in self.driver.current_url:
                print(f"URL {url} redirected to login, trying next...")
                continue
            
            # Check if we got a 404 page
            if "Page introuvable" in self.driver.title or "Page introuvable" in self.driver.page_source:
                print(f"URL {url} shows 404, trying next...")
                continue
            
            # If we reach here, we found a working URL
            print(f"Found working URL: {url}")
            break
        else:
            print("No working entities URL found, staying on dashboard...")
            self.driver.get("https://www.ffbridge.fr/user/dashboard")
            time.sleep(3)
        
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
        
        return entites
    
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
        scraper.login()
        print("Scraping entities...")
        entites = scraper.scrape_entites()
        # Convert Entite objects to dicts for DataFrame
        clubs_data = [e.dict() for e in entites]
        clubs_df = pd.DataFrame(clubs_data)
        clubs_df.to_csv('clubs.csv', index=False)
        print(f"Saved {len(clubs_df)} clubs to clubs.csv")
        print("Scraping members...")
        all_members = []
        for entite in entites:
            members = scraper.scrape_licensees(entite.id)
            print(f"Found {len(members)} members for club {entite.nom}")
            for member in members:
                member['club_id'] = entite.id
                all_members.append(member)
        # Convert members to DataFrame and save
        players_df = pd.DataFrame(all_members)
        players_df.to_csv('players.csv', index=False)
        print(f"Saved {len(players_df)} players to players.csv")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
