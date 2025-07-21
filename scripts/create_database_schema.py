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

class DatabaseSchemaGenerator:
    def __init__(self):
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, 10)
        self.schema = {
            'tables': {},
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
        
        print(f"  Current URL after navigation: {self.driver.current_url}")
        print(f"  Page title: {self.driver.title}")
        
        # Analyze main information tab
        self._analyze_informations_principales(entity_type)
        
        # Analyze other tabs based on entity type
        self._analyze_entity_tabs(entity_type)
        
        print(f"✓ {entity_type} entity analysis completed")
    
    def _analyze_informations_principales(self, entity_type: str):
        """Analyze the 'Informations principales' tab"""
        print("  Analyzing 'Informations principales' tab...")
        
        # Section Identification
        self._analyze_identification_section(entity_type)
        
        # Section Subordination
        self._analyze_subordination_section(entity_type)
        
        # Section Coordonnées
        self._analyze_coordonnees_section(entity_type)
        
        # Section Adresse(s) email de notification des factures
        self._analyze_notification_factures_section(entity_type)
        
        # Section Infos complémentaires
        self._analyze_infos_complementaires_section(entity_type)
        
        # Section Photo de l'entité
        self._analyze_photo_entite_section(entity_type)
        
        # Section Adresse
        self._analyze_adresse_section(entity_type)
    
    def _analyze_identification_section(self, entity_type: str):
        """Analyze the Identification section"""
        fields = [
            ('nom_entite', 'VARCHAR(255)', 'Nom de l\'entité'),
            ('numero_entite', 'VARCHAR(50)', 'Numéro d\'entité'),
            ('type_entite', 'VARCHAR(100)', 'Type'),
            ('checkbox_1', 'BOOLEAN', 'Checkbox 1'),
            ('checkbox_2', 'BOOLEAN', 'Checkbox 2'),
            ('checkbox_3', 'BOOLEAN', 'Checkbox 3'),
            ('checkbox_4', 'BOOLEAN', 'Checkbox 4')
        ]
        
        self._add_fields_to_table('entities', fields)
    
    def _analyze_subordination_section(self, entity_type: str):
        """Analyze the Subordination section"""
        if entity_type == 'FFB':
            fields = [
                ('entite_subordination', 'VARCHAR(255)', 'Entité de subordination'),
                ('entite_regroupement', 'VARCHAR(255)', 'Entité de regroupement')
            ]
        elif entity_type in ['Zone', 'Ligue']:
            fields = [
                ('entite_regroupement', 'VARCHAR(255)', 'Entité de regroupement')
            ]
        elif entity_type == 'Comité':
            # Multiple entities de regroupement
            self._add_junction_table('entity_regroupements', [
                ('entity_id', 'VARCHAR(50)', 'FK to entities'),
                ('regroupement_entity_id', 'VARCHAR(50)', 'FK to entities'),
                ('regroupement_type', 'VARCHAR(100)', 'Type of relationship')
            ])
            return
        else:  # Club
            fields = [
                ('subordination', 'VARCHAR(255)', 'Subordination')
            ]
        
        self._add_fields_to_table('entities', fields)
    
    def _analyze_coordonnees_section(self, entity_type: str):
        """Analyze the Coordonnées section"""
        base_fields = [
            ('email', 'VARCHAR(255)', 'E-mail'),
            ('site_internet', 'VARCHAR(255)', 'Site internet'),
            ('telephone_principal', 'VARCHAR(50)', 'Téléphone principal'),
            ('telephone_secondaire', 'VARCHAR(50)', 'Téléphone secondaire')
        ]
        
        if entity_type in ['FFB', 'Comité', 'Club']:
            base_fields.append(('email_competitions', 'VARCHAR(255)', 'E-mail des Compétitions'))
        
        self._add_fields_to_table('entity_coordinates', base_fields)
    
    def _analyze_notification_factures_section(self, entity_type: str):
        """Analyze the notification factures section"""
        fields = [
            ('email_principal', 'VARCHAR(255)', 'E-mail principal'),
            ('email_secondaire', 'VARCHAR(255)', 'E-mail secondaire'),
            ('commentaires', 'TEXT', 'Commentaires')
        ]
        
        self._add_fields_to_table('entity_notifications', fields)
    
    def _analyze_infos_complementaires_section(self, entity_type: str):
        """Analyze the Infos complémentaires section"""
        base_fields = [
            ('info_checkbox_1', 'BOOLEAN', 'Info checkbox 1'),
            ('info_checkbox_2', 'BOOLEAN', 'Info checkbox 2'),
            ('info_checkbox_3', 'BOOLEAN', 'Info checkbox 3'),
            ('nombre_tables', 'INTEGER', 'Nombre de tables'),
            ('organisme_tutelle', 'VARCHAR(255)', 'Organisme de tutelle'),
            ('horaires_ouverture', 'TEXT', 'Horaires d\'ouverture'),
            ('dates_fermeture', 'TEXT', 'Dates de fermeture'),
            ('saisonnier', 'VARCHAR(100)', 'Saisonnier'),
            ('plus_club', 'TEXT', 'Les plus du club')
        ]
        
        if entity_type == 'Club':
            base_fields.append(('participe_seances_decouverte', 'BOOLEAN', 'Participe aux 5 séances Découverte'))
        
        # 6 empty text blocks
        for i in range(1, 7):
            base_fields.append((f'info_texte_{i}', 'TEXT', f'Info texte {i}'))
        
        self._add_fields_to_table('entity_complementary_info', base_fields)
    
    def _analyze_photo_entite_section(self, entity_type: str):
        """Analyze the Photo de l'entité section"""
        fields = [
            ('photo_texte', 'TEXT', 'Photo texte'),
            ('photo_url', 'VARCHAR(500)', 'Photo URL'),
            ('photo_recommendations', 'TEXT', 'Photo recommendations'),
            ('photo_consigne', 'TEXT', 'Photo consigne')
        ]
        
        self._add_fields_to_table('entity_photos', fields)
    
    def _analyze_adresse_section(self, entity_type: str):
        """Analyze the Adresse section"""
        # Jeu address
        jeu_fields = [
            ('address_line_1', 'VARCHAR(255)', 'Address Line 1'),
            ('address_line_2', 'VARCHAR(255)', 'Address Line 2'),
            ('address_line_3', 'VARCHAR(255)', 'Address Line 3'),
            ('zipcode', 'VARCHAR(50)', 'Zipcode'),
            ('city', 'VARCHAR(255)', 'City'),
            ('country', 'VARCHAR(255)', 'Country')
        ]
        
        # Courrier address
        courrier_fields = [
            ('courrier_opg_option', 'VARCHAR(100)', 'Courrier OPG option'),
            ('courrier_1', 'VARCHAR(255)', 'Courrier 1'),
            ('courrier_2', 'VARCHAR(255)', 'Courrier 2'),
            ('courrier_3', 'VARCHAR(255)', 'Courrier 3'),
            ('courrier_4', 'VARCHAR(255)', 'Courrier 4'),
            ('courrier_5', 'VARCHAR(255)', 'Courrier 5'),
            ('courrier_6', 'VARCHAR(255)', 'Courrier 6'),
            ('country', 'VARCHAR(255)', 'Country')
        ]
        
        # Facturation address
        facturation_fields = [
            ('facturation_opg_option', 'VARCHAR(100)', 'Facturation OPG option'),
            ('facturation_1', 'VARCHAR(255)', 'Facturation 1'),
            ('facturation_2', 'VARCHAR(255)', 'Facturation 2'),
            ('facturation_3', 'VARCHAR(255)', 'Facturation 3'),
            ('facturation_4', 'VARCHAR(255)', 'Facturation 4'),
            ('facturation_5', 'VARCHAR(255)', 'Facturation 5'),
            ('facturation_6', 'VARCHAR(255)', 'Facturation 6'),
            ('country', 'VARCHAR(255)', 'Country')
        ]
        
        self._add_fields_to_table('entity_addresses_jeu', jeu_fields)
        self._add_fields_to_table('entity_addresses_courrier', courrier_fields)
        self._add_fields_to_table('entity_addresses_facturation', facturation_fields)
    
    def _analyze_entity_tabs(self, entity_type: str):
        """Analyze other tabs based on entity type"""
        if entity_type in ['FFB', 'Zone', 'Ligue', 'Comité', 'Club']:
            self._analyze_acteurs_tab()
        
        if entity_type in ['Comité', 'Club']:
            self._analyze_roles_tab()
        
        if entity_type in ['Zone', 'Ligue', 'Comité', 'Club']:
            self._analyze_tournois_tab()
        
        if entity_type in ['Comité', 'Club']:
            self._analyze_facturation_tab()
        
        if entity_type in ['FFB', 'Comité']:
            self._analyze_tableau_de_bord_tab()
        
        if entity_type == 'Comité':
            self._analyze_clubs_actifs_inactifs_tab()
        
        if entity_type == 'Club':
            self._analyze_cours_tab()
            self._analyze_ecoles_bridge_section()
            self._analyze_enseignants_actifs_section()
    
    def _analyze_acteurs_tab(self):
        """Analyze the Acteurs tab"""
        print("  Analyzing 'Acteurs' tab...")
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
        
        # Analyze Actifs sub-tab
        self._analyze_acteurs_actifs()
        
        # Analyze Historique sub-tab
        self._analyze_acteurs_historique()
    
    def _analyze_acteurs_actifs(self):
        """Analyze the Actifs sub-tab"""
        fields = [
            ('nom', 'VARCHAR(255)', 'Nom'),
            ('prenom', 'VARCHAR(255)', 'Prénom'),
            ('role', 'VARCHAR(255)', 'Rôle'),
            ('statut', 'VARCHAR(50)', 'Statut')
        ]
        
        self._add_fields_to_table('entity_actors', fields)
    
    def _analyze_acteurs_historique(self):
        """Analyze the Historique sub-tab"""
        # Same structure as actifs but with additional fields
        fields = [
            ('nom', 'VARCHAR(255)', 'Nom'),
            ('prenom', 'VARCHAR(255)', 'Prénom'),
            ('role', 'VARCHAR(255)', 'Rôle'),
            ('statut', 'VARCHAR(50)', 'Statut'),
            ('date_fin', 'DATE', 'Date de fin'),
            ('page', 'INTEGER', 'Page number')
        ]
        
        self._add_fields_to_table('entity_actors_history', fields)
    
    def _analyze_roles_tab(self):
        """Analyze the Rôles tab"""
        print("  Analyzing 'Rôles' tab...")
        print(f"    Current URL: {self.driver.current_url}")
        print(f"    Page title: {self.driver.title}")
        
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
        
        # Generic roles table structure
        self._add_fields_to_table('entity_roles', [
            ('role_name', 'VARCHAR(255)', 'Nom du rôle'),
            ('role_description', 'TEXT', 'Description du rôle'),
            ('role_type', 'VARCHAR(100)', 'Type de rôle')
        ])
    
    def _analyze_tournois_tab(self):
        """Analyze the Tournois tab"""
        print("  Analyzing 'Tournois' tab...")
        print(f"    Current URL: {self.driver.current_url}")
        print(f"    Page title: {self.driver.title}")
        
        try:
            tournois_xpath = "//a[.//tab-heading[contains(normalize-space(text()), 'Tournois')]]"
            print(f"    Looking for Tournois tab with XPath: {tournois_xpath}")
            tournois_tab = self.driver.find_element(By.XPATH, tournois_xpath)
            print(f"    Found Tournois tab: {tournois_tab.text}")
            tournois_tab.click()
            time.sleep(2)
            print(f"    Current URL after clicking Tournois: {self.driver.current_url}")
        except Exception as e:
            print(f"    Tournois tab not found - Error: {e}")
            print(f"    Current URL when error occurred: {self.driver.current_url}")
            return
        
        # Analyze Calendrier if available
        try:
            calendrier_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Calendrier')]")
            calendrier_btn.click()
            time.sleep(2)
            
            self._add_fields_to_table('tournament_calendar', [
                ('tournament_name', 'VARCHAR(255)', 'Nom du tournoi'),
                ('tournament_date', 'DATE', 'Date du tournoi'),
                ('tournament_location', 'VARCHAR(255)', 'Lieu'),
                ('tournament_type', 'VARCHAR(100)', 'Type de tournoi'),
                ('legende', 'TEXT', 'Légende')
            ])
        except:
            print("    Calendrier not available")
    
    def _analyze_facturation_tab(self):
        """Analyze the Facturation tab"""
        print("  Analyzing 'Facturation' tab...")
        print(f"    Current URL: {self.driver.current_url}")
        print(f"    Page title: {self.driver.title}")
        
        try:
            facturation_xpath = "//a[.//tab-heading[contains(normalize-space(text()), 'Facturation')]]"
            print(f"    Looking for Facturation tab with XPath: {facturation_xpath}")
            facturation_tab = self.driver.find_element(By.XPATH, facturation_xpath)
            print(f"    Found Facturation tab: {facturation_tab.text}")
            facturation_tab.click()
            time.sleep(2)
            print(f"    Current URL after clicking Facturation: {self.driver.current_url}")
        except Exception as e:
            print(f"    Facturation tab not found - Error: {e}")
            print(f"    Current URL when error occurred: {self.driver.current_url}")
            return
        
        # Barèmes section
        self._add_fields_to_table('billing_rates', [
            ('part_ffb', 'DECIMAL(10,2)', 'Part FFB'),
            ('part_comite', 'DECIMAL(10,2)', 'Part comité'),
            ('total', 'DECIMAL(10,2)', 'Total'),
            ('rate_type', 'VARCHAR(100)', 'Type de barème')
        ])
        
        # Prix des licences
        self._add_fields_to_table('license_prices', [
            ('license_type', 'VARCHAR(100)', 'Type de licence'),
            ('price', 'DECIMAL(10,2)', 'Prix'),
            ('description', 'TEXT', 'Description')
        ])
        
        # Montants FFB
        self._add_fields_to_table('ffb_amounts', [
            ('total', 'DECIMAL(10,2)', 'Total'),
            ('amount_type', 'VARCHAR(100)', 'Type de montant')
        ])
        
        # Somme due au comité
        self._add_fields_to_table('committee_amounts', [
            ('amount_description', 'VARCHAR(255)', 'Description'),
            ('amount', 'DECIMAL(10,2)', 'Montant'),
            ('due_date', 'DATE', 'Date d\'échéance')
        ])
        
        # 5 séance Découverte
        self._add_fields_to_table('discovery_sessions', [
            ('session_name', 'VARCHAR(255)', 'Nom de la session'),
            ('session_date', 'DATE', 'Date de la session'),
            ('participants', 'INTEGER', 'Nombre de participants')
        ])
        
        # Montants Comité/FFB (Club specific)
        self._add_fields_to_table('committee_ffb_amounts', [
            ('titre', 'VARCHAR(255)', 'Titre'),
            ('montant', 'DECIMAL(10,2)', 'Montant'),
            ('warning', 'TEXT', 'Warning')
        ])
        
        # Transfers de licences (Club specific)
        self._add_fields_to_table('license_transfers', [
            ('transfer_type', 'VARCHAR(100)', 'Type de transfert'),
            ('from_entity', 'VARCHAR(50)', 'Entité d\'origine'),
            ('to_entity', 'VARCHAR(50)', 'Entité de destination'),
            ('transfer_date', 'DATE', 'Date de transfert')
        ])
    
    def _analyze_tableau_de_bord_tab(self):
        """Analyze the Tableau de bord tab"""
        print("  Analyzing 'Tableau de bord' tab...")
        
        try:
            tableau_tab = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Tableau de bord')]")
            tableau_tab.click()
            time.sleep(2)
        except:
            print("    Tableau de bord tab not found")
            return
        
        # Licences et Tournois stats
        self._add_fields_to_table('dashboard_stats', [
            ('stat_title', 'VARCHAR(255)', 'Titre de la statistique'),
            ('stat_value', 'VARCHAR(255)', 'Valeur'),
            ('stat_type', 'VARCHAR(100)', 'Type de statistique'),
            ('stat_period', 'VARCHAR(100)', 'Période')
        ])
    
    def _analyze_clubs_actifs_inactifs_tab(self):
        """Analyze the Clubs actifs inactifs tab"""
        print("  Analyzing 'Clubs actifs inactifs' tab...")
        
        try:
            clubs_tab = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Clubs actifs inactifs')]")
            clubs_tab.click()
            time.sleep(2)
        except:
            print("    Clubs actifs inactifs tab not found")
            return
        
        self._add_fields_to_table('club_status', [
            ('club_name', 'VARCHAR(255)', 'Nom du club'),
            ('club_code', 'VARCHAR(50)', 'Code du club'),
            ('statut', 'VARCHAR(50)', 'Statut (Actif/Inactif)'),
            ('last_activity', 'DATE', 'Dernière activité')
        ])
    
    def _analyze_cours_tab(self):
        """Analyze the Cours tab"""
        print("  Analyzing 'Cours' tab...")
        
        try:
            cours_tab = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Cours')]")
            cours_tab.click()
            time.sleep(2)
        except:
            print("    Cours tab not found")
            return
        
        self._add_fields_to_table('courses', [
            ('course_name', 'VARCHAR(255)', 'Nom du cours'),
            ('course_type', 'VARCHAR(100)', 'Type de cours'),
            ('instructor', 'VARCHAR(255)', 'Instructeur'),
            ('schedule', 'VARCHAR(255)', 'Horaire'),
            ('duration', 'VARCHAR(100)', 'Durée')
        ])
    
    def _analyze_ecoles_bridge_section(self):
        """Analyze the Écoles de bridge section"""
        self._add_fields_to_table('bridge_schools', [
            ('ecoles_texte', 'TEXT', 'Texte des écoles'),
            ('ecoles_logo_url', 'VARCHAR(500)', 'URL du logo')
        ])
    
    def _analyze_enseignants_actifs_section(self):
        """Analyze the Enseignants actifs section"""
        self._add_fields_to_table('active_teachers', [
            ('nom', 'VARCHAR(255)', 'Nom'),
            ('prenom', 'VARCHAR(255)', 'Prénom'),
            ('agrement', 'VARCHAR(100)', 'Agrément'),
            ('validity_date', 'DATE', 'Date de validité')
        ])
    
    def _add_fields_to_table(self, table_name: str, fields: List[tuple]):
        """Add fields to a table in the schema"""
        if table_name not in self.schema['tables']:
            self.schema['tables'][table_name] = {
                'fields': [],
                'primary_key': None,
                'foreign_keys': [],
                'indexes': []
            }
        
        # Get existing field names to avoid duplicates
        existing_fields = {field['name'] for field in self.schema['tables'][table_name]['fields']}
        
        for field_name, field_type, description in fields:
            # Skip if field already exists
            if field_name in existing_fields:
                print(f"    Skipping duplicate field '{field_name}' in table '{table_name}'")
                continue
                
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
            elif table_name == 'members' and field_name == 'member_license':
                field['primary_key'] = True
                field['nullable'] = False
            
            # Add standard fields for non-junction tables
            if table_name not in ['entity_regroupements', 'entity_relationships']:
                if field_name not in ['created_at', 'updated_at', 'created_by', 'updated_by', 'soft_deleted']:
                    self.schema['tables'][table_name]['fields'].append(field)
                    existing_fields.add(field_name)  # Update the set
        
        # Add standard fields (only if not already present)
        self._add_standard_fields(table_name)
    
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
        """Add standard fields to a table"""
        standard_fields = [
            ('created_at', 'TIMESTAMP', 'Date de création', 'CURRENT_TIMESTAMP'),
            ('updated_at', 'TIMESTAMP', 'Date de modification', 'CURRENT_TIMESTAMP'),
            ('created_by', 'VARCHAR(100)', 'Créé par', None),
            ('updated_by', 'VARCHAR(100)', 'Modifié par', None),
            ('soft_deleted', 'BOOLEAN', 'Supprimé logiquement', 'FALSE')
        ]
        
        # Get existing field names to avoid duplicates
        existing_fields = {field['name'] for field in self.schema['tables'][table_name]['fields']}
        
        for field_name, field_type, description, default in standard_fields:
            # Skip if field already exists
            if field_name in existing_fields:
                print(f"    Skipping duplicate standard field '{field_name}' in table '{table_name}'")
                continue
                
            field = {
                'name': field_name,
                'type': field_type,
                'description': description,
                'nullable': True,
                'default': default
            }
            self.schema['tables'][table_name]['fields'].append(field)
            existing_fields.add(field_name)  # Update the set
    
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