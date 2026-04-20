# 🧠 Claude Code - Návod pro zachování kontextu

## Rychlý start pro pokračování v práci

### 1. Spuštění Claude Code
```bash
cd /root/vyvoj_sw/electron_app
claude
```

### 2. První prompt - načtení kontextu
Zkopírujte a vložte tento prompt:

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

## 📋 Důležité kontextové soubory

Claude Code automaticky načte CLAUDE.md při startu, ale pro plný kontext doporučuji explicitně načíst:

1. **CLAUDE.md** - Základní pravidla projektu
2. **PROGRESS.md** - Co je hotové, poslední změny
3. **PROJECT_PLAN.md** - Celkový přehled a cíle
4. **CLAUDE_CONTEXT_GUIDE.md** - Tento soubor
5. **PROGRESS_CONTEXT.md** - Detailní technický kontext (pokud existuje)

## 🌿 Správa větví (Git branches)

### Aktuální větve:
- **main** - Stabilní produkční verze
- **feature/next-phase** - Aktuální vývojová větev
- **deployment-windows** - Starší deployment větev (může být smazána)

### Přepínání větví:
```bash
# Zobrazit aktuální větev
git branch --show-current

# Přepnout na vývojovou větev
git checkout feature/next-phase

# Přepnout na hlavní větev
git checkout main

# Vytvořit novou feature větev
git checkout -b feature/nova-funkce
```

### Workflow pro nové změny:

1. **Malé opravy (hotfix)**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/nazev-opravy
   # ... práce ...
   git add -A && git commit -m "[fix-XXX] Popis opravy"
   git push origin hotfix/nazev-opravy
   # Vytvořit Pull Request na GitHubu
   ```

2. **Nové funkce**
   ```bash
   git checkout feature/next-phase
   git pull origin feature/next-phase
   # ... práce ...
   git add -A && git commit -m "[feat-XXX] Popis funkce"
   git push origin feature/next-phase
   ```

3. **Deployment**
   ```bash
   # Až budou změny otestované
   git checkout main
   git merge feature/next-phase
   git push origin main
   git tag -a v1.1.0 -m "Verze 1.1.0 - popis změn"
   git push origin v1.1.0
   ```

## 🔧 Časté úkoly a jejich řešení

### Přidání nové funkce
```
Chci přidat novou funkci: [POPIS FUNKCE]
Prosím:
1. Zkontroluj aktuální stav v PROGRESS.md
2. Naplánuj implementaci
3. Použij TodoWrite pro sledování úkolů
4. Commituj s odpovídajícím tagem [feat-XXX]
```

### Oprava chyby
```
Našel jsem chybu: [POPIS CHYBY]
Prosím:
1. Analyzuj problém
2. Navrhni řešení
3. Implementuj opravu
4. Otestuj
5. Commituj s tagem [fix-XXX]
```

### Vylepšení dokumentace
```
Potřebuji aktualizovat dokumentaci pro: [CO]
Prosím aktualizuj příslušné soubory a commituj s [docs-XXX]
```

## 📝 Šablony promptů

### Pro pokračování v rozpracované práci
```
Pokračuji v práci na [NÁZEV FUNKCE].
Poslední stav: [CO BYLO UDĚLÁNO]
Zbývá dokončit: [CO ZBÝVÁ]
Prosím pokračuj v implementaci.
```

### Pro code review
```
Prosím zkontroluj poslední commity:
git log --oneline -10
Ověř, že kód odpovídá našim standardům v CORE_DEVELOPMENT_PRINCIPLES.md
```

### Pro testování
```
Potřebuji otestovat [NÁSTROJ/FUNKCI].
Vytvoř test scénáře a ověř funkčnost.
Zaznamenej výsledky do PROGRESS.md.
```

## 🚀 Deployment checklist

Před nasazením nové verze:
```
Prosím projdi deployment checklist:
1. Jsou všechny testy zelené?
2. Je dokumentace aktuální?
3. Je PROGRESS.md aktualizován?
4. Jsou všechny commity v main větvi?
5. Je vytvořen nový tag verze?
6. Je aktualizován install-windows.bat (pokud potřeba)?
```

## 💡 Tipy pro efektivní práci

1. **Vždy začněte s kontextem** - načtěte důležité soubory
2. **Používejte TodoWrite** - sledujte rozpracované úkoly
3. **Commitujte často** - minimálně každé 2 hodiny
4. **Dodržujte konvence** - [feat-XXX], [fix-XXX], [docs-XXX]
5. **Testujte průběžně** - zejména na Windows

## 🔄 Pravidelná údržba

Každý měsíc:
```
Proveď měsíční údržbu:
1. Aktualizuj závislosti (npm update, pip list --outdated)
2. Zkontroluj bezpečnostní upozornění
3. Proveď git prune a vyčisti staré větve
4. Aktualizuj dokumentaci
5. Zkontroluj logs velikost
```

## 📞 Když něco nefunguje

1. Zkontrolujte aktuální větev: `git branch --show-current`
2. Zkontrolujte stav: `git status`
3. Přečtěte si logy: `tail -50 logs/electron.log`
4. Vraťte se k poslednímu funkčnímu stavu: `git reset --hard HEAD~1`
5. Požádejte Claude o pomoc s konkrétním problémem

---
*Poslední aktualizace: 2025-06-07*