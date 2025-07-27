from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import asyncio
from playwright.async_api import async_playwright
import config
import os

# Configuration
LOGIN_URL = "https://www.ffbridge.fr/auth/login"
METIER_URL = "https://metier.ffbridge.fr/"

# Initialize WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    # Remove headless mode to see what's happening
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Use ChromeDriverManager to get the latest compatible driver
    try:
        # Try to use the system ChromeDriver first
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Error initializing ChromeDriver: {str(e)}")
        print("Attempting to install the correct version...")
        
        # Try to install the correct version
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.core.utils import ChromeType
        
        # Get the correct version of ChromeDriver for ARM64
        driver_path = ChromeDriverManager(
            version="138.0.7204.94",
            os_type="mac_arm64"
        ).install()
        
        # Create a Service object
        service = Service(driver_path)
        
        # Create the driver with the correct service
        driver = webdriver.Chrome(service=service, options=options)
    
    return driver

def handle_popups(driver):
    """Handle any popups that might appear"""
    try:
        # Try to find and accept any alert
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"Found alert: {alert.text}")
        alert.accept()
        print("Alert accepted")
    except:
        pass
    
    try:
        # Try to find and close any cookie banner
        cookie_banner = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "cookie-banner"))
        )
        accept_cookie = cookie_banner.find_element(By.XPATH, "//button[contains(text(), 'Accepter')]")
        accept_cookie.click()
        print("Cookie banner accepted")
    except:
        pass

def login(driver):
    print(f"Attempting to login to {LOGIN_URL}")
    
    driver.get(LOGIN_URL)
    
    # Wait for login form with longer timeout
    try:
        print("Waiting for username input...")
        username_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-test-id='input']"))
        )
        print("Username input found")
        
        print("Waiting for password input...")
        password_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-test-id='password']"))
        )
        print("Password input found")
        
        # Fill login form
        print("Filling login form...")
        username_input.clear()
        username_input.send_keys(os.getenv('FFB_USERNAME'))
        password_input.clear()
        password_input.send_keys(os.getenv('FFB_PASSWORD'))
        
        # Submit form with explicit wait
        print("Waiting for submit button...")
        submit_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accepter')]"))
        )
        print("Submit button found")
        submit_button.click()
        
        # Wait for redirect with longer timeout
        print("Waiting for redirect to metier...")
        WebDriverWait(driver, 30).until(
            EC.url_contains(METIER_URL)
        )
        print("Redirect successful")
        
        # Wait for page to be fully loaded
        print("Waiting for page to be fully loaded...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Page loaded successfully")
        
        return True
    except TimeoutException as te:
        print(f"Timeout occurred: {str(te)}")
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        return False

def analyze_entites(driver):
    print("Analyzing Entités page...")
    driver.get(f"{METIER_URL}#/entites/tableau-de-bord")
    
    # Wait for page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    
    # Get page structure
    page_structure = {
        "url": driver.current_url,
        "title": driver.title,
        "elements": [],
        "tables": [],
        "forms": []
    }
    
    # Analyze elements
    elements = driver.find_elements(By.TAG_NAME, "*")
    for element in elements:
        try:
            page_structure["elements"].append({
                "tag": element.tag_name,
                "text": element.text[:100],
                "attributes": element.get_attribute("outerHTML")[:500]
            })
        except:
            continue
    
    return page_structure

def analyze_licensees(driver, club_id):
    print(f"Analyzing Licensees for club {club_id}...")
    driver.get(f"{METIER_URL}#/entites/{club_id}/licencies")
    
    # Wait for page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    
    # Get page structure
    page_structure = {
        "url": driver.current_url,
        "title": driver.title,
        "elements": [],
        "tables": [],
        "forms": []
    }
    
    # Analyze elements
    elements = driver.find_elements(By.TAG_NAME, "*")
    for element in elements:
        try:
            page_structure["elements"].append({
                "tag": element.tag_name,
                "text": element.text[:100],
                "attributes": element.get_attribute("outerHTML")[:500]
            })
        except:
            continue
    
    return page_structure

def analyze_club_members(driver):
    # This function is not implemented yet
    pass

def main():
    # Initialize driver
    driver = setup_driver()
    
    try:
        # Check if we're already logged in
        driver.get(LOGIN_URL)
        current_url = driver.current_url
        
        if METIER_URL in current_url:
            print("Already logged in!")
        else:
            # Attempt login
            if not login(driver):
                print("Failed to login. Exiting...")
                driver.quit()
                return
        
        # Scrape entities
        print("Scraping entities...")
        analyze_entites(driver)
        
        # Scrape licensees
        print("Scraping licensees...")
        analyze_licensees(driver, "club_id")
        
        # Scrape club members
        print("Scraping club members...")
        analyze_club_members(driver)
        
        print("Analysis completed successfully!")
        
    except Exception as e:
        print(f"An error occurred during scraping: {str(e)}")
    finally:
        # Clean up
        driver.quit()

if __name__ == "__main__":
    main() 