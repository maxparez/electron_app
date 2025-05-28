# Návod na instalaci MCP serverů

## 1. Instalace na Windows (Claude Desktop)

### Automatická instalace
1. Otevřete WSL Ubuntu terminal
2. Přejděte do projektové složky:
   ```bash
   cd /root/vyvoj_sw/electron_app
   ```
3. Spusťte instalační skript:
   ```bash
   ./install_mcp_servers.sh
   ```

### Manuální instalace
Pokud automatický skript nefunguje, nainstalujte každý server zvlášť:

```bash
# Filesystem server
npm install -g @modelcontextprotocol/server-filesystem

# Git server  
npm install -g @modelcontextprotocol/server-git

# Context7 (dokumentace)
npm install -g context7

# Fetch server (HTTP requesty)
npm install -g @modelcontextprotocol/server-fetch
```

## 2. Konfigurace Claude Desktop

1. Zkopírujte konfigurační soubor do Windows:
   ```bash
   cp claude_desktop_config.json /mnt/c/Users/[VAS_USERNAME]/AppData/Roaming/Claude/
   ```

2. Nebo ručně upravte soubor:
   - Otevřete: `%APPDATA%\Claude\claude_desktop_config.json`
   - Vložte obsah z `claude_desktop_config.json`

3. Restartujte Claude Desktop aplikaci

## 3. Ověření instalace

Po restartu Claude Desktop:
1. Vytvořte nový chat
2. Zadejte: "zkontroluj dostupné MCP servery"
3. Měli byste vidět nástroje začínající `mcp__`

## 4. Řešení problémů

### MCP servery se nezobrazují
- Zkontrolujte, že jsou servery nainstalovány: `npm list -g`
- Ověřte správnou cestu v konfiguraci
- Restartujte Claude Desktop

### Permission denied
```bash
sudo chown -R $USER:$USER /root/vyvoj_sw/electron_app
```

### NPM chyby
```bash
# Vyčistěte npm cache
npm cache clean --force

# Reinstalujte
./install_mcp_servers.sh
```

## 5. Použití MCP serverů

Po úspěšné instalaci budete moci používat:
- `mcp__filesystem` - práce se soubory
- `mcp__git` - git operace
- `mcp__context7` - dokumentace knihoven
- `mcp__fetch` - HTTP requesty

Příklad použití:
```
"Použij mcp__filesystem k přečtení souboru legacy_code/inv_vzd_copy.py"
"Použij mcp__git pro zobrazení git status"
```