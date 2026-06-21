# Change fragments

Každá uživatelsky významná změna má před vydáním vlastní JSON soubor:

```json
{
  "type": "feature",
  "title": "Krátký český nadpis",
  "description": "Srozumitelný popis přínosu pro uživatele.",
  "breaking": false
}
```

Podporované typy:

- `feature` – automaticky zvýší minor verzi;
- `improvement` – zvýší patch verzi, pokud vydání neobsahuje novou funkci;
- `fix` – zvýší patch verzi;
- `breaking: true` – zvýší major verzi.

Příkaz `npm run release:prepare` fragmenty vloží do changelogu a
`release-notes.json`, aktualizuje verzi a spotřebované JSON soubory odstraní.
