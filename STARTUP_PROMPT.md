# 🚀 Startup Prompt pro Claude Code

## Základní prompt pro načtení kontextu

Zkopírujte tento text při každém novém spuštění Claude Code:

```
Jsem zpět k projektu electron_app. Přečti si prosím tyto soubory pro kontext:
@CLAUDE.md @PROGRESS.md @PROJECT_PLAN.md @CLAUDE_CONTEXT_GUIDE.md

Aktuální stav:
- Aplikace je 100% dokončená a otestovaná
- Všechny 3 nástroje fungují (InvVzd, ZorSpecDat, Plakát)
- Instalační systém připraven (install-windows.bat)
- Branch: feature/next-phase

Co plánuji dělat dnes: [DOPLŇTE SVŮJ ZÁMĚR]
```

## Varianty podle situace

### 🔧 Pro opravu chyby
```
Jsem zpět k projektu electron_app. Přečti si prosím tyto soubory pro kontext:
@CLAUDE.md @PROGRESS.md @PROJECT_PLAN.md

Našel jsem chybu v [NÁSTROJ]:
[POPIS CHYBY]

Prosím analyzuj a navrhni opravu. Použij tag [fix-XXX] pro commit.
```

### ✨ Pro novou funkci
```
Jsem zpět k projektu electron_app. Přečti si prosím tyto soubory pro kontext:
@CLAUDE.md @PROGRESS.md @PROJECT_PLAN.md

Chci přidat novou funkci:
[POPIS FUNKCE]

Prosím:
1. Zkontroluj, jestli to neovlivní existující funkcionalitu
2. Navrhni implementaci
3. Použij TodoWrite pro plánování
4. Použij tag [feat-XXX] pro commity
```

### 📚 Pro aktualizaci dokumentace
```
Jsem zpět k projektu electron_app. Načti kontext:
@CLAUDE.md @PROGRESS.md 

Potřebuji aktualizovat dokumentaci:
- [CO AKTUALIZOVAT]
- [PROČ]

Použij tag [docs-XXX] pro commit.
```

### 🧪 Pro testování
```
Jsem zpět k projektu electron_app. Načti kontext:
@CLAUDE.md @PROGRESS.md @PROJECT_PLAN.md

Chci otestovat:
- Nástroj: [InvVzd/ZorSpecDat/Plakat]
- Scénář: [CO TESTOVAT]
- Prostředí: [Windows/Linux]

Vytvoř test a zaznamenej výsledky.
```

### 🚀 Pro deployment
```
Jsem zpět k projektu electron_app. Načti kontext:
@CLAUDE.md @PROGRESS.md @INSTALACE-WINDOWS.md

Chci nasadit novou verzi. Prosím:
1. Zkontroluj, že jsme na správné větvi
2. Projdi deployment checklist
3. Vytvoř nový tag verze
4. Aktualizuj dokumentaci
```

## Důležité poznámky

1. **Vždy uveďte svůj záměr** - Claude pak lépe pochopí kontext
2. **Specifikujte větev** - pokud pracujete na jiné než feature/next-phase
3. **Přidejte relevantní soubory** - pomocí @ pro konkrétní kontext
4. **Buďte konkrétní** - čím přesnější popis, tím lepší pomoc

## Příklady konkrétních záměrů

- "Opravit chybu s načítáním 32h šablony v InvVzd"
- "Přidat možnost exportu do CSV v ZorSpecDat"
- "Vylepšit error handling při síťových chybách"
- "Aktualizovat návod pro kolegy o nové funkci"
- "Připravit verzi 1.1.0 k nasazení"

---
*Tento soubor použijte jako rychlou referenci při startu nové session*