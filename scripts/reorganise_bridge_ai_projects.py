import os
import shutil
from pathlib import Path

base_path = Path.cwd()

# Dossiers cibles
paths = {
    "backend": base_path / "FFB_Database" / "backend",
    "data": base_path / "FFB_Database" / "data",
    "models": base_path / "FFB_Database" / "models",
    "legacy": base_path / "legacy"
}

# Fichiers à déplacer
moves = {
    "backend": ["scraper.py", "run_scraper.sh", "scripts", "prisma", "schema.sql"],
    "data": ["FFB_Scraped_Data"],
    "models": ["schema_diagram.mmd", "erDiagram"],
    "legacy": [
        "Supabase",
        "cursor_checking_if_you_re_there.md",
        "FFB_Database_Project_Draft",
        "Scrapping_Detailled.txt",
        "PROJECT_OVERVIEW.md",
        "mon-projet-supabase",
        "ffb-backend"
    ]
}

def safe_move(src_name, dest_dir):
    src = base_path / src_name
    dest = dest_dir / src.name
    if src.exists():
        print(f"🔁 Déplacement de {src_name} → {dest}")
        shutil.move(str(src), str(dest))
    else:
        print(f"⚠️  {src_name} non trouvé, ignoré.")

def main():
    print(f"📁 Réorganisation dans : {base_path}\n")
    # Création des dossiers
    for key, path in paths.items():
        path.mkdir(parents=True, exist_ok=True)

    # Déplacement
    for key, items in moves.items():
        for item in items:
            safe_move(item, paths[key])

    print("\n✅ Réorganisation terminée.")

if __name__ == "__main__":
    main()
