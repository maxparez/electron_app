# 📦 Nástroje OP JAK – Instalace pro Windows

Tato větev obsahuje minimální sadu souborů pro instalaci a aktualizace aplikace na Windows PC.

## 🚀 Rychlá instalace

### Pro koncové uživatele:

1. **Stáhněte instalátor** z [GitHub Releases](https://github.com/maxparez/electron_app/releases/latest)
2. **Spusťte** `install.bat` dvojklikem
3. **Hotovo** – aplikace se nainstaluje do `C:\OPJAK\electron_app`

Instalační i aktualizační skripty standardně pracují s větví `windows-install`, takže se na počítače kolegů nestahují vývojářské soubory, testy ani interní dokumentace. Pro řízené testování lze stejným mechanismem přepnout instalaci na kanál `windows-install-test`.

📖 **Podrobný návod:** [Instalační dokumentace](docs/windows_install.html)

## 📋 Předpoklady

Před instalací si připravte:

- **Python 3.11-3.13** (64-bit) – [python.org](https://www.python.org/downloads/)
- **Node.js 18+** – [nodejs.org](https://nodejs.org/)
- **Git for Windows** – [git-scm.com](https://git-scm.com/download/win)
- **Microsoft Office** (2019+ nebo Microsoft 365)
- **VC++ Redistributable 2015-2022** – [Stáhnout](https://aka.ms/vs/17/release/vc_redist.x64.exe)

⚠️ **Důležité:** Při instalaci Pythonu zaškrtněte "Add Python to PATH"!

## 📁 Struktura větve

Tato větev obsahuje pouze produkční soubory:

```
windows-install/
├── src/                    # Zdrojový kód
│   ├── electron/          # Frontend (Electron)
│   └── python/            # Backend (Flask)
├── templates/             # Excel šablony
├── config/                # Konfigurace
├── install.bat            # Instalační skript
├── update.bat             # Aktualizační skript
├── start-app.bat          # Spouštěcí skript
├── package.json           # Node.js závislosti
└── requirements-windows.txt  # Python závislosti
```

## 🔄 Aktualizace

Po instalaci najdete ve složce aplikace `update.bat`:

```cmd
cd C:\OPJAK\electron_app
update.bat
```

Skript načte cílovou větev z `channel-config.json`, stáhne poslední změny a případně doinstaluje Python a Node.js závislosti.

### Testovací kanál

Jednorázové přepnutí existující instalace na test kanál:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\update_windows.ps1 -Branch windows-install-test
```

Další běžné aktualizace už stačí spouštět přes:

```cmd
update-windows.bat
```

Návrat zpět na stable:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\update_windows.ps1 -Branch windows-install
```

Každá aktualizace ukládá transcript do `logs\update\` a test kanál navíc zapíná detailnější launch logging přes `logs\launcher\`.

## 🛠️ Pro vývojáře

**Tato větev není určena pro vývoj!**

Pro vývoj použijte větev `feature/next-phase` nebo `main`.

Synchronizace produkčních souborů do této větve:

```bash
# Na větvi feature/next-phase nebo main
./scripts/sync-to-windows-install.sh
```

## 📞 Podpora

V případě problémů:

1. Zkontrolujte logy v `C:\OPJAK\electron_app\logs/`
2. Otevřete [issue na GitHubu](https://github.com/maxparez/electron_app/issues)
3. Kontaktujte IT podporu

## 📄 Licence

MIT License – viz hlavní větev projektu

## 🔗 Odkazy

- **Hlavní repozitář:** [github.com/maxparez/electron_app](https://github.com/maxparez/electron_app)
- **Releases:** [GitHub Releases](https://github.com/maxparez/electron_app/releases)
- **Dokumentace:** [docs/windows_install.html](docs/windows_install.html)

---

**Verze:** 1.3.0
**Poslední aktualizace:** 2026-04-20
**Autor:** Max Parez
