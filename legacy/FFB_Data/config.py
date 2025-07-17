import os
from dotenv import load_dotenv

load_dotenv()

# FFB Credentials
FFB_USERNAME = "3144342"
FFB_PASSWORD = "7SaX=0324"

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# URLs
LOGIN_URL = "https://www.ffbridge.fr/auth/login"
METIER_URL = "https://metier.ffbridge.fr/"

# Club IDs - Starting with 42 for Lorraine clubs
LOTTINGE_CLUB_IDS = [
    # This list will be populated during scraping
]

# Database Tables
TABLE_ENTITES = "entites"
TABLE_LICENSEES = "licensees"
TABLE_ROLES = "roles"
TABLE_LICENSEE_ROLES = "licensee_roles"
