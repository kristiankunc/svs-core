#table(
  stroke: none,
  columns: (2fr, 3fr),
  image("img/gyarab_logo.png", width: 40%),
  align(right)[#heading(outlined: false)[Gymnázium, Praha 6, Arabská 14]
    tel.: 235 351 708 \
    fax.: 222 262 066 \
    e-mail: ga\@gyarab.cz\
    www.gyarab.cz],
)

#line(stroke: 0.15em + rgb("#808080"), length: 100%)

#heading(outlined: false)[Zadání ročníkového projektu]
#v(0.25cm)
#grid(
  columns: (1fr, 3fr),
  row-gutter: 0.5cm,
  heading(level: 2, outlined: false)[Název:],
  heading(level: 2, outlined: false)[Adess -- umělecky dirigovaný syntetizér zvuků motorů],

  heading(level: 2, outlined: false)[Řešitel:], heading(level: 2, outlined: false)[Kubota Leon, 4.E],

  heading(level: 2, outlined: false)[Vedoucí práce:], heading(level: 2, outlined: false)[Ing. Daniel Kahoun],

  heading(level: 2, outlined: false)[Datum odevzdání:], heading(level: 2, outlined: false)[28. 2. 2026],
)

#heading(level: 2, outlined: false)[Způsob zpracování a kritéria hodnocení:]
Zpracování v požadovaném rozsahu se řídí obecně závaznými pokyny zpracování ročníkových projektů. Řešitel elektronicky odevzdáve stanoveném termínu dokumentaci, prezentaci, poster a další vyžádané přílohy (např. zdrojové kódy, ukázková data). Před obhajobou řešitel odevzdá jeden výtisk stejné dokumentace s podepsaným prohlášením o autorství a jeden poster, neurčí-li vedoucí jinak. Hodnotí se odborné zpracování úlohy, použití návrhových vzorů, prezentace při obhajobě a funkcionalita produktu.

#heading(level: 2, outlined: false)[Popis (povinná část):]
Vytvořte konzolovou aplikaci pro procedurální syntézu zvuků motorů určenou pro film a animaci. Program generuje zvukové vzorky na základě uživatelské konfigurace a klíčových snímků definovaných ve vlastním datovém formátu _DST_.

#heading(level: 2, outlined: false)[Upřesnění zadání:]
- Implementace parseru konfiguračních souborů _adess_
- Procedurální generování pole vzorků zvuku motoru
- Práce s klíčovými snímky pro změnu zvuku v čase
- Export _audia_ do standardního formátu _WAV_
- Ovládání aplikace pomocí příkazové řádky (_CLI_)

#heading(level: 2, outlined: false)[Bonus (nepovinná část):]
- Podpora pro různé typy motorů (vrtulové, spalovací)
- Přidání zvukových efektů (např. ozvěna, zkreslení)
- Grafické znázornění generované zvukové vlny v _CLI_
- Možnost reálného náhledu (přehřání) před uložením

#heading(level: 2, outlined: false)[Platforma:]
- C

#v(1fr)

#table(
  columns: (1fr, 1fr, 1fr),
  align: center,
  stroke: none,
  row-gutter: -0.4em,

  [],
  [#line(stroke: (dash: "dashed", paint: rgb("#808080")), length: 92%)],
  [#line(stroke: (dash: "dashed", paint: rgb("#808080")), length: 92%)],

  [], [datum podpisu], [podpis řešitele],
)
