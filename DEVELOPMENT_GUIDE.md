# Průvodce vývojem - Electron App

## Vývojové prostředí

### Požadavky
- **OS**: Windows 10/11 s WSL2 Ubuntu
- **Node.js**: v18+ (pro Electron)
- **Python**: 3.9+ (pro backend)
- **MS Office**: Excel nainstalovaný (pro xlwings)
- **Claude Code**: Hlavní vývojový nástroj

### Struktura vývojového prostředí
```
Windows Host:
- MS Office (Excel)
- Testování finální aplikace
- Přístup k síťovým diskům

WSL Ubuntu (/root/vyvoj_sw/electron_app/):
- Hlavní vývoj
- Git repository
- Node.js/Python development
```

## Fáze vývoje

### 1. Příprava prostředí

#### Instalace závislostí (WSL Ubuntu)
```bash
# Node.js a npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Python a pip
sudo apt-get install python3 python3-pip python3-venv

# Vývojové nástroje
sudo apt-get install build-essential
```

#### Vytvoření projektové struktury
```bash
cd /root/vyvoj_sw/electron_app
mkdir -p src/{electron,python} docs tests dist
mkdir -p src/electron/{main,renderer,assets}
mkdir -p src/python/{tools,templates,api}
```

#### Inicializace projektu
```bash
# Electron projekt
npm init -y
npm install --save-dev electron electron-forge
npm install express cors

# Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors pandas openpyxl xlwings requests
```

### 2. Backend development (Python)

#### Struktura Python backendu
```python
# src/python/server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Import nástrojů
from tools.inv_vzd_processor import InvVzdProcessor
from tools.zor_spec_processor import ZorSpecProcessor
from tools.plakat_generator import PlakatGenerator

app = Flask(__name__)
CORS(app)

# API endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/process/inv-vzd', methods=['POST'])
def process_inv_vzd():
    # Implementace
    pass

@app.route('/api/process/zor-spec', methods=['POST'])
def process_zor_spec():
    # Implementace
    pass

@app.route('/api/generate/plakat', methods=['POST'])
def generate_plakat():
    # Implementace
    pass

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
```

#### Refaktoring legacy kódu
1. **Odstranění GUI závislostí**
   - PySimpleGUI → REST API
   - Tkinter dialogy → JSON responses

2. **Modularizace**
   - Rozdělení monolitických skriptů
   - Vytvoření tříd pro každý nástroj
   - Oddělení business logiky od I/O

3. **Error handling**
   ```python
   try:
       result = process_excel(file_path)
       return {"status": "success", "data": result}
   except Exception as e:
       return {"status": "error", "message": str(e)}
   ```

### 3. Frontend development (Electron)

#### Hlavní proces
```javascript
// src/electron/main.js
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    mainWindow.loadFile('src/electron/renderer/index.html');
}

function startPythonServer() {
    pythonProcess = spawn('python', 
        ['src/python/server.py'],
        { cwd: process.cwd() }
    );
    
    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python: ${data}`);
    });
}

app.whenReady().then(() => {
    startPythonServer();
    createWindow();
});
```

#### UI komponenty
```html
<!-- src/electron/renderer/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Zpracování projektové dokumentace</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="app-container">
        <nav class="sidebar">
            <div class="nav-item" data-tool="inv-vzd">
                <i class="icon">📝</i>
                <span>Inovativní vzdělávání</span>
            </div>
            <div class="nav-item" data-tool="zor-spec">
                <i class="icon">📊</i>
                <span>Speciální data</span>
            </div>
            <div class="nav-item" data-tool="plakat">
                <i class="icon">🖼️</i>
                <span>Generátor plakátů</span>
            </div>
        </nav>
        
        <main class="content">
            <!-- Dynamický obsah -->
        </main>
    </div>
    
    <script src="renderer.js"></script>
</body>
</html>
```

### 4. Integrace a komunikace

#### API komunikace
```javascript
// src/electron/renderer/api.js
class APIClient {
    constructor() {
        this.baseURL = 'http://localhost:5000/api';
    }
    
    async processInvVzd(files, options) {
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));
        formData.append('options', JSON.stringify(options));
        
        const response = await fetch(`${this.baseURL}/process/inv-vzd`, {
            method: 'POST',
            body: formData
        });
        
        return response.json();
    }
}
```

### 5. Build a distribuce

#### Konfigurace Electron Forge
```javascript
// forge.config.js
module.exports = {
    packagerConfig: {
        name: 'Projektová dokumentace',
        icon: './assets/icon',
        extraResource: ['./dist-python']
    },
    makers: [{
        name: '@electron-forge/maker-squirrel',
        config: {
            name: 'ProjektovaDokumentace',
            setupIcon: './assets/icon.ico'
        }
    }]
};
```

#### Build proces
```bash
# 1. Build Python části
pyinstaller --onefile --windowed \
    --add-data "templates:templates" \
    src/python/server.py

# 2. Build Electron aplikace
npm run make

# 3. Výsledný instalátor
# dist/ProjektovaDokumentace-Setup.exe
```

## Best practices

### 1. Verzování
- Semantic versioning (1.0.0)
- Git flow (main, develop, feature branches)
- Tagy pro release verze

### 2. Logování
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 3. Error handling
- Vždy zachytávat a logovat chyby
- Uživatelsky přívětivé error messages
- Fallback mechanismy

### 4. Testování
- Unit testy pro Python logiku
- E2E testy pro Electron UI
- Testování s reálnými daty

## Časté problémy a řešení

### xlwings na WSL
- xlwings funguje pouze na Windows
- Řešení: Remote execution přes SSH nebo dual development

### CORS problémy
- Správně nastavit CORS v Flask
- Electron security policies

### Path problémy Windows/Linux
```python
import os
from pathlib import Path

# Cross-platform paths
file_path = Path(file_path).resolve()
```

## Debugging

### Python backend
```bash
# Spustit server v debug módu
python src/python/server.py

# Sledovat logy
tail -f app.log
```

### Electron frontend
- Chrome DevTools (Ctrl+Shift+I)
- Electron DevTools Extension
- Console.log debugging

## Příkazy pro vývoj

```bash
# Spustit vývojový server
npm run dev

# Spustit Python server
python src/python/server.py

# Build aplikace
npm run build

# Vytvořit instalátor
npm run make

# Spustit testy
npm test
pytest tests/
```