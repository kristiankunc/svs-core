#set page(
  paper: "a3",
  flipped: false,
  margin: (x: 1.2cm, y: 1cm),
)

#set text(
  font: "New Computer Modern",
  size: 11.5pt,
  lang: "cs",
)

#set par(
  justify: true,
  leading: 1.14em,
)

#show heading: set text(weight: "bold")

#let card(title, body) = block(
  width: 100%,
  breakable: true,
  inset: 10pt,
  radius: 8pt,
  stroke: 0.8pt + black,
)[
  #text(size: 14pt, weight: "bold")[#title]
  #v(4pt)
  #body
]

#let badge(title, value) = block(
  width: 100%,
  inset: 8pt,
  radius: 8pt,
  stroke: 0.8pt + black,
)[
  #align(center)[
    #text(size: 8.5pt)[#title] \
    #text(size: 13pt, weight: "bold")[#value]
  ]
]

#let step(label) = block(
  width: 100%,
  inset: 6pt,
  radius: 6pt,
  stroke: 0.7pt + black,
)[#align(center)[#label]]

#let bullet(items) = list(..items.map(item => [#item]))

#align(center)[
  #grid(
    columns: (1fr, 6.3cm),
    column-gutter: 0.9cm,
    align: (left, right),
    [
      #text(size: 12pt, weight: "bold")[Gymnázium, Praha 6, Arabská 14] \
      #v(2pt)
      #text(size: 26pt, weight: "bold")[Studentský Vývojový Server] \
      #text(size: 15pt)[Platforma pro jednoduché hostování studentských webových projektů]
    ],
    block(
      inset: 8pt,
      radius: 8pt,
      stroke: 0.8pt + black,
    )[
      #set par(justify: false)
      #text(weight: "bold")[Autor:] Kristián Kunc, 4.E \
      #text(weight: "bold")[Vedoucí:] Ing. Daniel Kahoun \
      #text(weight: "bold")[Odevzdání:] Březen 2026 \
      #text(weight: "bold")[Typ práce:] maturitní projekt
    ],
  )
]

#v(0.75cm)

#grid(
  columns: (1fr, 1fr, 1fr),
  column-gutter: 10pt,
  badge("Jazyk a backend", "Python + Django"),
  badge("Správa služeb", "Docker kontejnery"),
  badge("Rozhraní", "CLI + web"),
)

#v(0.45cm)

#card([Shrnutí projektu], [
  SVS je open-source nástroj pro snadné nasazení a správu self-hosted aplikací na linuxovém serveru.
  Cílem je zpřístupnit správu kontejnerových služeb i méně zkušeným uživatelům, a to pomocí
  jednoduchého webového rozhraní a příkazové řádky. Projekt řeší zejména izolaci služeb,
  reprodukovatelné nasazení a snadnou správu šablon běžných aplikací.
])

#v(0.35cm)

#grid(
  columns: (1fr, 1fr),
  column-gutter: 10pt,
  row-gutter: 10pt,

  card([Cíle práce], [
    #bullet((
      [navrhnout moderní architekturu pro hostování studentských projektů,],
      [sjednotit nasazení služeb pomocí Dockeru a předpřipravených šablon,],
      [umožnit správu přes web i CLI bez nutnosti detailní znalosti infrastruktury,],
      [zachovat přehlednost, rozšiřitelnost a jednoduchou správu systému.],
    ))
  ]),

  card([Architektura řešení], [
    #grid(
      columns: (1fr, auto, 1fr, auto, 1fr),
      column-gutter: 4pt,
      align: center + horizon,
      step([Uživatel]), [→], step([Web / CLI]), [→], step([SVS Core]),
    )
    #v(6pt)
    #grid(
      columns: (1fr, auto, 1fr, auto, 1fr),
      column-gutter: 4pt,
      align: center + horizon,
      step([PostgreSQL]), [←], step([Konfigurace]), [→], step([Docker + Caddy]),
    )
    #v(8pt)
    #bullet((
      [Django zajišťuje databázovou vrstvu a webové rozhraní,],
      [Typer poskytuje přehledné CLI příkazy,],
      [Docker izoluje jednotlivé služby a šablony urychlují nasazení.],
    ))
  ]),

  card([Klíčové funkce], [
    #bullet((
      [správa uživatelů a jejich služeb,],
      [zakládání kontejnerů ze service templates,],
      [síťová izolace a práce s Docker sítěmi,],
      [vzdálený SSH přístup,],
      [správa logů a provozních informací,],
      [automatizované testy a linting v CI.],
    ))
  ]),

  card([Použité technologie], [
    #bullet((
      [Python 3.13+ jako hlavní implementační jazyk,],
      [Django 6.0 pro modely, migrace a webovou část,],
      [Typer pro příkazovou řádku,],
      [Docker a Docker Compose pro běh služeb,],
      [PostgreSQL jako databáze,],
      [pytest, mypy, ruff, black a isort pro kontrolu kvality.],
    ))
  ]),

  card([Výsledky a přínosy], [
    #bullet((
      [sjednocené prostředí pro nasazení studentských webů a doprovodných služeb,],
      [nižší chybovost díky šablonám a testům,],
      [lepší reprodukovatelnost konfigurace na Linux serveru,],
      [začátečnicky přívětivá práce s kontejnery bez ruční správy infrastruktury.],
    ))
    #v(6pt)
    #text(weight: "bold")[Další rozvoj:] CI/CD integrace, monitoring, obnova stavu systému a rozšíření katalogu šablon.
  ]),

  card([Výsledek aplikace], [
    #bullet((
      [správa uživatelů, sítí, služeb a šablon,],
      [webové rozhraní a CLI,],
      [testové nasazení na serveru.],
    ))
    #v(6pt)
    #grid(
      columns: (1fr, 1fr),
      column-gutter: 6pt,
      step([registrace uživatele]), step([výběr šablony]),
      step([spuštění služby]), step([správa přes web / CLI]),
    )
  ]),
)

#v(0.35cm)

#card([Řešený problém a přístup], [
  #bullet((
    [škola potřebuje bezpečný hosting pro studentské a učitelské projekty,],
    [ruční správa serveru je náchylná k chybám a obtížně se škáluje,],
    [SVS sjednocuje instalaci, provoz i správu služeb do jednoho systému,],
    [díky šablonám lze rychle nasadit například Django, databázi nebo statický web.],
  ))
])
