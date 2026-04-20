# Windows-Install Workflow

## Kontext
- Vývoj probíhá v běžných vývojových větvích jako `main` nebo `feature/*`.
- Větev `windows-install` je curated distribuční větev pro kolegy.
- Kolegové instalují i aktualizují pouze z `windows-install`, aby se jim nestahovaly testy, interní dokumentace a další vývojářské soubory.

## Cíl
Po dokončení změn synchronizovat jen nutný runtime obsah do `windows-install` a ověřit, že first-time install i `update-windows.bat` používají stejný zdroj.

## Doporučený postup

### 1. Dokončete změny ve vývojové větvi
```bash
git checkout feature/my-change
# ... implementace, testy, ověření ...
git add -A
git commit -m "[fix-XXX] Popis změny"
git push origin feature/my-change
```

### 2. Synchronizujte `windows-install`
Použijte jeden z připravených skriptů:

```bash
./scripts/sync_windows_branch.sh
```

nebo

```bash
./scripts/sync-to-windows-install.sh
```

Oba workflow mají za cíl zkopírovat jen whitelistovaný/minimální obsah do `windows-install`.

### 3. Zkontrolujte, co se do větve dostalo
- instalační skripty: `install.bat`, `install-windows-standalone.bat`, `update.bat`, `update-windows.bat`
- runtime soubory: `src/`, `package*.json`, `requirements-windows.txt`, `forge.config.js`
- uživatelská dokumentace: `README.md` nebo `README-windows-install.md`

Do `windows-install` nepatří `tests/`, `legacy_code/`, interní plánovací dokumentace ani pomocné vývojářské skripty.

### 4. Ověřte instalační a update flow
- čistá instalace z `install.bat` nebo `install-windows-standalone.bat`
- následný update přes `update-windows.bat`
- spuštění aplikace přes `start-app.bat`
- základní smoke test na Windows s Excelem

## Klíčová pravidla
1. `windows-install` je jediná větev pro kolegy.
2. First-time install i update musí používat stejnou větev: `windows-install`.
3. Dokumentace pro kolegy nesmí odkazovat na `production`, `main` ani `feature/*` jako instalační zdroj.
4. Pokud se změní instalační nebo update skript, otestujte obě cesty: nová instalace i aktualizace existující instalace.

## Poznámka k historii
Starší dokumentace pracovala s větví `production`. Aktuální workflow tuto roli nahrazuje větví `windows-install`, která slouží jako minimální distribuční snapshot pro Windows počítače kolegů.
