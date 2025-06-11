# 📋 Instalační příručka - Nástroje pro ŠI a ŠII OP JAK

## 🚀 Rychlý start

### 1. Instalace základních programů (jednou)

Stáhněte a nainstalujte:

1. **Python 3.13** 
   - 🔗 https://www.python.org/downloads/
   - ⚠️ **DŮLEŽITÉ**: Při instalaci zaškrtněte "Add Python to PATH"

2. **Node.js LTS** (doporučená verze)
   - 🔗 https://nodejs.org/

3. **Git** (doporučeno pro snadné aktualizace)
   - 🔗 https://git-scm.com/download/win
   - Výchozí nastavení stačí

### 2. Stažení a instalace aplikace

#### Varianta A - S Gitem (doporučeno):
```cmd
git clone -b feature/next-phase https://github.com/maxparez/electron_app.git
cd electron_app
install-windows.bat
```

**Poznámka:** Po dokončení testování bude vše v hlavní větvi a použijete:
```cmd
git clone https://github.com/maxparez/electron_app.git
```

#### Varianta B - Bez Gitu:
1. Stáhněte ZIP z: https://github.com/maxparez/electron_app
2. Rozbalte do složky (např. `C:\electron_app`)
3. Otevřete složku a spusťte `install-windows.bat`

### 3. Spuštění aplikace

- **Dvojklik na zástupce** "Nástroje OP JAK" na ploše
- Nebo spusťte `start-app.bat` ze složky aplikace

## 🔄 Aktualizace

### S Gitem:
```cmd
update-windows.bat
```

### Bez Gitu:
1. Stáhněte novou verzi ZIP
2. Přepište soubory (zachovejte složku `venv`)
3. Spusťte `update-windows.bat`

## ❓ Řešení problémů

### "Python není nainstalován"
- Zkontrolujte, že máte Python 3.13 (ne 3.12 nebo 3.14)
- Otevřete CMD a napište: `python --version`
- Pokud nefunguje, přeinstalujte Python a zaškrtněte "Add to PATH"

### "pip install selhalo"
- Zkontrolujte internetové připojení
- Zkuste vypnout antivirus dočasně
- Spusťte jako administrátor

### "Aplikace se nespustí"
1. Zkontrolujte, že jste spustili `install-windows.bat`
2. Podívejte se do složky `logs` na chybové hlášky
3. Zkuste znovu spustit instalaci

## 📞 Podpora

Pokud máte problém:
1. Podívejte se do `logs\electron.log`
2. Zavolejte kolegovi, který s instalací pomáhal
3. Vytvořte issue na GitHubu

## 💡 Tipy

- **První spuštění** může trvat déle (až 30 sekund)
- **Nechte aplikaci běžet** - nezavírejte černé okno na pozadí
- **Pravidelně aktualizujte** pro nové funkce a opravy

---
*Verze dokumentace: 1.0 (leden 2025)*