import os
import shutil
from pathlib import Path

root = Path.cwd()
apps_dir = root / "apps"
scripts_dir = root / "scripts"

# 1. Créer les dossiers si besoin
apps_dir.mkdir(exist_ok=True)
scripts_dir.mkdir(exist_ok=True)

# 2. Déplacer FFB_Database vers apps/ffb_database
src = root / "FFB_Database"
dst = apps_dir / "ffb_database"

if src.exists() and not dst.exists():
    shutil.move(str(src), str(dst))
    print(f"✅ FFB_Database déplacé vers {dst}")
else:
    print("⚠️ Dossier déjà déplacé ou source introuvable.")

# 3. Déplacer reorganise_bridge_ai_projects.py dans scripts/
script_src = root / "reorganise_bridge_ai_projects.py"
script_dst = scripts_dir / script_src.name

if script_src.exists() and not script_dst.exists():
    shutil.move(str(script_src), str(script_dst))
    print(f"✅ Script déplacé vers {script_dst}")
else:
    print("⚠️ Script déjà déplacé ou introuvable.")