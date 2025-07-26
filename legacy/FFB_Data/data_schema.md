# Schéma des Données - FFB Data

## 1. Entités (Clubs)

### Champs Principaux
- **id** (int) - Identifiant unique du club
- **nom** (str) - Nom du club
- **adresse** (str) - Adresse complète
- **code_postal** (str) - Code postal
- **ville** (str) - Ville
- **telephone** (str) - Numéro de téléphone
- **email** (str) - Adresse email
- **region** (str) - Région (Lorraine)
- **departement** (str) - Département
- **created_at** (datetime) - Date de création
- **updated_at** (datetime) - Date de dernière mise à jour

### Champs Possibles à Explorer
- Numéro SIRET
- Site web
- Horaires d'ouverture
- Capacité
- Type d'entité (club, école, etc.)

## 2. Joueurs (Licensees)

### Champs Principaux
- **id** (int) - Identifiant unique
- **nom** (str) - Nom
- **prenom** (str) - Prénom
- **numero_licence** (str) - Numéro de licence FFB
- **date_naissance** (date) - Date de naissance
- **email** (str) - Adresse email
- **telephone** (str) - Numéro de téléphone
- **adresse** (str) - Adresse complète
- **code_postal** (str) - Code postal
- **ville** (str) - Ville
- **besoin_special** (bool) - Indicateur de besoin spécial
- **club_id** (int) - Club principal
- **statut** (str) - Statut (licencié, sympathisant, bénévole)
- **saison** (str) - Saison de la licence
- **created_at** (datetime) - Date de création
- **updated_at** (datetime) - Date de dernière mise à jour

### Champs Possibles à Explorer
- Genre
- Date d'inscription
- Catégorie d'âge
- Niveau de jeu
- Points FFB
- Historique des clubs
- Statistiques de jeu

## 3. Rôles

### Champs Principaux
- **id** (int) - Identifiant unique
- **nom** (str) - Nom du rôle
- **description** (str) - Description du rôle
- **created_at** (datetime) - Date de création

### Rôles Potentiels à Explorer
- Président
- Secrétaire
- Trésorier
- Responsable des tournois
- Professeur
- Bénévole
- Autres rôles spécifiques

## 4. Relations Joueurs-Rôles

### Structure
- **licensee_id** (int) - Référence au joueur
- **role_id** (int) - Référence au rôle
- **created_at** (datetime) - Date de création
- **updated_at** (datetime) - Date de dernière mise à jour

### Notes
- Un joueur peut avoir plusieurs rôles
- Les rôles peuvent changer au fil du temps
- Certains rôles peuvent être temporaires

## Notes Techniques

### Index à Créer
- Sur les noms et prénoms des joueurs
- Sur les clubs
- Sur les statuts et saisons
- Sur les rôles

### Contraintes
- Uniques sur les identifiants
- Uniques sur les numéros de licence
- Références obligatoires entre les tables

### Points à Clarifier
1. Structure exacte des données sur la page des clubs
2. Structure exacte des données sur la page des joueurs
3. Format des dates et heures
4. Format des numéros de téléphone
5. Format des adresses
6. Liste complète des statuts possibles
7. Liste complète des rôles possibles

### Questions à Résoudre
1. Quels sont les champs obligatoires vs optionnels ?
2. Y a-t-il des validations spécifiques sur certains champs ?
3. Quelles sont les relations possibles entre les tables ?
4. Quelles sont les données historiques à conserver ?
5. Quelles sont les données sensibles à protéger ?

### Exemples de Requêtes Possibles
1. Liste des joueurs par club
2. Liste des rôles par joueur
3. Statistiques par club
4. Statistiques par région
5. Historique des changements

## À Faire
1. Exécuter le script d'analyse pour confirmer la structure
2. Mettre à jour ce schéma avec les informations réelles
3. Créer les tables dans la base de données
4. Implémenter le parsing des données
