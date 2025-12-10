# Changelog - Nástroje OP JAK

Všechny významné změny v tomto projektu budou zdokumentovány v tomto souboru.

## [1.2.0] - 2025-12-10

### ✨ Nové funkce

#### ZorSpecDat - Dynamická detekce 16h/32h verzí
- **Automatická detekce**: Aplikace nyní automaticky rozpozná, zda zpracováváte 16hodinové nebo 32hodinové inovativní vzdělávání
- **Dynamické zobrazení**: Hlavička "Počet dětí/žáků se splněnou docházkou" zobrazuje správný práh (16h nebo 32h)
- **Přesné výpočty**: Počty studentů se počítají s prahem 16+ nebo 32+ hodin podle detekované verze

#### ZorSpecDat - Ochrana před smíšením verzí
- **Validace při výběru**: Aplikace zabrání kombinování souborů 16h a 32h verzí v jednom zpracování
- **Inteligentní error panel**: Při detekci smíšených verzí se zobrazí přehledný panel s:
  - Počtem souborů každé verze (modré 16h, fialové 32h)
  - Třemi akčními tlačítky pro rychlé řešení:
    - "Ponechat pouze 16h verzi"
    - "Ponechat pouze 32h verzi"
    - "Smazat vše a začít znovu"
- **Funguje všude**: Validace probíhá jak při výběru složky, tak při manuálním výběru souborů

#### ZorSpecDat - Kontrolní součty hodin
- **Celkem hodin - formy**: Součet všech hodin přes všechny formy vzdělávání
- **Celkem hodin - témata**: Součet všech hodin přes všechna témata
- **Vedle sebe**: Oba kontrolní součty jsou zobrazeny vedle sebe pod statistikami docházky

### 🔧 Vylepšení

#### Vylepšené error logování
- **Kontext souborů**: Chybové zprávy nyní obsahují název souboru, který způsobil chybu
- **Detailní traceback**: Kompletní stack trace pro snadné debugování
- **Lepší diagnostika**: Rychlejší identifikace problémových souborů

#### Detekce datových anomálií
- **Varování o číslech**: Pokud sloupec "jmena" obsahuje číselné hodnoty místo jmen, zobrazí se varování
- **Detailní informace**: Varování obsahuje:
  - Název souboru
  - Počet problémových buněk
  - Čísla řádků (např. "řádek 24, řádek 42, řádek 65")
  - Ukázku hodnot
- **Pokračování zpracování**: Hodnoty se automaticky převedou na text a zpracování pokračuje

#### Vizuální vylepšení
- **Decentní varování**: Varování jsou zobrazena v příjemné krémové barvě (ne křiklavá oranžová)
- **Správné umístění**: Varování se zobrazují pod blokem "Zpracování dokončeno"
- **Profesionální vzhled**: Gradientové pozadí a ikonky pro lepší vizuální přehled

### 🐛 Opravy chyb

- **[fix-146]**: Opravena chyba TypeError při porovnávání stringů a čísel ve sloupci 'jmena'
- **[fix-150]**: Opraven hardcoded čas zpracování - nyní se zobrazuje skutečný čas
- **[fix-154]**: Opraven překlep v názvu elementu, který zabraňoval zobrazení error panelu
- **[fix-155]**: Přidána validace verzí i při manuálním výběru souborů (nejen při výběru složky)

### 🎨 Stylové změny

- **[style-149]**: Změna varování z agresivní oranžové na decentní krémovou

### 📋 Technické detaily

Celkem 10 commitů s vylepšeními:
- [feat-145]: Vylepšené error logování s kontextem souborů
- [feat-147]: Detekce číselných hodnot v 'jmena' sloupci s varováními
- [feat-148]: Stylování varovných zpráv
- [feat-151]: Dynamická detekce 16h/32h prahu
- [feat-152]: Validace smíšených verzí (16h/32h)
- [feat-153]: Enhanced error panel s akčními tlačítky

---

## [1.1.0] - 2025-12-09

### ✨ Nové funkce

#### ZorSpecDat - Rozšíření pro ZUŠ a SŠ
- Přidána podpora pro školy typu ZUŠ (Základní umělecké školy)
- Přidána podpora pro školy typu SŠ (Střední školy)
- Statistiky docházky nyní zobrazují všechny typy škol: MŠ, ZŠ, ŠD, ZUŠ, SŠ

### 🔧 Vylepšení

- Kontrolní součty (celkem hodin) pro formy a témata zobrazeny vedle sebe
- Opraveny názvy sloupců pro výpočet kontrolních součtů

---

## [1.0.0] - 2025-12-06

### 🎉 První stabilní release

#### Funkční nástroje
1. **InvVzd Copy** - Zpracování inovativního vzdělávání (16/32 hodin)
2. **ZorSpecDat** - Agregace docházek a generování reportů
3. **Plakát Generator** - Generování PDF plakátů pro projekty

#### Základní funkce
- Electron desktop aplikace
- Python Flask backend
- Zpracování Excel souborů s xlwings
- Automatická instalace pro Windows
- Automatická aktualizace přes Git

---

**Formát**: Tento changelog dodržuje [Keep a Changelog](https://keepachangelog.com/cs/1.0.0/)
a projekt používá [Semantic Versioning](https://semver.org/lang/cs/).
