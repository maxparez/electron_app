# Nástroje pro ŠI a ŠII OP JAK

Desktop aplikace pro zpracování školní projektové dokumentace.

## 📋 Co aplikace umí

Aplikace nabízí 3 nástroje pro zpracování dat:

1. **Inovativní vzdělávání - Kopírování docházky** (16h/32h)
   - Kopírování docházky do oficiálních šablon
   - Automatické zpracování dat pro 16h a 32h varianty
   - Kontrola součtů a validace dat

2. **Specifické datové položky - Zpracování do ZoR**
   - Zpracování docházky z více tříd
   - Generování HTML reportů
   - Export unikátních seznamů žáků
   - Statistiky podle typů škol (MŠ, ZŠ, ŠD, ZUŠ, SŠ)

3. **Generátor plakátů**
   - Tvorba PDF plakátů pro projekty
   - Automatické formátování a export

---

## 🚀 Instalace

### Požadavky
- **Windows 10 nebo 11**
- **Microsoft Excel** (pro práci se šablonami)

### Postup instalace

1. **Stáhněte aplikaci** (pokud ještě nemáte):
   ```
   git clone git@github.com:maxparez/electron_app.git C:\OPJAK\electron_app
   ```

2. **Spusťte instalaci**:
   ```
   cd C:\OPJAK\electron_app
   install-windows.bat
   ```

3. **Vytvořte zástupce** na ploše:
   - Pravý klik na `start-app.bat`
   - Odeslat → Plocha (vytvořit zástupce)
   - Přejmenujte zástupce na "OP JAK Nástroje"

---

## 💻 Spuštění aplikace

**Dvakrát klikněte** na zástupce na ploše nebo spusťte:
```
C:\OPJAK\electron_app\start-app.bat
```

Aplikace se spustí a otevře se hlavní okno s výběrem nástrojů.

---

## 📚 Jak používat nástroje

### 1. Inovativní vzdělávání - Kopírování docházky

1. Vyberte nástroj "Inovativní vzdělávání"
2. Zvolte variantu (16h nebo 32h)
3. Vyberte zdrojový soubor s docházkou
4. Vyberte výstupní šablonu
5. Klikněte na "Zpracovat"
6. Výsledný soubor se automaticky uloží

### 2. Specifické datové položky - Zpracování do ZoR

1. Vyberte nástroj "Specifické datové položky"
2. Vyberte soubory nebo složku s docházkou
3. Klikněte na "Zpracovat"
4. Získáte:
   - HTML report s přehledy
   - Textový soubor se seznamem unikátních žáků
   - Statistiky podle typů škol
   - Kontrolní součty hodin

### 3. Generátor plakátů

1. Vyberte nástroj "Generátor plakátů"
2. Vyplňte údaje o projektu
3. Nahrajte loga a obrázky (pokud potřeba)
4. Klikněte na "Vygenerovat PDF"
5. PDF se automaticky uloží

---

## 🔄 Aktualizace aplikace

Pro aktualizaci na nejnovější verzi:

1. **Spusťte update script**:
   ```
   cd C:\OPJAK\electron_app
   update.bat
   ```

2. **Postupujte podle pokynů** na obrazovce

3. **Restartujte aplikaci** po dokončení aktualizace

**⚠️ POZOR:** Aktualizace přepíše lokální změny v aplikaci, ale vaše data v jiných složkách zůstanou nedotčena.

---

## 🛠️ Řešení problémů

### Aplikace se nespustí

1. **Zkontrolujte instalaci**:
   - Je složka `C:\OPJAK\electron_app` kompletní?
   - Existuje podsložka `venv`?

2. **Přeinstalujte aplikaci**:
   ```
   cd C:\OPJAK\electron_app
   install-windows.bat
   ```

### Chyba při zpracování souborů

1. **Zkontrolujte formát Excel souboru**:
   - Musí být ve formátu `.xlsx`
   - Musí obsahovat správné listy a sloupce

2. **Zkontrolujte Microsoft Excel**:
   - Je nainstalovaný?
   - Není otevřený jiný Excel soubor, který by blokoval operaci?

### Python backend nefunguje

1. **Zkontrolujte venv**:
   - Existuje složka `C:\OPJAK\electron_app\venv`?

2. **Reinstalujte Python prostředí**:
   ```
   cd C:\OPJAK\electron_app
   rmdir /s /q venv
   install-windows.bat
   ```

### Update selhal

1. **Zkontrolujte git**:
   - Je Git nainstalovaný?
   - Máte připojení k internetu?

2. **Manuální update**:
   ```
   cd C:\OPJAK\electron_app
   git pull origin windows-install
   ```

---

## 📁 Adresářová struktura

```
C:\OPJAK\electron_app\
├── start-app.bat          ← Spouštěcí soubor (vytvořte z něj zástupce)
├── install-windows.bat    ← Instalační script
├── update.bat             ← Update script
├── src/                   ← Zdrojové kódy aplikace
├── templates/             ← Excel šablony
├── venv/                  ← Python prostředí
├── node_modules/          ← Node.js závislosti
└── logs/                  ← Logy aplikace
```

---

## 📞 Kontakt a podpora

Pokud narazíte na problém:

1. Zkontrolujte logy v `C:\OPJAK\electron_app\logs\`
2. Kontaktujte správce aplikace
3. Popište problém co nejpodrobněji (co jste dělali, co se stalo, jaká chyba se zobrazila)

---

## 📝 Poznámky

- **Všechna data** (vstupní i výstupní soubory) ukládejte **MIMO** složku aplikace
- **Pravidelně aktualizujte** aplikaci pomocí `update.bat`
- **Nevytvářejte ručně** soubory ve složce aplikace - mohly by být přepsány při aktualizaci
- **Zálohujte** důležitá data před zpracováním

---

**Verze:** 1.1.0
**Poslední aktualizace:** 2024-12-08
