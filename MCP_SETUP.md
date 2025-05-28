# MCP Setup - Model Context Protocol pro vývoj

## Přehled MCP serverů pro projekt

### 1. Filesystem MCP Server
**Účel**: Přístup k souborům mezi WSL Ubuntu a Windows
**Instalace**:
```bash
npm install -g @modelcontextprotocol/server-filesystem
```

**Konfigurace** (claude_desktop_config.json):
```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/root/vyvoj_sw/electron_app"],
    "env": {}
  }
}
```

**Použití**:
- Čtení/zápis souborů projektu
- Přístup k legacy kódu
- Správa templates

### 2. Git MCP Server
**Účel**: Verzování kódu, správa commitu
**Instalace**:
```bash
npm install -g @modelcontextprotocol/server-git
```

**Konfigurace**:
```json
{
  "git": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-git", "--repository", "/root/vyvoj_sw/electron_app"],
    "env": {}
  }
}
```

**Použití**:
- Git operace (status, diff, commit)
- Branch management
- Historie změn

### 3. Context7 MCP Server
**Účel**: Aktuální dokumentace knihoven
**Instalace**:
```bash
npm install -g context7
```

**Konfigurace**:
```json
{
  "context7": {
    "command": "context7",
    "args": [],
    "env": {
      "DEFAULT_MINIMUM_TOKENS": "10000"
    }
  }
}
```

**Klíčové knihovny pro projekt**:
- `electron` - Electron framework docs
- `flask` - Python REST API
- `pandas` - Data processing
- `xlwings` - Excel automation
- `openpyxl` - Excel file handling
- `reportlab` - PDF generation

### 4. Fetch MCP Server
**Účel**: HTTP requesty, API testování
**Instalace**:
```bash
npm install -g @modelcontextprotocol/server-fetch
```

**Konfigurace**:
```json
{
  "fetch": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-fetch"],
    "env": {}
  }
}
```

**Použití**:
- Testování Flask API endpoints
- Stahování dokumentace
- GitHub API pro plakat generator reference

## Kompletní konfigurace

### Windows cesta ke konfiguraci:
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Finální claude_desktop_config.json:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/root/vyvoj_sw/electron_app"
      ],
      "env": {}
    },
    "git": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git",
        "--repository",
        "/root/vyvoj_sw/electron_app"
      ],
      "env": {}
    },
    "context7": {
      "command": "context7",
      "args": [],
      "env": {
        "DEFAULT_MINIMUM_TOKENS": "10000"
      }
    },
    "fetch": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-fetch"
      ],
      "env": {}
    }
  }
}
```

## Instalační skript

Pro rychlou instalaci všech MCP serverů:

```bash
#!/bin/bash
# install_mcp_servers.sh

echo "Instalace MCP serverů pro Electron App projekt..."

# Filesystem server
echo "1. Instalace Filesystem MCP..."
npm install -g @modelcontextprotocol/server-filesystem

# Git server
echo "2. Instalace Git MCP..."
npm install -g @modelcontextprotocol/server-git

# Context7
echo "3. Instalace Context7..."
npm install -g context7

# Fetch server
echo "4. Instalace Fetch MCP..."
npm install -g @modelcontextprotocol/server-fetch

echo "✅ Instalace dokončena!"
echo "Nezapomeňte nakonfigurovat claude_desktop_config.json"
```

## Použití v Claude Code

### Příklady příkazů:

1. **Práce se soubory**:
   ```
   "Přečti soubor legacy_code/inv_vzd_copy.py"
   "Vytvoř nový soubor src/python/tools/inv_vzd_processor.py"
   ```

2. **Git operace**:
   ```
   "Zobraz git status"
   "Commitni změny s popisem 'Refactor inv_vzd processor'"
   ```

3. **Dokumentace**:
   ```
   "Ukaž mi dokumentaci k xlwings"
   "Jak používat Flask CORS?"
   ```

4. **API testování**:
   ```
   "Otestuj endpoint POST /api/process/inv-vzd"
   ```

## Troubleshooting

### Problém: MCP server se nespustí
**Řešení**:
1. Zkontrolujte instalaci: `npm list -g`
2. Restartujte Claude Desktop
3. Zkontrolujte cesty v konfiguraci

### Problém: Permission denied v WSL
**Řešení**:
```bash
# Nastavit správná práva
sudo chown -R $USER:$USER /root/vyvoj_sw/electron_app
```

### Problém: Context7 nenachází dokumentaci
**Řešení**:
- Zkontrolujte název knihovny
- Zvyšte DEFAULT_MINIMUM_TOKENS
- Použijte alternativní názvy (např. "pandas python" místo jen "pandas")

## Best Practices

1. **Verzování**: Vždy používejte Git MCP pro commity
2. **Dokumentace**: Před použitím nové knihovny zkontrolujte Context7
3. **Testování**: Použijte Fetch MCP pro API testy
4. **Soubory**: Preferujte Filesystem MCP před manuálním kopírováním

## Rozšíření (volitelné)

### Python MCP Server
Pro přímé spouštění Python kódu:
```bash
npm install -g @modelcontextprotocol/server-python
```

### Database MCP
Pokud budete potřebovat databázi:
```bash
npm install -g @modelcontextprotocol/server-sqlite
```