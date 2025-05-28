# Localization Guide - Czech UI for Electron App

## Pravidla lokalizace

### Základní princip
- **Veškerý kód**: Anglicky (názvy funkcí, proměnné, komentáře)
- **UI pro uživatele**: Česky (tlačítka, zprávy, nápověda)

## Implementace lokalizace

### 1. Struktura lokalizačních souborů

```
src/
├── electron/
│   └── locales/
│       └── cs.json    # České texty
└── python/
    └── locales/
        └── cs.py      # České texty pro Python
```

### 2. Frontend lokalizace (Electron)

#### Lokalizační soubor
```json
// src/electron/locales/cs.json
{
  "app": {
    "title": "Zpracování projektové dokumentace",
    "version": "Verze"
  },
  "navigation": {
    "inv_vzd": "Inovativní vzdělávání",
    "zor_spec": "Speciální data",
    "plakat": "Generátor plakátů"
  },
  "common": {
    "select_files": "Vybrat soubory",
    "process": "Zpracovat",
    "cancel": "Zrušit",
    "close": "Zavřít",
    "save": "Uložit",
    "loading": "Načítání...",
    "processing": "Zpracovávám..."
  },
  "inv_vzd": {
    "title": "Zpracování docházky - Inovativní vzdělávání",
    "select_attendance": "Vyberte soubory docházky",
    "select_template": "Vyberte šablonu",
    "version_16h": "16 hodin",
    "version_32h": "32 hodin",
    "auto_detect": "Automatická detekce verze"
  },
  "zor_spec": {
    "title": "Zpracování speciálních dat",
    "select_data": "Vyberte datové soubory",
    "generate_report": "Generovat report",
    "unique_students": "Seznam unikátních žáků"
  },
  "plakat": {
    "title": "Generátor plakátů",
    "paste_data": "Vložte data z Excelu",
    "orientation": "Orientace",
    "portrait": "Na výšku",
    "landscape": "Na šířku",
    "common_text": "Společný text",
    "generate_pdf": "Generovat PDF"
  },
  "messages": {
    "success": "Úspěšně dokončeno",
    "error": "Nastala chyba",
    "file_not_found": "Soubor nebyl nalezen",
    "invalid_format": "Neplatný formát souboru",
    "processing_complete": "Zpracování dokončeno",
    "select_file_first": "Nejprve vyberte soubor",
    "saved_to": "Uloženo do: {path}"
  },
  "errors": {
    "connection_failed": "Nepodařilo se připojit k serveru",
    "invalid_template": "Neplatná šablona",
    "excel_required": "Tato funkce vyžaduje MS Excel",
    "processing_failed": "Zpracování selhalo: {error}"
  }
}
```

#### Použití v kódu
```javascript
// src/electron/renderer/i18n.js
class I18n {
    constructor() {
        this.locale = 'cs';
        this.translations = require(`./locales/${this.locale}.json`);
    }
    
    t(key) {
        const keys = key.split('.');
        let value = this.translations;
        
        for (const k of keys) {
            value = value[k];
            if (!value) return key;
        }
        
        return value;
    }
    
    // For parameterized messages
    format(key, params) {
        let text = this.t(key);
        for (const [param, value] of Object.entries(params)) {
            text = text.replace(`{${param}}`, value);
        }
        return text;
    }
}

const i18n = new I18n();

// Usage in components
document.getElementById('process-btn').textContent = i18n.t('common.process');
```

### 3. Backend lokalizace (Python)

```python
# src/python/locales/cs.py
MESSAGES = {
    'processing_started': 'Zahájeno zpracování souboru: {filename}',
    'processing_completed': 'Zpracování dokončeno',
    'error_file_not_found': 'Soubor nenalezen: {filename}',
    'error_invalid_format': 'Neplatný formát souboru',
    'validation_error': 'Chyba validace: {details}',
    'saving_output': 'Ukládám výstup do: {path}',
    'report_generated': 'Report vygenerován',
    'students_found': 'Nalezeno {count} unikátních žáků',
    'processing_sheet': 'Zpracovávám list: {sheet_name}',
    'version_detected': 'Detekována verze: {version} hodin'
}

def get_message(key, **kwargs):
    """Get localized message with parameters"""
    message = MESSAGES.get(key, key)
    return message.format(**kwargs)
```

### 4. Chybové hlášky a logování

```python
# src/python/utils/logger.py
import logging
from locales.cs import get_message

class LocalizedLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        
    def info_localized(self, key, **kwargs):
        """Log info with localized message for UI"""
        message = get_message(key, **kwargs)
        self.logger.info(f"[UI] {message}")
        return {'level': 'info', 'message': message}
    
    def error_localized(self, key, **kwargs):
        """Log error with localized message for UI"""
        message = get_message(key, **kwargs)
        self.logger.error(f"[UI] {message}")
        return {'level': 'error', 'message': message}
```

### 5. API Response s lokalizací

```python
# src/python/api/responses.py
def success_response(data, message_key=None, **kwargs):
    """Create success response with optional localized message"""
    response = {
        'status': 'success',
        'data': data
    }
    
    if message_key:
        response['message'] = get_message(message_key, **kwargs)
    
    return jsonify(response)

def error_response(message_key, status_code=400, **kwargs):
    """Create error response with localized message"""
    return jsonify({
        'status': 'error',
        'message': get_message(message_key, **kwargs)
    }), status_code
```

## Glosář termínů

| Anglicky (kód) | Česky (UI) |
|----------------|------------|
| attendance | docházka |
| template | šablona |
| process | zpracovat |
| report | report/výkaz |
| student | žák |
| unique | unikátní |
| sheet | list |
| workbook | sešit |
| innovative education | inovativní vzdělávání |
| special data | speciální data |
| poster | plakát |
| orientation | orientace |
| portrait | na výšku |
| landscape | na šířku |
| generate | generovat |
| export | exportovat |
| import | importovat |
| save | uložit |
| load | načíst |
| select | vybrat |
| cancel | zrušit |
| confirm | potvrdit |
| delete | smazat |
| error | chyba |
| warning | varování |
| success | úspěch |
| failed | selhalo |
| completed | dokončeno |
| in progress | probíhá |
| ready | připraveno |

## Best Practices

1. **Konzistence**: Používejte stejné termíny napříč celou aplikací
2. **Srozumitelnost**: Vyhněte se technickému žargonu v UI
3. **Kontext**: Zprávy by měly být jasné i bez kontextu
4. **Parametry**: Používejte parametry místo konkatenace stringů
5. **Fallback**: Vždy mějte fallback pro chybějící překlady