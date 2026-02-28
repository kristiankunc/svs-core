#table(
  stroke: none,
  columns: (2fr, 3fr),
  image("img/gyarab_logo.png", width: 40%),
  align(
    right,
  )[#heading(outlined: false)[Gymnázium, Praha 6, Arabská 14] tel.: 235 351 708 \ fax.: 222 262 066 \ e-mail: ga\@gyarab.cz\ www.gyarab.cz],
)

#line(stroke: 0.15em + rgb("#808080"), length: 100%)

#heading(outlined: false)[Zadání maturitní práce]
#v(0.25cm)
#grid(
  columns: (1.4fr, 3fr),
  row-gutter: 0.4cm,
  heading(level: 2, outlined: false)[Téma maturitní práce:],
  heading(level: 2, outlined: false)[Modernizace SVS pomocí kontejnerizace a Dockeru],

  heading(level: 2, outlined: false)[Zadavatel:], heading(level: 2, outlined: false)[RNDr. Zdeňka Hamhalterová],
  heading(level: 2, outlined: false)[Řešitel:], heading(level: 2, outlined: false)[ Kunc Kristián, 4.E],
  heading(level: 2, outlined: false)[Vedoucí práce:], heading(level: 2, outlined: false)[Ing. Daniel Kahoun],
  heading(level: 2, outlined: false)[Oponent:], heading(level: 2, outlined: false)[Ing. Zdeněk Murikář, CSc.],
  heading(level: 2, outlined: false)[Datum odevzdání:], heading(level: 2, outlined: false)[31. 3. 2026],
)

#set par(leading: 0.3em)
#heading(level: 2, outlined: false)[Způsob zpracování a kritéria hodnocení:]
Zpracování se řídí obecně závaznými pokyny pro zpracování maturitních prací v požadovaném rozsahu. Řešitel odevzdá na studijním oddělení určenému zástupci vedení školy ve stanoveném termínu dva svázané výtisky projektové dokumentace s podepsaným prohlášením o autorství a jeden poster. Přílohu s dokumentací ve stejném znění, posterem, zdrojovými kódy a dalšími podklady řešitel odevzdá podle pokynů vedoucího práce také elektronicky. Hodnotí se odborné zpracování, užití návrhových vzorů, prezentace při obhajobě a funkcionalita produktu. Posudek vedoucího a oponenta hodnotící samotnou práci získá řešitel k nahlédnutí před obhajobou.

#heading(level: 2, outlined: false)[Popis (povinná část):]
Navrhněte a realizujte novou architekturu Studentského Vývojového Serveru (SVS) postavenou na technologii Docker. Cilem je vytvořit izolované, snadno spravovatelné a reprodukovatelné prostředí pro běh studentských projektů a služeb.

#heading(level: 2, outlined: false)[Upřesnění zadání:]
- Návrh a konfigurace hostitelského systému Linux
- Kontejnerizace klíčových služeb
- Implementace webového rozhraní pro správu kontejnerů
- Zajištění perzistence dat a síťové izolace projektů
- Automatizace nasazení pomocí Docker Compose či skriptů

#heading(level: 2, outlined: false)[Bonus (nepovinná část):]
- Monitorování stavu serveru a zdrojů (např. Grafana)
- Implementace CI/CD procesů pro automatický deployment
- Zabezpečení pomocí reverzní proxy a SSL certifikátů
- Systém automatického zálohování konfiguraci a dat

#heading(level: 2, outlined: false)[Platforma:]
- CSS
- Django
- HTML
- Linux
- Python
- SQL

#v(1fr)

#table(
  columns: (1fr, 1fr, 1fr),
  align: center,
  stroke: none,
  row-gutter: -0.4em,
  [#line(stroke: (dash: "dashed", paint: rgb("#808080")), length: 92%)],
  [#line(stroke: (dash: "dashed", paint: rgb("#808080")), length: 92%)],
  [#line(stroke: (dash: "dashed", paint: rgb("#808080")), length: 92%)],

  [podpis zadavatele], [datum podpisu], [podpis řešitele],
)
