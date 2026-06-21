# Rozdělení docházky podle listů

## Cíl

Přidat samostatný nástroj, který najde excelové sešity obsahující více listů
s docházkou inovativního vzdělávání a rozdělí každý vhodný list do samostatného
souboru. Stávající nástroj pro zpracování docházky zůstane beze změny.

## Uživatelský tok

V levém menu a na domovské stránce bude nová sekce „Rozdělení docházky“.
Uživatel může vybrat jednotlivé soubory nebo složku. Aplikace před zařazením
ověří, že sešit obsahuje nejméně dva viditelné listy odpovídající docházce.
Seznam vhodných souborů lze upravit odebráním položek. Tlačítko „Rozdělit“
spustí zpracování a zobrazí výsledek po jednotlivých zdrojových souborech.

## Detekce

Kontrola struktury používá `openpyxl`, takže výběr a skenování fungují bez
spouštění Excelu. Za docházkový list se považuje viditelný list, který odpovídá
podporovanému 16hodinovému nebo 32hodinovému vstupnímu formátu. Skryté,
prázdné a pomocné listy se přeskočí. Soubor je vhodný pouze tehdy, když
obsahuje alespoň dva takové listy.

## Rozdělení a výstupy

Vlastní kopírování listů používá Excel přes `xlwings`, aby se zachovalo
formátování, vzorce, rozměry, tiskové nastavení a další vlastnosti listu.
Každý zdroj ukládá výstupy do podsložky `rozdelene_dochazky` vedle originálu.
Název má tvar `dochazka_inovace_<nazev_listu_bez_diakritiky>.xlsx`.
Nepovolené znaky se převedou na podtržítka a kolize se řeší příponou `_2`,
`_3` a podobně; existující soubory se nepřepisují.

## Chyby a report

Výsledek obsahuje zdrojový soubor, vytvořené soubory, přeskočené listy
s důvodem a chyby. Selhání jednoho sešitu nezastaví ostatní. Pokud není
dostupný Windows Excel nebo `xlwings`, aplikace vrátí jasnou chybu a nevytvoří
neúplné výstupy.

## Ověření

Automatické testy pokryjí detekci vhodných listů, ignorování skrytých listů,
normalizaci názvů, kolize výstupů, částečné chyby a přítomnost kompletního UI
a API zapojení. Skutečné zachování Excelových vlastností vyžaduje závěrečný
manuální test na Windows s Microsoft Excelem.
