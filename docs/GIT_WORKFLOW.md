# Git Workflow pro Electron App

## 🏷️ Systém tagování commitů

### Formát commit message

```
[typ-číslo] Krátký popis (max 50 znaků)

Detailnější vysvětlení změn. Maximálně 72 znaků na řádek.
Vysvětlete CO se změnilo a PROČ bylo potřeba změnu udělat.

- Odrážky jsou v pořádku
- Použijte pomlčku nebo hvězdičku

Fixes #123
```

### Typy tagů

- `[feat-XXX]` - Nová funkcionalita
- `[fix-XXX]` - Oprava chyby
- `[refactor-XXX]` - Refaktoring kódu
- `[test-XXX]` - Přidání nebo úprava testů
- `[docs-XXX]` - Dokumentace
- `[style-XXX]` - Formátování, styly (ne CSS)
- `[perf-XXX]` - Optimalizace výkonu
- `[build-XXX]` - Změny v build systému
- `[ci-XXX]` - CI/CD změny
- `[chore-XXX]` - Údržba, drobné změny

### Příklady

```
[feat-001] Add Excel date fixing algorithm

Implemented intelligent date parsing that handles incomplete dates
and infers year from context with confidence levels.

- Supports DD.MM and DD.MM.YYYY formats
- Adds confidence indicator for inferred dates
- Handles edge cases for year boundaries

Fixes #12
```

```
[fix-002] Fix plakat generator financingType error

Changed financingType value from Czech to English and added
proper Content-Type header for form submissions.

- Changed 'spolufinancován' to 'co-financed'
- Added application/x-www-form-urlencoded header
```

## 🌿 Struktura větví

### Hlavní větve

- **`main`** (nebo `master`): Produkční kód
  - Vždy připravený k nasazení
  - Změny pouze přes pull requesty
  - Tagován verzemi (v1.0.0, v1.1.0, atd.)

- **`develop`**: Vývojová integrace
  - Integrace feature větví
  - Musí být funkční
  - Cíl pro PR z feature větví

### Feature větve

```
feature/tool-{nástroj}-{popis}
feature/ui-{komponenta}-{popis}
feature/api-{endpoint}-{popis}
```

Příklady:
- `feature/tool-plakat-pdf-generation`
- `feature/ui-progress-indicators`
- `feature/api-file-upload`

### Opravné větve

```
fix/tool-{nástroj}-{problém}
fix/ui-{komponenta}-{problém}
```

Příklady:
- `fix/tool-invvzd-date-parsing`
- `fix/ui-download-dialog`

### Hotfix větve (urgentní opravy)

```
hotfix/v{verze}-{popis}
```

Příklad:
- `hotfix/v1.0.1-critical-crash`

## 📝 Automatický commit workflow

### Pravidla pro časté commity

1. **Commit po každé dokončené funkci** (ne po každém souboru)
2. **Maximálně 2 hodiny práce** bez commitu
3. **Push na GitHub minimálně 2x denně**
4. **Vždy před přestávkou nebo koncem práce**

### Helper script pro tagy

```bash
#!/bin/bash
# next-tag.sh

type=$1
if [ -z "$type" ]; then
  echo "Usage: ./next-tag.sh [feat|fix|refactor|test|docs]"
  exit 1
fi

# Najdi poslední číslo pro daný typ
last_num=$(git log --oneline --grep="\[$type-[0-9]\{3\}\]" | head -1 | grep -o "\[$type-[0-9]\{3\}\]" | grep -o "[0-9]\{3\}")
if [ -z "$last_num" ]; then
  next_num="001"
else
  next_num=$(printf "%03d" $((10#$last_num + 1)))
fi

echo "[$type-$next_num]"
```

## 🔄 Workflow příklad

```bash
# 1. Začni novou feature
git checkout develop
git pull origin develop
git checkout -b feature/tool-plakat-optimization

# 2. Pracuj a commituj průběžně
# Po implementaci části funkcionality:
git add src/python/tools/plakat_generator.py
git commit -m "[feat-003] Add progress tracking to plakat generator

Added ability to track progress when generating multiple PDFs.
Updates UI with current/total counter.

- Added progress callback to generator class
- Integrated with frontend progress bar"

# 3. Po 2 hodinách nebo významném milníku - push
git push origin feature/tool-plakat-optimization

# 4. Pokračuj v práci...
# Další commit:
git add .
git commit -m "[feat-004] Add batch processing for plakat

Implemented parallel processing for multiple projects to
improve performance when generating many PDFs.

- Process up to 5 PDFs concurrently
- Show individual progress for each"

# 5. Na konci dne nebo po dokončení - push a PR
git push origin feature/tool-plakat-optimization
# Vytvoř Pull Request na GitHubu
```

## 🚀 Automatizace

### Git aliases pro časté operace

Přidej do `~/.gitconfig`:

```ini
[alias]
    # Quick commit s automatickým tagem
    qc = "!f() { tag=$(./next-tag.sh $1); git commit -m \"$tag $2\"; }; f"
    
    # Status + diff
    sd = !git status && git diff --stat
    
    # Push current branch
    pc = !git push origin $(git branch --show-current)
    
    # Quick save (add all + commit + push)
    save = !git add -A && git commit -m \"[chore-$(date +%Y%m%d)] WIP: Save progress\" && git pc
```

Použití:
```bash
git qc feat "Add new validation"
git qc fix "Resolve date parsing issue"
git save  # Rychlé uložení WIP
```

## 📊 Commit frekvence

### Doporučený rytmus

- **Ranní start**: Pull nejnovější změny
- **Každé 2 hodiny**: Alespoň 1 commit + push
- **Před obědem**: Commit + push aktuální práce
- **Odpoledne**: 2-3 commity podle postupu
- **Konec dne**: Finální commit + push + PR pokud je hotovo

### Monitoring

```bash
# Zobraz dnešní commity
git log --oneline --since="6am" --author="$(git config user.name)"

# Počet commitů tento týden
git shortlog -sn --since="1 week ago"
```

## 🔙 Rollback postupy

### Vrácení lokálních změn

```bash
# Zahodit všechny neuložené změny
git reset --hard HEAD

# Nebo je schovat na později
git stash save "WIP: popis změn"
```

### Vrácení posledního commitu

```bash
# Ponechat změny
git reset --soft HEAD~1

# Zahodit změny
git reset --hard HEAD~1
```

### Vrácení push-nutého commitu

```bash
# Vytvoř revert
git revert HEAD
git push origin $(git branch --show-current)
```

## 📋 Checklist pro každý den

- [ ] Ráno: `git pull origin develop`
- [ ] Před prací: Zkontroluj aktuální větev
- [ ] Každé 2h: Commit změny s proper tagem
- [ ] Každé 2h: Push na GitHub
- [ ] Před pauzou: Quick save (`git save`)
- [ ] Konec dne: Review commitů a push
- [ ] Pátek: Vytvoř PR pro dokončené features

## 🎯 Best Practices

1. **Atomické commity** - Každý commit dělá jednu věc
2. **Srozumitelné zprávy** - Jiný vývojář musí pochopit
3. **Testuj před commitem** - Alespoň základní funkčnost
4. **Nepushuj broken kód** - Vždy musí jít zkompilovat
5. **Review před merge** - I vlastní PR si přečti

## 📝 Integrace s CLAUDE.md

Přidej do svých instrukcí:

```markdown
## Git Workflow

- Commituj každé 2 hodiny nebo po dokončení funkce
- Používej tagy: [feat-XXX], [fix-XXX], [refactor-XXX]
- Push na GitHub minimálně 2x denně
- Viz docs/GIT_WORKFLOW.md pro detaily
```