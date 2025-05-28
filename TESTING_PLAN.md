# Plán testování - Electron App

## Přehled testovací strategie

### Úrovně testování
1. **Unit testy** - Python business logika
2. **Integrační testy** - API komunikace
3. **E2E testy** - Kompletní user flow
4. **Manuální testy** - UI/UX, Excel výstupy

### Testovací prostředí
- **Vývojové**: WSL Ubuntu
- **Testovací**: Windows 10/11 s MS Office
- **Data**: Anonymizovaná testovací data

## 1. Unit testy (Python)

### Framework: pytest

#### Instalace
```bash
pip install pytest pytest-cov pytest-mock
```

#### Struktura testů
```
tests/
├── python/
│   ├── test_inv_vzd_processor.py
│   ├── test_zor_spec_processor.py
│   ├── test_plakat_generator.py
│   └── test_utils.py
├── fixtures/
│   ├── test_data/
│   └── expected_outputs/
└── conftest.py
```

#### Příklad testu
```python
# tests/python/test_inv_vzd_processor.py
import pytest
from src.python.tools.inv_vzd_processor import InvVzdProcessor

class TestInvVzdProcessor:
    @pytest.fixture
    def processor(self):
        return InvVzdProcessor()
    
    def test_detect_version_16h(self, processor):
        """Test detekce 16 hodinové verze"""
        result = processor.detect_version("fixtures/16h_test.xlsx")
        assert result == "16h"
    
    def test_process_attendance_data(self, processor):
        """Test zpracování docházky"""
        input_file = "fixtures/test_attendance.xlsx"
        template = "fixtures/test_template.xlsx"
        
        result = processor.process(input_file, template)
        assert result['status'] == 'success'
        assert 'output_file' in result
```

#### Spuštění testů
```bash
# Všechny testy
pytest

# S coverage
pytest --cov=src/python --cov-report=html

# Konkrétní test
pytest tests/python/test_inv_vzd_processor.py::test_detect_version_16h
```

## 2. Integrační testy

### API testy (Python)

```python
# tests/integration/test_api.py
import pytest
import json
from src.python.server import app

class TestAPI:
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        return app.test_client()
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'
    
    def test_process_inv_vzd(self, client):
        """Test zpracování Inv Vzd"""
        with open('fixtures/test_file.xlsx', 'rb') as f:
            data = {
                'file': (f, 'test_file.xlsx'),
                'template': 'default'
            }
            response = client.post(
                '/api/process/inv-vzd',
                data=data,
                content_type='multipart/form-data'
            )
        
        assert response.status_code == 200
        assert 'output_files' in response.json
```

### Frontend-Backend komunikace (Jest)

```javascript
// tests/integration/api.test.js
const axios = require('axios');
const { spawn } = require('child_process');

describe('API Integration', () => {
    let pythonProcess;
    
    beforeAll((done) => {
        // Spustit Python server
        pythonProcess = spawn('python', ['src/python/server.py']);
        setTimeout(done, 2000); // Počkat na start
    });
    
    afterAll(() => {
        pythonProcess.kill();
    });
    
    test('Health check', async () => {
        const response = await axios.get('http://localhost:5000/api/health');
        expect(response.status).toBe(200);
        expect(response.data.status).toBe('healthy');
    });
});
```

## 3. E2E testy (Electron)

### Framework: Playwright/Spectron

```javascript
// tests/e2e/app.test.js
const { _electron: electron } = require('playwright');
const path = require('path');

describe('Electron App E2E', () => {
    let app;
    
    beforeEach(async () => {
        app = await electron.launch({
            args: [path.join(__dirname, '../../src/electron/main.js')]
        });
    });
    
    afterEach(async () => {
        await app.close();
    });
    
    test('App starts successfully', async () => {
        const window = await app.firstWindow();
        const title = await window.title();
        expect(title).toBe('Zpracování projektové dokumentace');
    });
    
    test('Navigation works', async () => {
        const window = await app.firstWindow();
        
        // Klik na Inv Vzd
        await window.click('[data-tool="inv-vzd"]');
        const invVzdVisible = await window.isVisible('#inv-vzd-panel');
        expect(invVzdVisible).toBe(true);
    });
    
    test('File processing workflow', async () => {
        const window = await app.firstWindow();
        
        // 1. Vybrat nástroj
        await window.click('[data-tool="zor-spec"]');
        
        // 2. Nahrát soubory
        const fileInput = await window.$('input[type="file"]');
        await fileInput.setInputFiles(['tests/fixtures/test_file.xlsx']);
        
        // 3. Spustit zpracování
        await window.click('#process-button');
        
        // 4. Čekat na výsledek
        await window.waitForSelector('.success-message', {
            timeout: 30000
        });
        
        const message = await window.textContent('.success-message');
        expect(message).toContain('Zpracování dokončeno');
    });
});
```

## 4. Manuální testovací scénáře

