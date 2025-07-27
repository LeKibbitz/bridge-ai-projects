import os
import shutil

# Chemin absolu vers la racine du projet
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Dossiers cibles
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
APPS_DIR = os.path.join(PROJECT_ROOT, "apps")

# Crée les dossiers s'ils n'existent pas
os.makedirs(SCRIPTS_DIR, exist_ok=True)
os.makedirs(APPS_DIR, exist_ok=True)

# Déplacement des scripts Python à la racine (hors __init__.py)
moved = False
for item in os.listdir(PROJECT_ROOT):
    item_path = os.path.join(PROJECT_ROOT, item)
    if os.path.isfile(item_path) and item.endswith(".py") and item != "__init__.py":
        dest_path = os.path.join(SCRIPTS_DIR, item)
        print(f"🔄 Déplacement de {item} vers scripts/")
        shutil.move(item_path, dest_path)
        moved = True

if not moved:
    print("✅ Aucun fichier .py à déplacer (ou déjà déplacé).")

print("📁 FFB_Database reste à la racine.")
print("📁 scripts/ contient maintenant les scripts Python.")
print("📁 apps/ est prêt pour les apps futures.")