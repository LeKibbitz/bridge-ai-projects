from tkinter import YES
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
BASE_URL = "https://metier.ffbridge.fr/#/entites"
START_ID = 1
END_ID = 5000
WAIT_BETWEEN_REQUESTS = 1  # seconds

# --- DATAFRAME INITIALIZATION ---
entities_df = pd.DataFrame()
last_working_url = None

# --- UTILITY FUNCTIONS ---
def fetch_entity_informations(entity_id: int):
    url = f"{BASE_URL}/{entity_id}/informations"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.text.strip():
            return response.text, url
        else:
            return None, url
    except Exception as e:
        print(f"Error fetching entity {entity_id}: {e}")
        return None, url

def parse_informations_page(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    # TODO: Parse all fields except 'Adresse(s) email de notification des factures'
    # For now, just return a placeholder dict
    data = {"field1": "value1", "field2": "value2"}
    return data

def fetch_entity_acteurs(entity_id: int):
    url = f"{BASE_URL}/{entity_id}/acteurs/actifs"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.text.strip():
            return response.text, url
        else:
            return None, url
    except Exception as e:
        print(f"Error fetching acteurs for entity {entity_id}: {e}")
        return None, url

def parse_acteurs_page(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    # TODO: Parse all actors/members for the entity
    # For now, just return a placeholder list
    data = [{"actor_field1": "actor_value1"}]
    return data

# --- MAIN SCRAPING LOOP ---
def main():
    global last_working_url
    for entity_id in range(START_ID, END_ID + 1):
        html, url = fetch_entity_informations(entity_id)
        if html:
            last_working_url = url
            info_data = parse_informations_page(html)
            info_data['entity_id'] = str(entity_id)
            info_data['informations_url'] = url
            # Save to DataFrame
            entities_df.loc[len(entities_df)] = info_data
            print(f"Scraped entity ID: {entity_id} (success)")
            # Scrape acteurs/actifs page
            acteurs_html, acteurs_url = fetch_entity_acteurs(entity_id)
            if acteurs_html:
                # Placeholder for parsing and saving actors
                acteurs_data = parse_acteurs_page(acteurs_html)
                # TODO: Save acteurs_data as needed
            # TODO: Handle left-side block redirections and error recovery
        else:
            print(f"Scraped entity ID: {entity_id} (fail)")
        time.sleep(WAIT_BETWEEN_REQUESTS)
    # Save all entities to CSV at the end
    entities_df.to_csv('entities.csv', sep='\t', index=False)
    print("Scraping complete. entities.csv saved.")

if __name__ == "__main__":
    main()
 