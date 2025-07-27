import os
import shutil

ROOT = os.getcwd()
LEGACY = os.path.join(ROOT, 'apps', 'bridge-referee-app', 'bridge-arbitrage-legacy')
TARGET = os.path.join(ROOT, 'apps', 'bridge-arbitrage')

os.makedirs(TARGET, exist_ok=True)

for item in os.listdir(LEGACY):
    if item.startswith('.'): continue
    src = os.path.join(LEGACY, item)
    dest = os.path.join(TARGET, item)
    if os.path.exists(dest):
        print(f"⚠️ {dest} already exists, skipping")
    else:
        print(f"Moving {item} to apps/bridge-arbitrage")
        shutil.move(src, dest)

print("✅ Done reorganizing bridge-arbitrage project.")