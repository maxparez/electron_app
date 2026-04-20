# Technická architektura - Electron App

## Přehled architektury

```
┌─────────────────────────────────────────────────────────────┐
│                         Uživatel                            │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Electron Frontend                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Inv Vzd   │  │  Zor Spec   │  │   Plakát    │        │
│  │     UI      │  │     UI      │  │     UI      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐                                        │
│  │    DVPP     │                                        │
│  │     UI      │                                        │
│  └─────────────┘                                        │
│                                                             │
│  ┌─────────────────────────────────────────────────┐      │
│  │            Renderer Process (UI)                 │      │
│  │  - HTML/CSS/JS                                  │      │
│  │  - File selection                               │      │
│  │  - Progress tracking                            │      │
│  └─────────────────────────────────────────────────┘      │
│                                                             │
│  ┌─────────────────────────────────────────────────┐      │
│  │             Main Process                         │      │
│  │  - Window management                            │      │
│  │  - Python process management                    │      │
│  │  - IPC communication                            │      │
│  └─────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                               │
                               │ HTTP (localhost:5000)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     Python Backend                           │
│  ┌─────────────────────────────────────────────────┐      │
│  │              Flask REST API                      │      │
│  │  - CORS enabled                                  │      │
│  │  - JSON responses                                │      │
│  │  - File upload handling                          │      │
│  └─────────────────────────────────────────────────┘      │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  InvVzd     │  │  ZorSpec    │  │  Plakat     │        │
│  │  Processor  │  │  Processor  │  │  Generator  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐                                        │
│  │    DVPP     │                                        │
│  │  Processor  │                                        │
│  └─────────────┘                                        │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────────────────────────────────────────┐      │
│  │           Shared Libraries                       │      │
│  │  - pandas (data processing)                     │      │
│  │  - xlwings (Excel manipulation)                 │      │
│  │  - openpyxl (Excel read/write)                  │      │
│  │  - reportlab (PDF generation)                   │      │
│  └─────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      File System                             │
│  - Input Excel files                                        │
│  - Template files                                           │
│  - Output Excel/PDF/HTML files                              │
└─────────────────────────────────────────────────────────────┘
```

## Komponenty

### 1. Electron Frontend

#### Main Process
- **Zodpovědnost**: Správa aplikačního okna, lifecycle
- **Technologie**: Electron, Node.js
- **Klíčové soubory**:
  - `main.js` - Vstupní bod aplikace
  - `backend-manager.js` - Správa Python procesu a restartů

#### Renderer Process
- **Zodpovědnost**: Uživatelské rozhraní
- **Technologie**: HTML5, CSS3, JavaScript (ES6+)
- **Komponenty**:
  - Navigation sidebar
  - Tool panels
  - File picker
  - Progress indicators
  - Result viewers

#### IPC Communication
```javascript
// Renderer → Main
ipcRenderer.send('process-files', {
    tool: 'inv-vzd',
    files: selectedFiles,
    options: userOptions
});

// Main → Renderer
mainWindow.webContents.send('process-complete', {
    status: 'success',
    results: processedFiles
});
```

### 2. Python Backend

#### REST API Endpoints

| Endpoint | Method | Popis |
|----------|---------|-------|
| `/api/health` | GET | Health check |
| `/api/process/inv-vzd` | POST | Zpracování Inv Vzd |
| `/api/process/zor-spec` | POST | Zpracování Zor Spec |
| `/api/process/plakat` | POST | Generování plakátů |
| `/api/scan/dvpp-directory` | POST | Vyhledání DVPP workbooků |
| `/api/process/dvpp-report` | POST | Generování DVPP HTML reportu |

#### Request/Response Format
```json
// Request
{
    "files": ["path/to/file1.xlsx", "path/to/file2.xlsx"],
    "template": "path/to/template.xlsx",
    "options": {
        "outputFormat": "excel",
        "generateReport": true
    }
}

// Response
{
    "status": "success",
    "taskId": "uuid-1234",
    "results": {
        "processedFiles": ["output1.xlsx", "output2.xlsx"],
        "report": "report.html",
        "summary": {
            "totalProcessed": 50,
            "errors": 0
        }
    }
}
```

### 3. Processing Modules

#### InvVzd Processor
```python
class InvVzdProcessor:
    def __init__(self):
        self.xlwings_app = None
        
    def process(self, input_files, template_path):
        # 1. Detekce verze (16/32 hodin)
        # 2. Načtení šablony
        # 3. Zpracování dat
        # 4. Uložení výstupu
        pass
```

