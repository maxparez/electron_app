# Regression Test Suite - Návod k použití

## 🎯 Účel

Regression testy zajišťují, že při úpravách kódu nedojde k nechtěným změnám v chování aplikace. Testy automaticky:
- Zpracují testovací soubory
- Porovnají výstupy s očekávanými výsledky
- Nahlásí jakékoliv rozdíly

## 🚀 První spuštění - vytvoření baseline

Při prvním spuštění je potřeba vytvořit "baseline" - očekávané výstupy:

```bash
cd tests/regression
python run_initial_baseline.py
```

Tento script:
1. Zpracuje všechny testovací soubory
2. Uloží výstupy jako očekávané výsledky do `expected/`
3. Pro chybové případy uloží JSON s error messages
4. Pro validní případy uloží Excel výstupy

## ✅ Spuštění testů

Po vytvoření baseline můžete kdykoliv spustit testy:

```bash
cd tests/regression
python test_regression.py

# nebo pomocí shell scriptu
./run_tests.sh
```

## 📊 Výstup testů

```
===========================================================
REGRESSION TEST SUITE - InvVzd Tool
===========================================================
Start time: 2025-06-03 14:30:00

Testing 16h version...
  Testing: error_dates.xlsx
    ✅ PASSED
  Testing: error_missing.xlsx
    ✅ PASSED
  Testing: valid_basic.xlsx
    ✅ PASSED
  Testing: valid_full.xlsx
    ❌ FAILED

Testing 32h version...
  ...

===========================================================
SUMMARY
===========================================================
Total tests: 8
✅ Passed: 7
❌ Failed: 1
⚠️  Errors: 0

Failed/Error tests:
  - 16h/valid_full.xlsx: FAILED
```

## 🔍 Co testy kontrolují

### Pro validní soubory:
- Zda se vytvoří výstupní Excel
- Zda data v Excel souborech odpovídají očekávaným
- Porovnává se obsah, ne formátování

### Pro chybové soubory:
- Zda aplikace správně detekuje chyby
- Zda error messages odpovídají očekávaným

## 🛠️ Údržba testů

### Přidání nového testu:
1. Přidejte soubor do `inputs/16h/` nebo `inputs/32h/`
2. Spusťte `run_initial_baseline.py` pro vytvoření expected output
3. Nebo ručně přidejte očekávaný výstup do `expected/`

### Aktualizace expected outputs:
Pokud je změna v chování záměrná:
1. Ověřte, že nové chování je správné
2. Spusťte `run_initial_baseline.py` znovu
3. Nebo ručně aktualizujte soubory v `expected/`

## 📁 Struktura

```
tests/regression/
├── inputs/          # Testovací vstupy (v gitu)
├── outputs/         # Aktuální výstupy (ignorováno)
├── expected/        # Očekávané výstupy (v gitu)
├── test_regression.py
├── run_initial_baseline.py
└── run_tests.sh
```

## 💡 Tipy

- Spouštějte testy před každým commitem
- Při CI/CD můžete volat `python test_regression.py`
- Exit code: 0 = úspěch, 1 = selhání