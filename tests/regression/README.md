# Regression Test Suite

## Struktura adresářů

```
tests/regression/
├── inputs/                      # Vstupní soubory
│   ├── templates/              # Šablony
│   │   ├── template_16h.xlsx   # Šablona pro 16h verzi
│   │   └── template_32h.xlsx   # Šablona pro 32h verzi
│   │
│   ├── 16h/                    # Testovací docházky 16h
│   │   ├── valid_basic.xlsx    # Základní validní soubor
│   │   ├── valid_full.xlsx     # Plně vyplněný soubor
│   │   ├── valid_minimal.xlsx  # Minimální validní data
│   │   ├── error_dates.xlsx    # Chyby v datumech
│   │   ├── error_missing.xlsx  # Chybějící povinná data
│   │   └── edge_case.xlsx      # Hraniční případ
│   │
│   └── 32h/                    # Testovací docházky 32h
│       ├── valid_basic.xlsx    # Základní validní soubor
│       ├── valid_full.xlsx     # Plně vyplněný soubor
│       ├── valid_minimal.xlsx  # Minimální validní data
│       ├── error_dates.xlsx    # Chyby v datumech
│       ├── error_missing.xlsx  # Chybějící povinná data
│       └── edge_case.xlsx      # Hraniční případ
│
├── outputs/                     # Aktuální výstupy (git ignore)
│   ├── 16h/                    # Výstupy z 16h testů
│   └── 32h/                    # Výstupy z 32h testů
│
└── expected/                    # Očekávané výstupy
    ├── 16h/                    # Očekávané výstupy 16h
    │   ├── valid_basic_output.xlsx
    │   ├── valid_full_output.xlsx
    │   ├── valid_minimal_output.xlsx
    │   ├── error_dates_output.json     # JSON s chybami
    │   ├── error_missing_output.json   # JSON s chybami
    │   └── edge_case_output.xlsx
    │
    └── 32h/                    # Očekávané výstupy 32h
        ├── valid_basic_output.xlsx
        ├── valid_full_output.xlsx
        ├── valid_minimal_output.xlsx
        ├── error_dates_output.json     # JSON s chybami
        ├── error_missing_output.json   # JSON s chybami
        └── edge_case_output.xlsx
```

## Pojmenování souborů

### Vstupní soubory (inputs/)
- **valid_*** - soubory které mají projít bez chyb
- **error_*** - soubory které mají vyvolat chyby
- **edge_*** - hraniční případy

### Výstupní soubory (expected/)
- Pro validní vstupy: `{input_name}_output.xlsx`
- Pro chybové vstupy: `{input_name}_output.json` (obsahuje error messages)

## Použití

1. Nahrajte testovací data do `inputs/`
2. Spusťte současnou verzi aplikace na všechny vstupy
3. Zkontrolujte výstupy a uložte je do `expected/`
4. Při budoucích změnách spusťte regression test