#### ZorSpec Processor
```python
class ZorSpecProcessor:
    def __init__(self):
        self.unique_students = set()
        
    def process(self, attendance_files, template_path):
        # 1. Iterace přes soubory
        # 2. Zpracování docházky
        # 3. Generování reportu
        # 4. Export seznamu žáků
        pass
```

#### Plakat Generator
```python
class PlakatGenerator:
    def __init__(self):
        self.pdf_settings = {}
        
    def generate(self, project_list, orientation, common_text):
        # 1. Parsování seznamu projektů
        # 2. Generování PDF pro každý projekt
        # 3. Kompilace do jednoho PDF
        pass
```

## Datové toky

### 1. Inv Vzd Copy workflow
```
1. Uživatel vybere soubory docházky
2. Frontend → POST /api/process/inv-vzd
3. Backend:
   - Detekuje verzi (16/32h)
   - Otevře Excel přes xlwings
   - Zpracuje data
   - Uloží výstupy
4. Backend → Response s cestami k souborům
5. Frontend zobrazí výsledky
```

### 2. Zor Spec Dat workflow
```
1. Uživatel vybere docházky + šablonu
2. Frontend → POST /api/process/zor-spec
3. Backend:
   - Iteruje přes všechny soubory
   - Agreguje data
   - Generuje HTML report
   - Vytvoří seznam žáků
4. Backend → Response s výsledky
5. Frontend zobrazí report + možnost stažení
```

### 3. Plakát Generator workflow
```
1. Uživatel vloží seznam projektů
2. Frontend → POST /api/process/plakat
3. Backend:
   - Volá externí službu pro povinnou publicitu
   - Generuje PDF plakáty
   - Vrací PDF soubory rendereru
4. Backend → Response s PDF
5. Frontend nabídne stažení
```

### 4. DVPP report workflow
```
1. Uživatel vybere projektovou složku
2. Frontend → POST /api/scan/dvpp-directory
3. Backend:
   - Rekurzivně projde Excel workbooky
   - Vyfiltruje soubory s požadovanou DVPP strukturou
4. Frontend zobrazí nalezené workbooky a výběr
5. Frontend → POST /api/process/dvpp-report
6. Backend vytvoří HTML report přímo do projektové složky
```

## Bezpečnost

### 1. Komunikace
- Lokální komunikace Electron ↔ Flask backend běží na `127.0.0.1`, výchozí port je `5000`
- Generátor plakátů navíc komunikuje s externí službou `publicita.dotaceeu.cz`
- CORS je povoleno pro desktop aplikaci

### 2. File Access
- Lokální práce se soubory přes Electron dialogy a Python zpracování
- Validace a normalizace cest souborů včetně převodu Windows cest ve WSL scénáři
- Na Windows se při správě backendu používají i externí systémové příkazy pro ukončení procesů

### 3. Data Protection
- Žádné ukládání citlivých dat
- Temporary files mazány po zpracování
- Logs bez osobních údajů

## Škálovatelnost

### Současný stav
- Single-user desktop aplikace
- Synchronní zpracování
- Lokální soubory

### Možná rozšíření
1. **Multi-threading** pro Python zpracování
2. **Queue system** pro dlouhé úlohy
3. **Síťové úložiště** podpory
4. **Multi-user** podpora (budoucnost)

## Technické detaily

### Dependencies

#### Frontend (package.json)
```json
{
  "devDependencies": {
    "electron": "^28.0.0",
    "electron-forge": "^7.0.0"
  },
  "dependencies": {
    "axios": "^1.6.0"
  }
}
```

#### Backend (requirements.txt)
```
flask==3.0.0
flask-cors==4.0.0
pandas==2.1.0
openpyxl==3.1.0
xlwings==0.30.0
reportlab==4.0.0
requests==2.31.0
```

### Konfigurace

#### Electron
```javascript
// Hlavní okno
{
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
    }
}
```

#### Python
```python
# Konfigurace serveru
UPLOAD_FOLDER = './uploads'
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
```

## Deployment

### Build Pipeline
1. **Python bundling**: PyInstaller
2. **Electron packaging**: Electron Forge
3. **Installer creation**: Squirrel (Windows)
4. **Code signing**: Windows Authenticode

### Výsledná struktura
```
ProjektovaDokumentace.exe (150-200 MB)
├── Electron runtime
├── Python runtime (embedded)
├── Application code
└── Dependencies
```
