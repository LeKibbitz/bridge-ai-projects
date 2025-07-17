from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from config import FFB_USERNAME, FFB_PASSWORD, LOGIN_URL, METIER_URL
from models import Entite, Licensee, ClubMember
import time
from datetime import datetime
import json
import pandas as pd
import csv

class FFBScraper:
    def __init__(self):
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, 10)
        
    def _setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=options
        )
        return driver
    
    def login(self):
        self.driver.get(LOGIN_URL)
        
        # Wait for login form
        email_input = self.wait.until(EC.presence_of_element_located((By.ID, "tui_21752435592303")))
        password_input = self.wait.until(EC.presence_of_element_located((By.ID, "tui_31752435592305")))
        
        # Fill login form
        email_input.send_keys(FFB_USERNAME)
        password_input.send_keys(FFB_PASSWORD)
        
        # Submit form
        submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Se connecter')]")
        submit_button.click()
        
        # Wait for redirect to metier
        self.wait.until(EC.url_contains(METIER_URL))
    
    def scrape_entites(self):
        # Navigate to entites page
        self.driver.get(f"{METIER_URL}#/entites/tableau-de-bord")
        
        # Wait for entities list to load
        entities_list = self.wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "entities-list-item"))
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
