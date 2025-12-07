#!/bin/bash
# Sync production files to windows-install branch
# Spouští vývojář MANUÁLNĚ po dokončení změn
#
# Usage: ./scripts/sync-to-windows-install.sh

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Sync to windows-install branch - Developer Tool           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get current branch and commit
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_COMMIT=$(git rev-parse HEAD)
echo "📍 Current branch: $CURRENT_BRANCH"
echo "📍 Current commit: $CURRENT_COMMIT"
echo ""

# Confirm action
read -p "⚠️  This will OVERWRITE windows-install branch. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled."
    exit 1
fi

echo ""
echo "[1/7] Switching to windows-install branch..."
git checkout windows-install

echo "[2/7] Removing old files (except .git)..."
find . -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +

echo "[3/7] Extracting production files from $CURRENT_BRANCH ($CURRENT_COMMIT)..."

# Create directory structure
mkdir -p src/electron/assets
mkdir -p src/electron/locales
mkdir -p src/electron/renderer
mkdir -p src/python/tools
mkdir -p templates
mkdir -p config

# Extract files using git show
# Electron frontend files
git show "$CURRENT_COMMIT:src/electron/main.js" > src/electron/main.js
git show "$CURRENT_COMMIT:src/electron/preload.js" > src/electron/preload.js
git show "$CURRENT_COMMIT:src/electron/config.js" > src/electron/config.js
git show "$CURRENT_COMMIT:src/electron/backend-manager.js" > src/electron/backend-manager.js

# Electron assets (binary files)
git show "$CURRENT_COMMIT:src/electron/assets/icon.ico" > src/electron/assets/icon.ico
git show "$CURRENT_COMMIT:src/electron/assets/icon.png" > src/electron/assets/icon.png

# Electron locales
git show "$CURRENT_COMMIT:src/electron/locales/cs.json" > src/electron/locales/cs.json

# Electron renderer
git show "$CURRENT_COMMIT:src/electron/renderer/index.html" > src/electron/renderer/index.html
git show "$CURRENT_COMMIT:src/electron/renderer/renderer.js" > src/electron/renderer/renderer.js
git show "$CURRENT_COMMIT:src/electron/renderer/styles.css" > src/electron/renderer/styles.css
git show "$CURRENT_COMMIT:src/electron/renderer/i18n.js" > src/electron/renderer/i18n.js
git show "$CURRENT_COMMIT:src/electron/renderer/backend-monitor.js" > src/electron/renderer/backend-monitor.js

# Python backend files
git show "$CURRENT_COMMIT:src/python/server.py" > src/python/server.py
git show "$CURRENT_COMMIT:src/python/logger.py" > src/python/logger.py
git show "$CURRENT_COMMIT:src/python/tools/__init__.py" > src/python/tools/__init__.py
git show "$CURRENT_COMMIT:src/python/tools/base_tool.py" > src/python/tools/base_tool.py
git show "$CURRENT_COMMIT:src/python/tools/inv_vzd_processor.py" > src/python/tools/inv_vzd_processor.py
git show "$CURRENT_COMMIT:src/python/tools/zor_spec_dat_processor.py" > src/python/tools/zor_spec_dat_processor.py
git show "$CURRENT_COMMIT:src/python/tools/plakat_generator.py" > src/python/tools/plakat_generator.py

# Templates (Excel files - binary)
git show "$CURRENT_COMMIT:templates/template_16_hodin.xlsx" > templates/template_16_hodin.xlsx
git show "$CURRENT_COMMIT:templates/template_32_hodin.xlsx" > templates/template_32_hodin.xlsx

# Config
git show "$CURRENT_COMMIT:config/production.json" > config/production.json

# Root files
git show "$CURRENT_COMMIT:package.json" > package.json
git show "$CURRENT_COMMIT:package-lock.json" > package-lock.json
git show "$CURRENT_COMMIT:requirements-windows.txt" > requirements-windows.txt
git show "$CURRENT_COMMIT:start-app.bat" > start-app.bat
git show "$CURRENT_COMMIT:icon.ico" > icon.ico
git show "$CURRENT_COMMIT:forge.config.js" > forge.config.js

# Install/update scripts
git show "$CURRENT_COMMIT:install.bat" > install.bat
git show "$CURRENT_COMMIT:update.bat" > update.bat

# README for windows-install
git show "$CURRENT_COMMIT:README-windows-install.md" > README.md 2>/dev/null || echo "⚠️  README-windows-install.md not found, skipping"

echo "[4/7] Checking git status..."
git status --short

echo ""
echo "[5/7] Staging all changes..."
git add -A

echo "[6/7] Creating commit..."
git commit -m "[release] Sync windows artifacts from $CURRENT_COMMIT" || echo "No changes to commit"

echo "[7/7] Pushing to origin/windows-install..."
git push origin windows-install

echo ""
echo "✅ Sync completed successfully!"
echo ""
echo "📦 Windows-install branch updated with production files"
echo "🔗 Users can now install/update from GitHub"
echo ""

# Return to original branch
echo "Returning to $CURRENT_BRANCH..."
git checkout "$CURRENT_BRANCH"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                       ✅ DONE!                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
