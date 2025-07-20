# FFB Database - Projet Bridge

Base de données pour la Fédération Française de Bridge (FFB) utilisant Prisma et Supabase.

## 🚀 Configuration

### 1. Installation des dépendances
```bash
npm install
```

### 2. Configuration de l'environnement
Copiez le fichier `.env.example` vers `.env` et configurez vos variables d'environnement :

```env
# === SUPABASE ===
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_ANON_KEY=votre-clé-anon
SUPABASE_SERVICE_ROLE_KEY=votre-clé-service

# === POSTGRESQL ===
DATABASE_URL="postgresql://postgres:votre-mot-de-passe@votre-host:5432/postgres"
```

### 3. Génération du client Prisma
```bash
npm run db:generate
```

## 📊 Modèles de données

### Club
- Informations de base (nom, code, adresse, etc.)
- Relations avec joueurs, rôles et agréments

### Joueur
- Informations personnelles (nom, prénom, licence, etc.)
- Relation avec le club d'appartenance
- Relations avec rôles et agréments

### Role
- Définition des rôles/fonctions
- Relations avec joueurs et clubs

### Agrement
- Définition des agréments/autorisations
- Relations avec joueurs et clubs

## 🔧 Scripts disponibles

### Base de données
```bash
# Générer le client Prisma
npm run db:generate

# Récupérer le schéma de la base
npm run db:pull

# Créer une migration
npm run db:migrate

# Ouvrir Prisma Studio
npm run db:studio
```

### Import/Export
```bash
# Importer les données CSV
npm run import:data

# Tester la connexion
npm run test:connection
```

## 📁 Structure du projet

```
FFB_Database/
├── prisma/
│   └── schema.prisma          # Schéma de la base de données
├── scripts/
│   ├── import-data.js         # Script d'import CSV
│   └── test-connection.js     # Script de test
├── clubs.csv                  # Données des clubs
├── players.csv                # Données des joueurs
└── .env                       # Variables d'environnement
```

## 🚨 Résolution des problèmes

### Problème de connexion
Si vous obtenez une erreur de connexion :
1. Vérifiez que votre projet Supabase est actif
2. Vérifiez les variables d'environnement dans `.env`
3. Testez la connexion avec `npm run test:connection`

### Problème d'import
Si l'import échoue :
1. Vérifiez que les fichiers CSV sont dans le bon format
2. Vérifiez que la base de données est accessible
3. Consultez les logs d'erreur

## 📝 Notes

- Les fichiers `.env`, `.gitignore` et `.cursorignore` sont ignorés par Git
- Le client Prisma est généré automatiquement après modification du schéma
- Les scripts d'import gèrent automatiquement les relations entre les tables

## 📚 FFB-Specific Data Model & Schema Reference

For historical and reference purposes, the following files document the original FFB data model and SQL schema used for scraping and legacy import:

- [docs/FFB_data_schema.md](docs/FFB_data_schema.md): Detailed documentation of the FFB data model (clubs, players, roles, etc.)
- [scripts/ffb_schema.sql](scripts/ffb_schema.sql): Original FFB SQL schema (not used in production)

> **Note:** The main schema for your Supabase/PostgreSQL database is defined in [schema.sql](schema.sql) at the root. Always keep this file up to date with your live database structure.

## 🚦 Scraper Progress & Status (July 2025)

- Scrapes all Lorraine clubs/entities (skipping Comité de Lorraine and first 3 dropdown entries)
- For each club: visits info page, robustly saves clubs.csv after each entity
- For each club: scrapes all members (current and renewed), handles 'Sympathisant' (licence ending with 's')
- Outputs tab-delimited CSVs for both clubs and players
- Saves players.csv after each club to minimize data loss
- Known issue: error when navigating to member section (under investigation)
- Script is robust for large-scale scraping, but under active development for further detail and error handling

## 🚦 Scraper Refactor Plan (July 2025)

- **Batch-first scraping:**
  - Scrape all clubs/entities from the dropdown, collecting all info from the /informations page and FFB entity ID.
  - Build the clubs DataFrame with all fields encountered, dynamically adding columns as new fields are found (missing values filled with '').
  - Save the full clubs.csv only after all entities are processed.
  - Print progress (e.g., "Comité de Lorraine - Collecte des Clubs - Traités n/total").
