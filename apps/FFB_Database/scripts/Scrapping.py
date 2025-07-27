import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Replace with your login credentials and the website URLs
LOGIN_URL = 'https://www.ffbridge.fr/auth/login'
TARGET_URL = 'https://formation.ffbridge.fr/formation/7'
USERNAME = '3144342'
PASSWORD = '7SaX=0324'

def login_and_scrape():
    # Start a session to persist cookies and headers across requests
    session = requests.Session()
    
    # Step 1: Log in to the site
    login_payload = {
        'username': USERNAME,  # Adjust field names as per website form
        'password': PASSWORD,
    }
    
    # Perform login request
    login_response = session.post(LOGIN_URL, data=login_payload)
    
    # Check if login was successful
    if login_response.status_code == 200 and "Logout" in login_response.text:
        print("Logged in successfully.")
    else:
        print("Failed to log in.")
        return
    
    # Step 2: Access the target page after logging in
    response = session.get(TARGET_URL)
    
    # Check for successful page retrieval
    if response.status_code != 200:
        print("Failed to retrieve the target page.")
        return

    # Parse HTML to find all document links
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Assuming documents have extensions like .pdf, .docx, .xls, etc.
    document_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith(('.pdf', '.docx', '.xls', '.xlsx', '.ppt', '.pptx')):
            # Resolve relative URLs
            full_url = urljoin(TARGET_URL, href)
            document_links.append(full_url)
    
    # Display all found document links
    print("Document links found:")
    for doc_link in document_links:
        print(doc_link)
        
    return document_links

# Call the function
# login_and_scrape()