# FFB-Data

Ce projet est un scraper pour récupérer les données des joueurs de bridge de la région Lorraine depuis le site de la Fédération Française de Bridge (FFB).

## Fonctionnalités

- Scraping des informations des clubs (entités) de la région Lorraine
- Scraping des informations des joueurs (licenciés) par club
- Gestion des données via Supabase
- Support Docker pour le déploiement

## Installation

1. Créer un fichier `.env` avec vos identifiants Supabase :
```
SUPABASE_URL=votre_url
SUPABASE_KEY=votre_clé
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancer le scraper :
```bash
python scraper.py
```

## Structure des données

Le projet utilise les modèles suivants :

- `Entite` : Informations sur les clubs
- `Licensee` : Informations sur les joueurs
- `ClubMember` : Relations entre clubs et joueurs

## Technologies utilisées

- Python
- Selenium pour le scraping
- Supabase pour la base de données
- Docker pour le déploiement
- Playwright pour la gestion des navigateurs

## Contributing

N'hésitez pas à contribuer au projet en soumettant des pull requests ou en signalant des bugs.

## Licence

Ce projet est sous licence MIT.
