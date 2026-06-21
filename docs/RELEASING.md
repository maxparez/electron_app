# Příprava nové verze

## 1. Zapište změny

Pro každou uživatelsky významnou změnu vytvořte JSON soubor v `changes/`.
Použijte český nadpis a popis zaměřený na přínos pro uživatele, nikoli
technický název commitu.

```json
{
  "type": "feature",
  "title": "Nový nástroj",
  "description": "Uživatel nyní může ...",
  "breaking": false
}
```

Typy `improvement` a `fix` automaticky připraví patch vydání. Typ `feature`
připraví minor vydání a `breaking: true` major vydání.

## 2. Připravte release

```bash
npm run release:prepare
```

Příkaz:

- určí další SemVer verzi;
- aktualizuje `package.json`, lockfile a runtime konfigurace;
- vygeneruje `release-notes.json`;
- vloží české poznámky do `CHANGELOG.md`;
- odstraní spotřebované JSON fragmenty.

Výjimečně lze typ vydání vynutit:

```bash
npm run release:patch
npm run release:minor
npm run release:major
```

## 3. Ověřte a publikujte

Zkontrolujte diff a spusťte relevantní testy. Release nástroj záměrně
necommitne, netaguje ani nepushuje automaticky.

Použijte commit ve formátu:

```text
[release-NNN] Prepare version X.Y.Z
```

Po synchronizaci distribuční větve updater načte `release-notes.json` a zobrazí
uživatelům stejné poznámky přímo v aplikaci.
