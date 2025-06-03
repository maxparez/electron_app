# 📖 Návod na instalaci ElektronApp

**ElektronApp - Nástroje pro zpracování projektové dokumentace OP JAK**

---

## 📋 Systémové požadavky

### ✅ Co je potřeba:
- **Windows 10 nebo 11** (64-bit)
- **Microsoft Excel** (jakákoli verze 2016+)
- **Python 3.8+** nebo připojení k internetu pro automatickou instalaci
- **Alespoň 500 MB volného místa** na disku

### ⚠️ Důležité poznámky:
- Aplikace vyžaduje **Microsoft Excel** pro správnou funkci (kvůli zachování formátování)
- Antivirus může vyžadovat povolení spuštění .exe souborů
- Během instalace se připojuje k internetu pro stažení Python knihoven

---

## 🚀 Instalace - 3 jednoduché kroky

### Krok 1: Instalace hlavní aplikace

1. **Najděte soubor `ElektronApp-Setup.exe`** v distribučním balíčku
2. **Klikněte pravým tlačítkem** → "Spustit jako správce" (doporučeno)
3. **Postupujte podle pokynů** instalátoru:
   - Vyberte instalační složku (výchozí: `C:\Users\[USERNAME]\AppData\Local\ElektronApp`)
   - Potvrďte vytvoření zástupců na ploše a v Start menu
   - Dokončete instalaci

**✅ Po dokončení**: Na ploše se objeví ikona "ElektronApp"

---

### Krok 2: Instalace Python backendu

1. **Otevřete složku s distribučním balíčkem**
2. **Najděte soubor `python-backend-install.bat`**
3. **Klikněte pravým tlačítkem** → "Spustit jako správce"
4. **Sledujte průběh instalace**:
   - Script zkontroluje Python
   - Vytvoří izolované prostředí
   - Nainstaluje potřebné knihovny
   - Ověří funkčnost

**🐍 Pokud nemáte Python:**
- Script vás upozorní a poskytne odkazy na stažení
- Doporučujeme: Python z [Microsoft Store](https://apps.microsoft.com/store/detail/python-311/9NRWMJP3717K)
- Po instalaci Python spusťte `python-backend-install.bat` znovu

**✅ Po dokončení**: Zobrazí se zpráva "INSTALACE DOKONČENA ÚSPĚŠNĚ!"

---

### Krok 3: První spuštění

1. **Klikněte na ikonu "ElektronApp"** na ploše
2. **Počkejte na načtení** (první spuštění může trvat 10-15 sekund)
3. **Aplikace se otevře** s hlavním menu

**✅ Hotovo!** Aplikace je připravena k použití.

---

## 🛠️ Řešení problémů

### ❌ "Python není nainstalován"

**Problém**: Script hlásí chybějící Python

**Řešení**:
1. Nainstalujte Python z [python.org](https://www.python.org/downloads/) nebo [Microsoft Store](https://apps.microsoft.com/store/detail/python-311/9NRWMJP3717K)
2. Při instalaci zaškrtněte "Add Python to PATH"
3. Restartujte počítač
4. Spusťte `python-backend-install.bat` znovu

### ❌ "Backend se nepodařilo spustit"

**Problém**: Aplikace se nespustí nebo hlásí chybu backendu

**Řešení**:
1. Zkontrolujte, že `python-backend-install.bat` proběhl úspěšně
2. Zkuste restartovat počítač
3. Spusťte aplikaci jako správce
4. Zkontrolujte antivirus - možná blokuje Python procesy

### ❌ "Chyba při zpracování Excel souborů"

**Problém**: Nástroje nefungují s Excel soubory

**Řešení**:
1. Zkontrolujte, že máte nainstalovaný Microsoft Excel
2. Otevřete Excel alespoň jednou a dokončete úvodní nastavení
3. Zkuste restartovat počítač
4. Spusťte aplikaci jako správce

### ❌ Antivirus blokuje aplikaci

**Problém**: Antivirus označuje soubory jako podezřelé

**Řešení**:
1. Přidejte složku aplikace do výjimek antivirsu
2. Dočasně vypněte real-time ochranu během instalace
3. Označte aplikaci jako důvěryhodnou

### ❌ "Port 5000 je obsazený"

**Problém**: Backend se nemůže spustit kvůli obsazenému portu

**Řešení**:
1. Restartujte počítač
2. Ukončete všechny Python procesy v Task Manageru
3. Spusťte aplikaci znovu

---

## 📞 Kontakt a podpora

### 🆘 Potřebujete pomoc?

**Email**: max.parez@seznam.cz  
**Telefon**: [váš telefon]  
**Dostupnost**: Po-Pá, 8:00-16:00

### 📝 Při kontaktování uveďte:
- Jaký problém máte
- Co jste dělali před vznikem problému
- Screenshot chybové hlášky (pokud existuje)
- Verzi Windows a Office

---

## 📚 Rychlá nápověda k nástrojům

### 🎓 Nástroj 1: Inovativní vzdělávání
**Co dělá**: Zpracovává docházku z inovativního vzdělávání (16h nebo 32h kurzy)
**Postup**: Vybrat šablonu → Vybrat soubory s docházkou → Zpracovat

### 📊 Nástroj 2: Speciální data ZoR
**Co dělá**: Vytváří přehledy docházky z více tříd
**Postup**: Vybrat soubory → Nastavit možnosti → Zpracovat

### 📄 Nástroj 3: Generátor plakátů
**Co dělá**: Vytváří PDF plakáty projektů
**Postup**: Zadat seznam projektů → Vybrat orientaci → Generovat

---

## 📋 Kontrolní seznam po instalaci

- [ ] ElektronApp-Setup.exe úspěšně nainstalován
- [ ] python-backend-install.bat proběhl bez chyb
- [ ] Ikona aplikace se objevila na ploše
- [ ] Aplikace se spustí kliknutím na ikonu
- [ ] Hlavní menu se načte správně
- [ ] Všechny 3 nástroje jsou dostupné

---

## 🔄 Aktualizace aplikace

V budoucnu při vydání nových verzí:

1. **Stáhněte nový distribuční balíček**
2. **Spusťte `ElektronApp-Setup.exe`** (přepíše starou verzi)
3. **Spusťte `python-backend-install.bat`** (aktualizuje knihovny)
4. **Restart aplikace**

---

*Vytvořeno: 2025-06-03*  
*Verze aplikace: 1.0.0*  
*Verze návodu: 1.0*