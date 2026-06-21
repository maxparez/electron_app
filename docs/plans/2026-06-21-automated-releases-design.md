# Automatizované verzování a poznámky k vydání

## Cíl

Zavést jeden opakovatelný release příkaz, který určí novou SemVer verzi,
aktualizuje všechny výskyty verze, vytvoří podrobný changelog a připraví data
pro přehledný aktualizační dialog přímo v aplikaci.

## Zdroj změn

Každá uživatelsky významná změna bude mít samostatný JSON soubor v `changes/`.
Fragment obsahuje typ změny (`feature`, `improvement`, `fix`), krátký český
nadpis a srozumitelný český popis. Volitelný příznak `breaking` označí
nekompatibilní změnu.

Tento formát odděluje technický commit od textu určeného uživateli. Release
nástroj spotřebuje všechny fragmenty, vloží je do `CHANGELOG.md` a odstraní je,
aby se v příštím vydání neopakovaly.

## Automatické určení verze

- alespoň jeden `breaking` fragment: zvýšení major verze;
- alespoň jeden `feature` fragment: zvýšení minor verze;
- ostatní změny: zvýšení patch verze.

Typ vydání lze explicitně přepsat parametrem `--type patch|minor|major`.
Příkaz aktualizuje `package.json`, `package-lock.json`, obě environment
konfigurace a výchozí Electron konfiguraci.

## Výstup releasu

Soubor `release-notes.json` obsahuje aktuální verzi, datum a změny rozdělené do
sekcí. Stejná data se vloží v Markdown podobě na začátek `CHANGELOG.md`.
Release příkaz pouze připraví změny; automaticky necommitne, netaguje ani
nepushuje, aby zůstala zachována kontrola před publikací.

## Aktualizační dialog

Updater načte `release-notes.json` přímo z cílové vzdálené větve pomocí
`git show`. Vlastní modal v aplikaci zobrazí:

- aktuální a novou verzi;
- kanál aktualizací;
- přehled nových funkcí, vylepšení a oprav;
- akce „Aktualizovat nyní“ a „Později“.

Pokud metadata ve starší větvi chybí nebo jsou neplatná, updater použije
bezpečný fallback s posledním commit summary.

## Aktuální vydání

Změny od `1.3.0`, včetně nové sekce rozdělení docházky, představují nové
funkce. První vydání připravené novým procesem proto bude `1.4.0`.