- **Member scraping:**
  - For each club, build the URL for the members list and scrape all members, always including the FFB licensee ID.
  - Build the players DataFrame, dynamically adding columns as new fields are found (missing values filled with '').
  - Save the full players.csv only after all members are processed.
- **Section-by-section deep scraping:**
  - For each section/tab, iterate through the relevant DataFrame, build the URL, and scrape all new fields, updating the DataFrame and saving after each section.
  - Print progress for each section and entity/member.
- **Dynamic DataFrame handling:**
  - As new fields are scraped, add them to the DataFrame if they don’t exist, filling missing values for previous rows with ''.
  - Final CSVs always have all columns seen so far, matching the evolving DB schema.
- **Navigation optimization:**
  - Batch scraping and direct URL building minimize navigation time.
- **Scalability:**
  - Approach is robust for all committees and the full FFB dataset (1050 clubs, 100,000+ members).
- **Error handling & data safety:**
  - Save CSVs after each major batch/section to avoid data loss.
  - Print errors and continue processing to maximize data collection.

> The script is being refactored to follow this plan for maximum efficiency, robustness, and scalability.

## 🛡️ Robust Scraper Checkpointing & Recovery (2025)

- The scraper saves the CSV after each major section (e.g., "Informations principales") is scraped for all entities.
- On error for an entity, the error and entity ID are logged, the entity is skipped, and scraping continues.
- On crash or interruption, the scraper saves progress before exiting.
- On restart, the scraper resumes from the last successfully scraped entity (using the URL ID or a progress log).
- Timing and debug prints are provided for each major block per entity.
- The CSV always contains the full entity IDs as scraped (with all digits/leading zeros) and all relevant fields.
- An error log file is maintained for skipped entities or sections.
- This hybrid checkpointing approach ensures minimal data loss, easy recovery, and robust, maintainable scraping.

# FFB_Database Scraping - Details on what, where the data are.

For all of these, the BreadCrumb is a source of information but not to be scraped