### Testovací checklist

#### A. Instalace a spuštění
- [ ] Instalátor se spustí bez chyb
- [ ] Aplikace se nainstaluje do správné složky
- [ ] Ikona se objeví na ploše
- [ ] Aplikace se spustí dvojklikem
- [ ] Žádné antivirus varování

#### B. UI/UX testy
- [ ] Navigace mezi nástroji funguje
- [ ] Všechny tlačítka jsou responzivní
- [ ] Progress bar zobrazuje průběh
- [ ] Error messages jsou srozumitelné
- [ ] Aplikace reaguje na resize okna

#### C. Funkční testy - Inv Vzd Copy
- [ ] Detekce 16h verze funguje
- [ ] Detekce 32h verze funguje
- [ ] Šablona se správně vyplní
- [ ] Formátování zůstává zachováno
- [ ] Makra v Excelu fungují
- [ ] Výstupní soubor má správný název

#### D. Funkční testy - Zor Spec Dat
- [ ] Zpracování více souborů najednou
- [ ] HTML report se generuje správně
- [ ] Seznam žáků je kompletní
- [ ] Agregace dat je správná
- [ ] Šablona se správně používá

#### E. Funkční testy - Plakát Generator
- [ ] Import dat z Excelu funguje
- [ ] PDF se generuje správně
- [ ] Orientace (portrait/landscape) funguje
- [ ] Společný text se aplikuje
- [ ] Více plakátů v jednom PDF

#### F. Edge cases
- [ ] Prázdný soubor
- [ ] Poškozený Excel soubor
- [ ] Velmi velký soubor (1000+ řádků)
- [ ] Soubor s chybějícími daty
- [ ] Neplatný formát souboru

## 5. Performance testy

### Měření rychlosti
```python
# tests/performance/test_performance.py
import time
import pytest
from src.python.tools.zor_spec_processor import ZorSpecProcessor

def test_large_file_processing():
    """Test zpracování velkého souboru"""
    processor = ZorSpecProcessor()
    large_file = "fixtures/large_test_file.xlsx"  # 1000+ řádků
    
    start_time = time.time()
    result = processor.process([large_file], "template.xlsx")
    end_time = time.time()
    
    processing_time = end_time - start_time
    assert processing_time < 30  # Max 30 sekund
    assert result['status'] == 'success'
```

### Memory profiling
```bash
# Měření paměti
python -m memory_profiler tests/memory_test.py
```

## 6. Testovací data

### Struktura testovacích dat
```
tests/fixtures/
├── test_data/
│   ├── 16h_simple.xlsx
│   ├── 16h_complex.xlsx
│   ├── 32h_simple.xlsx
│   ├── 32h_complex.xlsx
│   ├── template_ms.xlsx
│   ├── template_zs.xlsx
│   └── projects_list.xlsx
├── expected_outputs/
│   ├── expected_16h_output.xlsx
│   ├── expected_report.html
│   └── expected_plakat.pdf
└── edge_cases/
    ├── empty_file.xlsx
    ├── corrupted.xlsx
    └── huge_file.xlsx
```

### Anonymizace dat
```python
# scripts/anonymize_data.py
import pandas as pd
import random
import string

def anonymize_excel(input_file, output_file):
    """Anonymizuje osobní údaje v Excel souboru"""
    df = pd.read_excel(input_file)
    
    # Náhrada jmen
    if 'Jméno' in df.columns:
        df['Jméno'] = ['Student' + str(i) for i in range(len(df))]
    
    # Náhrada příjmení
    if 'Příjmení' in df.columns:
        df['Příjmení'] = ['Test' + str(i) for i in range(len(df))]
    
    df.to_excel(output_file, index=False)
```

## 7. CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test-python:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: pytest --cov=src/python
      
  test-electron:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm install
      - name: Run tests
        run: npm test
```

## 8. Reporting

### Test Coverage Report
- Python: HTML report v `htmlcov/`
- JavaScript: Coverage report v `coverage/`
- Kombinovaný report v `docs/test-coverage.md`

### Bug tracking
- GitHub Issues s labely:
  - `bug`
  - `priority-high`
  - `tool-inv-vzd`
  - `tool-zor-spec`
  - `tool-plakat`

## 9. Akceptační kritéria

### Před release
- [ ] Všechny unit testy projdou
- [ ] Integrační testy projdou
- [ ] E2E testy projdou
- [ ] Manuální testy dokončeny
- [ ] Code coverage > 80%
- [ ] Žádné kritické bugy
- [ ] Performance testy splněny
- [ ] Testováno na Windows 10 a 11

## 10. Kontinuální testování

### Denní
- Automatické spuštění unit testů při commitu

### Týdenní
- Kompletní E2E test suite
- Performance testy

### Před release
- Kompletní manuální testování
- Testování na čistých Windows instalacích
- User Acceptance Testing s kolegy