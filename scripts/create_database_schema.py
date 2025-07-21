#!/usr/bin/env python3
"""
FFB Database Schema Generator
============================

This script analyzes the structure of FFB entities and generates a complete database schema.
It scrapes entities 1, 2, 18, 38, 850 (representing each entity type) and builds the schema
progressively as new data structures are discovered.

Key points:
- entity_code is the primary key for entities
- license_number is the primary key for members
- Includes created_at, updated_at, created_by, updated_by, soft_deleted fields
- Generates relationships, indexes, and constraints
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Set, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from config import FFB_USERNAME, FFB_PASSWORD
import re
from unidecode import unidecode

def to_snake_case(name):
    """Convert a string to snake_case."""
    name = unidecode(name)  # Transliterate unicode characters
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name).strip() # Remove special characters
    name = re.sub(r'\s+', '_', name) # Replace spaces with underscores
    return name.lower()

class DatabaseSchemaGenerator:
    def __init__(self):
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, 10)
        self.schema = {
            'tables': {
                'entities': {
                    'fields': [],
                    'primary_key': 'entity_code',
                    'foreign_keys': [],
                    'indexes': []
                }
            },
            'relationships': [],
            'enums': {},
            'indexes': [],
            'triggers': []
        }
        self.discovered_fields = set()
        
    def _setup_driver(self):
        """Setup Chrome driver for scraping"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver_path = "/Users/lekibbitz/chromedriver_arm64"
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    
    def login(self):
        """Login to FFB system"""
        print("Logging in to FFB system...")
        self.driver.get("https://www.ffbridge.fr/auth/login")
        time.sleep(3)
        
        if "auth/login" in self.driver.current_url:
            self._perform_login()
        else:
            self.driver.get("https://metier.ffbridge.fr/#/home")
            time.sleep(3)
            if "auth/login" in self.driver.current_url:
                self._perform_login()
    
    def _perform_login(self):
        """Perform the actual login"""
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
            import traceback
            traceback.print_exc()
            return
    
    def analyze_entity_structure(self, entity_id: int, entity_type: str):
        """Analyze the structure of a specific entity"""
        print(f"\n--- Analyzing {entity_type} entity (ID: {entity_id}) ---")
        
        # Navigate to entity
        entity_url = f"https://metier.ffbridge.fr/#/entites/{entity_id}/informations"
        print(f"  Navigating to: {entity_url}")
        self.driver.get(entity_url)
        time.sleep(3)
        
        # The scraping logic is now centralized
        self._scrape_informations_principales_unified()
        
        # Analyze other tabs for related tables (1-to-N or N-to-N)
        self._analyze_entity_tabs(entity_type)
        
        print(f"✓ {entity_type} entity analysis completed")

    def _scrape_informations_principales_unified(self):
        """
        Scrapes all sections from the main 'Informations principales' page 
        and adds the fields to the single 'entities' table.
        It uses labels to generate explicit, snake_case field names.
        """
        print("  Scraping 'Informations principales' into unified 'entities' table...")
        
        try:
            # Find all potential field containers. This is a common pattern on the site.
            field_containers = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'row') and .//label]")
            
            for container in field_containers:
                try:
                    label_element = container.find_element(By.TAG_NAME, "label")
                    label_text = label_element.text.strip()

                    if not label_text:
                        continue

                    # Generate a clean, snake_cased field name from the label
                    field_name = to_snake_case(label_text)
                    
                    # Default field type is VARCHAR, can be overridden
                    field_type = 'VARCHAR(255)'

                    # Check if it's a checkbox and adjust type
                    try:
                        container.find_element(By.XPATH, ".//input[@type='checkbox']")
                        field_type = 'BOOLEAN'
                    except:
                        pass # It's not a checkbox

                    # Add the discovered field to the 'entities' table definition
                    self._add_fields_to_table('entities', [(field_name, field_type, label_text)])

                except Exception as e:
                    # Some containers might not be fields, we can ignore them.
                    # print(f"    - Could not parse a container: {e}")
                    pass
        except Exception as e:
            print(f"  ERROR: Could not find field containers on the page. {e}")

    def _analyze_entity_tabs(self, entity_type: str):
        """
        Analyzes the tabs for data that should go into separate, related tables
        (e.g., actors, roles, etc.).
        """
        if entity_type in ['FFB', 'Zone', 'Ligue', 'Comité', 'Club']:
            self._analyze_acteurs_tab()
        
        if entity_type in ['Comité', 'Club']:
            self._analyze_roles_tab()
        
        # Add other tab analyses here for 1-to-N relationships
        # For example: _analyze_tournois_tab, _analyze_facturation_tab etc.
        # These will create new tables like 'tournaments', 'billing_rates' etc.

    def _analyze_acteurs_tab(self):
        """Analyze the Acteurs tab"""
        print("  Analyzing 'Acteurs' tab for 'entity_actors' table...")
        print(f"    Current URL: {self.driver.current_url}")
        print(f"    Page title: {self.driver.title}")
        
        # Debug: List all links on the page
        all_links = self.driver.find_elements(By.TAG_NAME, "a")
        print(f"    Found {len(all_links)} links on page:")
        for i, link in enumerate(all_links[:15]):  # Show first 15 links
            link_text = link.text.strip()
            link_href = link.get_attribute('href')
            link_class = link.get_attribute('class')
            print(f"      {i}: text='{link_text}' href='{link_href}' class='{link_class}'")
        
        # Try to click on Acteurs tab
        try:
            acteurs_xpath = "//a[.//tab-heading[contains(normalize-space(text()), 'Acteurs')]]"
            print(f"    Looking for Acteurs tab with XPath: {acteurs_xpath}")
            acteurs_tab = self.driver.find_element(By.XPATH, acteurs_xpath)
            print(f"    Found Acteurs tab: {acteurs_tab.text}")
            acteurs_tab.click()
            time.sleep(2)
            print(f"    Current URL after clicking Acteurs: {self.driver.current_url}")
        except Exception as e:
            print(f"    Acteurs tab not found - Error: {e}")
            print(f"    Current URL when error occurred: {self.driver.current_url}")
            return
        
        # Define fields for the separate 'entity_actors' table
        actor_fields = [
            ('last_name', 'VARCHAR(255)', 'Nom'),
            ('first_name', 'VARCHAR(255)', 'Prénom'),
            ('middle_name', 'VARCHAR(255)', 'Deuxième prénom'),
            ('role', 'VARCHAR(255)', 'Rôle'),
            ('status', 'VARCHAR(50)', 'Statut')
        ]
        self._add_fields_to_table('entity_actors', actor_fields)

        history_fields = [
            ('last_name', 'VARCHAR(255)', 'Nom'),
            ('first_name', 'VARCHAR(255)', 'Prénom'),
            ('middle_name', 'VARCHAR(255)', 'Deuxième prénom'),
            ('role', 'VARCHAR(255)', 'Rôle'),
            ('status', 'VARCHAR(50)', 'Statut'),
            ('end_date', 'DATE', 'Date de fin'),
            ('page', 'INTEGER', 'Page number')
        ]
        self._add_fields_to_table('entity_actors_history', history_fields)
    
    def _analyze_roles_tab(self):
        """Analyze the Rôles tab"""
        print("  Analyzing 'Rôles' tab for 'entity_roles' table...")
        try:
            roles_xpath = "//a[.//tab-heading[contains(normalize-space(text()), 'Rôles')]]"
            print(f"    Looking for Rôles tab with XPath: {roles_xpath}")
            roles_tab = self.driver.find_element(By.XPATH, roles_xpath)
            print(f"    Found Rôles tab: {roles_tab.text}")
            roles_tab.click()
            time.sleep(2)
            print(f"    Current URL after clicking Rôles: {self.driver.current_url}")
        except Exception as e:
            print(f"    Rôles tab not found - Error: {e}")
            print(f"    Current URL when error occurred: {self.driver.current_url}")
            return
        
        # Define fields for the separate 'entity_roles' table
        role_fields = [
            ('role_name', 'VARCHAR(255)', 'Nom du rôle'),
            ('role_description', 'TEXT', 'Description du rôle'),
            ('role_type', 'VARCHAR(100)', 'Type de rôle')
        ]
        self._add_fields_to_table('entity_roles', role_fields)
    
    def _add_fields_to_table(self, table_name: str, fields: List[tuple]):
        """Add fields to a table in the schema"""
        if table_name not in self.schema['tables']:
            self.schema['tables'][table_name] = {
                'fields': [],
                'primary_key': None,
                'foreign_keys': [],
                'indexes': []
            }
        
        table_definition = self.schema['tables'][table_name]
        # Get existing field names to avoid duplicates
        existing_fields = {field['name'] for field in table_definition['fields']}
        
        for field_name, field_type, description in fields:
            # Skip if field already exists
            if field_name in existing_fields:
                # print(f"    Skipping duplicate field '{field_name}' in table '{table_name}'")
                continue
                
            # Special handling for middle_name
            if field_name == 'middle_name' and table_name == 'entity_actors':
                 # you can add specific logic here if needed in the future
                pass

            field = {
                'name': field_name,
                'type': field_type,
                'description': description,
                'nullable': True,
                'default': None
            }
            
            # Set primary keys
            if table_name == 'entities' and field_name == 'entity_code':
                field['primary_key'] = True
                field['nullable'] = False
            
            table_definition['fields'].append(field)
            existing_fields.add(field_name)

    def _add_junction_table(self, table_name: str, fields: List[tuple]):
        """Add a junction table to the schema"""
        if table_name not in self.schema['tables']:
            self.schema['tables'][table_name] = {
                'fields': [],
                'primary_key': None,
                'foreign_keys': [],
                'indexes': []
            }
        else:
            print(f"    Junction table '{table_name}' already exists, skipping...")
            return
        
        # Get existing field names to avoid duplicates
        existing_fields = {field['name'] for field in self.schema['tables'][table_name]['fields']}
        
        for field_name, field_type, description in fields:
            # Skip if field already exists
            if field_name in existing_fields:
                print(f"    Skipping duplicate field '{field_name}' in junction table '{table_name}'")
                continue
                
            field = {
                'name': field_name,
                'type': field_type,
                'description': description,
                'nullable': False
            }
            self.schema['tables'][table_name]['fields'].append(field)
            existing_fields.add(field_name)  # Update the set
    
    def _add_standard_fields(self, table_name: str):
        """Add standard fields to a table in a specific order at the end."""
        standard_fields_order = [
            'created_at', 'created_by', 'updated_at', 'updated_by', 'soft_deleted'
        ]
        
        standard_fields_map = {
            'created_at': ('TIMESTAMP', 'Date de création', 'CURRENT_TIMESTAMP'),
            'created_by': ('VARCHAR(100)', 'Créé par', None),
            'updated_at': ('TIMESTAMP', 'Date de modification', 'CURRENT_TIMESTAMP'),
            'updated_by': ('VARCHAR(100)', 'Modifié par', None),
            'soft_deleted': ('BOOLEAN', 'Supprimé logiquement', 'FALSE')
        }
        
        table_definition = self.schema['tables'][table_name]
        
        # Get current fields and remove any existing standard fields to re-add them at the end
        current_fields = [f for f in table_definition['fields'] if f['name'] not in standard_fields_order]
        
        new_standard_fields = []
        for field_name in standard_fields_order:
            field_type, description, default = standard_fields_map[field_name]
            field = {
                'name': field_name,
                'type': field_type,
                'description': description,
                'nullable': True,
                'default': default
            }
            new_standard_fields.append(field)

        table_definition['fields'] = current_fields + new_standard_fields
    
    def _clean_schema_duplicates(self):
        """Remove duplicate fields from all tables"""
        print("  Cleaning duplicate fields...")
        for table_name, table_info in self.schema['tables'].items():
            seen_fields = set()
            unique_fields = []
            
            for field in table_info['fields']:
                if field['name'] not in seen_fields:
                    unique_fields.append(field)
                    seen_fields.add(field['name'])
                else:
                    print(f"    Removed duplicate field '{field['name']}' from table '{table_name}'")
            
            table_info['fields'] = unique_fields

    def generate_sql_schema(self):
        """Generate the complete SQL schema"""
        print("\n=== Generating SQL Schema ===")
        
        # Clean duplicates before generating SQL
        self._clean_schema_duplicates()
        
        sql_lines = []
        
        # Add header
        sql_lines.append("-- FFB Database Schema")
        sql_lines.append("-- Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sql_lines.append("-- Based on analysis of entities: 1 (FFB), 2 (Zone), 18 (Ligue), 38 (Comité), 850 (Club)")
        sql_lines.append("")
        
        # Create ENUMs
        sql_lines.extend(self._generate_enums())
        
        # Create tables
        for table_name, table_info in self.schema['tables'].items():
            sql_lines.extend(self._generate_table_sql(table_name, table_info))
        
        # Create indexes
        sql_lines.extend(self._generate_indexes())
        
        # Create foreign key constraints
        sql_lines.extend(self._generate_foreign_keys())
        
        # Create triggers
        sql_lines.extend(self._generate_triggers())
        
        return "\n".join(sql_lines)
    
    def _generate_enums(self):
        """Generate ENUM definitions"""
        enums = []
        
        # Entity types
        enums.append("-- Entity Types")
        enums.append("CREATE TYPE entity_type AS ENUM ('FFB', 'Zone', 'Ligue', 'Comité', 'Club');")
        
        # Status types
        enums.append("-- Status Types")
        enums.append("CREATE TYPE entity_status AS ENUM ('Actif', 'Inactif', 'En attente');")
        
        # Member types
        enums.append("-- Member Types")
        enums.append("CREATE TYPE member_type AS ENUM ('Payé', 'Non payé', 'En attente');")
        
        enums.append("")
        return enums
    
    def _generate_table_sql(self, table_name: str, table_info: Dict):
        """Generate SQL for a single table"""
        sql_lines = []
        
        sql_lines.append(f"-- Table: {table_name}")
        sql_lines.append(f"CREATE TABLE {table_name} (")
        
        field_lines = []
        primary_keys = []
        
        for field in table_info['fields']:
            field_line = f"    {field['name']} {field['type']}"
            
            if not field.get('nullable', True):
                field_line += " NOT NULL"
            
            if field.get('default'):
                field_line += f" DEFAULT {field['default']}"
            
            field_line += f" -- {field['description']}"
            field_lines.append(field_line)
            
            if field.get('primary_key'):
                primary_keys.append(field['name'])
        
        sql_lines.append(",\n".join(field_lines))
        
        # Add primary key
        if primary_keys:
            sql_lines.append(f",\n    PRIMARY KEY ({', '.join(primary_keys)})")
        
        sql_lines.append(");")
        sql_lines.append("")
        
        return sql_lines
    
    def _generate_indexes(self):
        """Generate index definitions"""
        indexes = []
        indexes.append("-- Indexes")
        
        # Entity indexes
        indexes.append("CREATE INDEX idx_entities_type ON entities(type_entite);")
        indexes.append("CREATE INDEX idx_entities_soft_deleted ON entities(soft_deleted);")
        
        # Member indexes
        indexes.append("CREATE INDEX idx_members_license_number ON members(license_number);")
        indexes.append("CREATE INDEX idx_members_entity_code ON members(entity_code);")
        indexes.append("CREATE INDEX idx_members_soft_deleted ON members(soft_deleted);")
        
        # Actor indexes
        indexes.append("CREATE INDEX idx_entity_actors_entity_id ON entity_actors(entity_id);")
        indexes.append("CREATE INDEX idx_entity_actors_statut ON entity_actors(statut);")
        
        # Address indexes
        indexes.append("CREATE INDEX idx_entity_addresses_jeu_entity_id ON entity_addresses_jeu(entity_id);")
        indexes.append("CREATE INDEX idx_entity_addresses_courrier_entity_id ON entity_addresses_courrier(entity_id);")
        indexes.append("CREATE INDEX idx_entity_addresses_facturation_entity_id ON entity_addresses_facturation(entity_id);")
        
        indexes.append("")
        return indexes
    
    def _generate_foreign_keys(self):
        """Generate foreign key constraints"""
        fks = []
        fks.append("-- Foreign Key Constraints")
        
        # Entity relationships
        fks.append("ALTER TABLE entity_actors ADD CONSTRAINT fk_entity_actors_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);")
        fks.append("ALTER TABLE entity_coordinates ADD CONSTRAINT fk_entity_coordinates_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);")
        fks.append("ALTER TABLE entity_notifications ADD CONSTRAINT fk_entity_notifications_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);")
        fks.append("ALTER TABLE entity_complementary_info ADD CONSTRAINT fk_entity_complementary_info_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);")
        fks.append("ALTER TABLE entity_photos ADD CONSTRAINT fk_entity_photos_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);")
        fks.append("ALTER TABLE entity_addresses_jeu ADD CONSTRAINT fk_entity_addresses_jeu_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);")
        fks.append("ALTER TABLE entity_addresses_courrier ADD CONSTRAINT fk_entity_addresses_courrier_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);")
        fks.append("ALTER TABLE entity_addresses_facturation ADD CONSTRAINT fk_entity_addresses_facturation_entity_id FOREIGN KEY (entity_id) REFERENCES entities(entity_code);")
        
        # Member relationships
        fks.append("ALTER TABLE members ADD CONSTRAINT fk_members_entity_code FOREIGN KEY (entity_code) REFERENCES entities(entity_code);")
        
        fks.append("")
        return fks
    
    def _generate_triggers(self):
        """Generate trigger definitions"""
        triggers = []
        triggers.append("-- Triggers")
        
        # Updated at trigger function
        triggers.append("""
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';
""")
        
        # Apply trigger to all tables
        for table_name in self.schema['tables'].keys():
            if table_name not in ['entity_regroupements', 'entity_relationships']:
                triggers.append(f"CREATE TRIGGER update_{table_name}_updated_at BEFORE UPDATE ON {table_name} FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
        
        triggers.append("")
        return triggers
    
    def save_schema(self):
        """Save the schema to files"""
        
        # Add standard fields to all non-junction tables just before saving
        for table_name in self.schema['tables']:
             if 'regroupements' not in table_name: # A simple way to exclude junction tables
                self._add_standard_fields(table_name)

        output_dir = os.path.join(os.path.dirname(__file__), '..', 'FFB_Scraped_Data')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON schema
        schema_file = os.path.join(output_dir, 'database_schema.json')
        with open(schema_file, 'w', encoding='utf-8') as f:
            json.dump(self.schema, f, indent=2, ensure_ascii=False)
        
        # Save SQL schema
        sql_file = os.path.join(output_dir, 'database_schema.sql')
        sql_schema = self.generate_sql_schema()
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write(sql_schema)
        
        print(f"✓ Schema saved to:")
        print(f"  - JSON: {schema_file}")
        print(f"  - SQL: {sql_file}")
    
    def close(self):
        """Close the browser"""
        self.driver.quit()

def main():
    """Main function"""
    generator = DatabaseSchemaGenerator()
    
    try:
        print("=== FFB Database Schema Generator ===")
        
        # Login
        generator.login()
        
        # Analyze each entity type
        entities_to_analyze = [
            (1, 'FFB'),
            (2, 'Zone'),
            (18, 'Ligue'),
            (38, 'Comité'),
            (850, 'Club')
        ]
        
        for entity_id, entity_type in entities_to_analyze:
            generator.analyze_entity_structure(entity_id, entity_type)
        
        # Generate and save schema
        generator.save_schema()
        
        print("\n=== Schema Generation Completed ===")
        print("The database schema has been generated based on the analysis of all entity types.")
        print("Review the generated files and make any necessary adjustments before creating the database.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        generator.close()

if __name__ == "__main__":
    main() 