FFB (ID: 1)
BreadCumb : Entités > FFB > Informations principales
	Tab INFORMATIONS PRINCIPALES
        * Identification
            * Nom de l’entité
            * Numéro d’entité
            * Type
            * Check boxes (All 4, with checked/not checked)
        * Subordination
            * Entité de subordination
            * Entité de regroupement
        * Coordonnées
            * E-mail
            * Site internet
            * Téléphone principal
            * Téléphone secondaire
            * E-mail des Compétitions
        * Adresse(s) email de notification des factures
            * E-mail principal
            * E-mail secondaire
            * Commentaires
        * Infos complémentaires
            * 3 check boxes with their check status
            * Nombre de tables
            * Organisme de tutelle
            * Horaires d’ouverture
            * Dates de fermeture
            * Saisonnier
            * Les plus du club
        * Photo de l’entité 
            * Texte, image et Recommendations à droite de l’image
        * Adresse
            * Jeu
                * Tous les champs
                * Lien Google map (voir sur la carte)
            * Courrier (bandeau comprimé), développé, on y trouve
                * Un optionGroupButton, seule la première option fonctionne (peut-être que les autres aussi si, il y a quelque chose derrière)
                * 6 Text Boxes
            * Facturation
                * Idem que courrier
	Tab ACTEURS
        * Onglet Actifs (Le titre “Liste des acteurs actifs”, toute la liste, peut être sur plusieurs pages, mais, ça m’étonnerait)
            * Onglet Historique (Le titre “Liste des acteurs inactifs”, la liste (ATTENTION : Plusieurs pages, navigations en bas de la liste)
	Tab TOURNOIS : Inaccessible
	Tab TABLEAU DE BORD
        * Onglet Licences et Tournois
            Des stats sous forme de tableaux avec chacun leur titre
            Là, faut être clever, on ne retrouve ce Tab qu’au niveau des clubs, je ne sais pas, mais ça peut servir, on prends.

Zone (ID: 2)
BreadCrumb : Entités > Dropdown list > Informations principales (qui se décompose ainsi)
				7 digits : Numéro de l’entité - Type d’entité (Zone) - Code de l’entité (I, II, III…) 				Nom de l’entité > Informations principales
	Tab INFORMATIONS PRINCIPALES
        * Identification : Idem FFB
        * Subordination , ⊖ Entité de regroupement
        * Coordonnées : Titre présent mais pas de bloc texte (parce que pas de data ? Dans la table, ce n’est pas grave, mais pour ton contrôleur… Je pense qu’on prend quand même. Il sera toujours plus facile de commenter ou supprimer plus tard dans le contrôleur.
        * Adresses(s) mails de notifications de factures : Comme coordonnées de la Zone 
        * ⊖⊖⊖⊖⊖ Plus rien après, fin de la page
	Tab ACTEURS : Idem FFB
	Tab TOURNOIS
        * ⊕ Un bandeau vertical sur la gauche avec 3 choix (Organisation, Livret, Calendrier)
            Les deux premiers sont cliquables mais, pas de données derrière
            Le troisième : Option indisponible pour cette entité
	⊖ Tab TABLEAU DE BORD
    * ⊖⊖⊖⊖⊖ FIN DE LA PAGE

Ligue (ID: 18)
BreadCrumb : Idem Zone sauf Code de l’entité (01, 02, 03...) 
	Tab INFORMATIONS PRINCIPALES
        * Identification : Idem FFB
        * Subordination : Idem Zone
	⊖ Entité de regroupement (Bizarre qu’il n’y ait pas Zone I AL-BO-CP-FL-LO)
        * Coordonnées
            * E-mail Compétions renseigné. Rien d’autre/ Cela confirme peut-être que s’il n’y a pas de données derrière, les blocs texte ne s’affichent pas.
        * Adresse(s) email de notification des factures : Titre mais pas de bloc texte (même raison que pour Coordonnées ?)
	Tab ACTEURS : idem Zone
	Tab Tournois : Idem Zone

Comité (ID: 38)
BreadCrumb : Idem Ligue sauf Code de l’entité (de… Lorraine, d’Anjou, de Bourgogne…) 
	Tab INFORMATIONS PRINCIPALES
        * Identification : Idem FFB
        * Subordination : Idem Zone
            * ⊕ Entité de regroupement : Ligue 09 AL-BO-LO
            * ⊕ Entité de regroupement : Zone 09 AL-BOCP-FL-LO
        * Coordonnées : Idem FFB
        * Adresse(s) email de notification des factures
            * E-mail principal + Bloc de texterenseigné
            * E-mail secondaire + Bloc de texte mais vide
            * ⊕ Commentaires + Bloc de texte rensseigné
            Ça vient peut-être contredire ce que je pensais, à moins que les champs de la BDD FFB aient dans un cas des NULL value et dans l’autre “”
        * Infos complémentaires
            * 3 check boxes et leur valeur
            * 6 blocs de texte vides
        * Photo de l’identité
            * Texte
            * Bloc photo mais vide
            * Consigne à côté, en bas à droite de l’image
        * Adresse
            * Jeu : On scrap les 6 blocs de texte
            * Courrier : On scrap les 6 blocs de texte
            * Facturation : On scrap les 6 blocs de texte
	Tab ACTEURS : idem Zone
	Tab RÔLES
        * On ne scrap que la liste avec les en-têtes, sans la colonne Actions
	Tab TOURNOIS
	Un bandeau vertical sur la gauche
        * Organisation : on ne peut s’inscrire ni voir qui est inscrit, on passe
        * Livret : Sans intérêt, c’est gérer en amont par les organisateurs
        * Calendrier : On scrap le tableau et la légende
	Tab FACTURATION
	Un bandeau vertical sur la gauche avec plusieurs options
        * Barèmes
            * AFFILIATION DU CLUB
                * Part FFB : 75€
                * Part comité : 10€
                * Total 85€
            * PRIX DES LICENCES
                * On scrap la liste avec ses en-têtes, sauf la colonne Action
        * Montants FFB : Bloc texte TOTAL
            * SOMME DUE AU COMITÉ 
                * On scrap la liste avec ses en-têtes, sauf la colonne Action
        * Encaissemens : On passe
        * Factures FFB : On passe
        * Parcours Bridge : On passe
        * As de Trèfle : On Passe
        * 5 séance Découverte : On scrap Titre + Liste (même vide)
	Tab TABLEAU DE BORD
        * Licences et Tournois : On scrap Titres et Tableaux

	Tab CLUBS ACTIFS INACTIFS
        * On scrap Titre + Liste (même vide), Dernière colonne : RadioButton Actif / Inactif

	Tab ENSEIGNANTS : Non maintenu et double emploi, on passe

	Tab ARBITRES : Non maintenu et double emploi, on passe


Club (ID: 850)
	BreadCrumb : Entités > Dropdown list > Informations principales (qui se décompose ainsi)
	⊖			7 digits : Numéro de l’entité - Nom de l’entité > Informations principales

	Tab INFORMATIONS PRINCIPALES
        * Identification : Idem FFB.
        * Subordination :
            * Subordination : Idem Comité, 1 seul bloc de texte vide
        * Coordonnées : Idem Comité ⊖E-mail Compétitions
        * Adresse(s) email de notification des factures : Idem Comité 
        * Infos complémentaires : Idem Comité 
            * ⊕ Votre club participe aux opérations “5 séances Découverte” + RadioButton
            * 3 check boxes et leur valeur
            * 6 blocs de texte vides
        * Photo de l’identité
            * Texte
            * Bloc photo renseigné
            * Consigne à côté, en bas à droite de l’image
        * ⊕ Écoles de bridge + Logo
            * Texte
        * Liste des enseignants actifs avec un agrément valide
En-tête + Liste
        * Adresse : Idem Comité

	Tab ACTEURS : idem Comité
	Tab RÔLES
        * On ne scrap que la liste avec les en-têtes, sans la colonne Actions
	Tab TOURNOIS
	Un bandeau vertical sur la gauche
        * Organisation : on ne peut s’inscrire ni voir qui est inscrit, on passe
        * Livret : Sans intérêt, c’est gérer en amont par les organisateurs
        * Calendrier : On scrap le tableau et la légende
	Tab COURS : On scrap le tableau sans la dernière colonne

	Tab FACTURATION
	Un bandeau vertical sur la gauche avec plusieurs options
        * Barèmes
            * AFFILIATION DU CLUB
                * Part FFB : 57,50€
                * Part comité : 10€
                * Total 67,505€
            * PRIX DES LICENCES
                * On scrap la liste avec ses en-têtes, sauf la colonne Action
        * ⊕⊕⊕ Montants Comité/FFB :
            * Titre + Tableau + Warning sous le tableau
            * ⊕ TRANSFERTS DE LICENCES : En-têtes + Liste
            * SOMME DUE AU COMITÉ 
                * On scrap la liste avec ses en-têtes, sauf la colonne Action
        * Encaissemens : On passe
        * Factures FFB : On passe
        * Parcours Bridge : On passe
        * As de Trèfle : On Passe
        * 5 séance Découverte : On scrap Titre + Liste (même vide) si présente

					THIS IS THE END !

---

# 📝 Project Progress & Robust Scraping Architecture (2025)

- **Dual-URL member scraping and status merging**: The scraper now collects member data from both the full list (encaissement) and the renewed/consultation list, merging statuses for completeness.
- **CSV-based parsing**: Member tables are parsed as tab-delimited CSV for reliability and speed, with robust header detection and status inference.
- **Robust error handling**: The scraper gracefully handles missing OPGButtons, absent or empty tables, and navigation errors, logging issues and skipping problematic entities without hanging.
- **Modular scraping functions**: Each entity type (FFB, Zone, etc.) will have its own modular scraping function, with a clear, commented skeleton for each section (informations principales, acteurs, tableau de bord, etc.).
- **Clear separation of logic**: The codebase is structured so that each section/tab of the FFB site is scraped by a dedicated function, making it easy to adapt to new entity types or changes in the site structure.
- **Checkpointing and recovery**: The scraper saves progress after each major section, can resume from the last successful entity, and maintains error logs for skipped entities or sections.
- **API key hygiene**: Guidance is provided for handling public API key leaks, including revoking, deleting, and purging secrets from git history, and ensuring sensitive files are not tracked.

---
