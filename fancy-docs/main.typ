#set page(
  paper: "a4",
  margin: (x: 1.8cm, y: 1.5cm),
  number-align: center,
  numbering: "1.",
)

#set page(footer: context {
  let abspage = locate(here()).page()

  if abspage > 4 {
    align(center)[#counter(page).display("1")]
  }
})

#set text(
  font: "New Computer Modern",
  size: 12pt,
  lang: "cs",
)
#set heading(numbering: "1.")

#show heading.where(level: 1): it => {
  set text(size: 14pt, weight: "bold")
  it
  v(12pt)
}

#show heading.where(level: 2): it => {
  set text(size: 13pt, weight: "bold")
  it
  v(12pt)
}

#show heading.where(level: 3): it => {
  set text(size: 13pt, weight: "bold")
  it
  v(12pt)
}

#show raw.where(block: true): it => {
  set text(size: 9pt)
  block(
    fill: luma(245),
    inset: 1em,
    radius: 0.5em,
    width: 100%,
  )[
    #let lines = it.text.split("\n")
    #grid(
      columns: (auto, 1fr),
      column-gutter: 0.5em,
      row-gutter: 0.2em,
      ..lines
        .enumerate()
        .map(((i, line)) => {
          (align(right)[#text(fill: gray, size: 9pt, str(i + 1))], raw(line, block: false, lang: it.lang))
        })
        .flatten()
    )
  ]
}

#set par(
  first-line-indent: (amount: 1.5em, all: true),
  leading: 1.15em,
  justify: true,
)


#let type = sys.inputs.at("type", default: "soc")

#let title-page() = {
  align(center)[
    #text(size: 18pt, weight: "bold")[STŘEDOŠKOLSKÁ ODBORNÁ ČINNOST]
    #v(10pt)
    #text(size: 14pt)[Obor č. 18: Informatika]

    #v(0.5fr)

    #text(size: 20pt, weight: "bold")[Studentsý Vývojový Server] \
    #v(10pt)
    #text(size: 20pt, weight: "bold")[Selfhosted Virtual Stack]
  ]

  v(1fr)

  align(left)[
    #text(size: 16pt)[
      Autor: Kristián Kunc \
      Škola: Gymnázium, Praha 6, Arabská 14 \
      Kraj: N \
      Konzultant: N \
      Rok: 2025
    ]
  ]
}

#let mp-page() = {
  grid(
    columns: (0.3fr, 0.7fr),
    column-gutter: 1em,
    image("img/gyarab_logo.png", width: 2cm),
    align(left)[
      #text(size: 14pt, weight: "bold")[Gymnázium, Praha 6, Arabská 14] \
      předmět Programování, vyučující Ing. Daniel Kahoun
    ],
  )

  v(10cm)

  align(center)[
    #text(size: 20pt, weight: "bold")[
      Studentsý Vývojový Server \
    ]
  ]

  v(1fr)

  grid(
    columns: (0.5fr, 0.5fr),
    align(left)[
      #text(size: 14pt)[Kristián Kunc, 4.E]
    ],
    align(right)[
      #text(size: 14pt)[Duben 2025]
    ],
  )
}

#if type == "soc" [
  #title-page()
] else [
  #mp-page()
]

#if type == "soc" [
  #pagebreak()

  #heading(numbering: none, outlined: false)[Prohlášení]

  Prohlašuji, že jsem svou práci SOČ vypracoval samostatně a použil jsem pouze prameny a literaturu uvedené v seznamu bibliografických záznamů.

  Beru na vědomí, že nejpozději odevzdáním slovesné vědecké práce do veřejné soutěže Středoškolská odborná činnost, stejně jako odevzdáním jejích příloh a dalších připojených děl, např. audiovizuálních, fotografických, výtvarných, architektonických apod. (dále jen „soutěžní dílo“), dochází ke zveřejnění díla podle § 4 odst. 1 zákona č. 121/2000 Sb., autorského zákona, ve znění pozdějších předpisů (dále jen „autorský zákon“). Totéž platí pro pozdější odevzdání doplněného, změněného, upraveného nebo opraveného díla.

  Beru na vědomí, že zveřejněním díla, jehož součástí je vynález, se tento vynález stává součástí stavu techniky podle § 5 odst. 1, 2 zákona č. 527/1990 Sb., o vynálezech, průmyslových vzorech a zlepšovacích návrzích, ve znění pozdějších předpisů (dále jen „patentový zákon“), což zakládá překážku pro udělení patentu podle § 3 odst. 1 patentového zákona.

  Beru na vědomí, že vyhlašovatel soutěže je podle § 61 odst. 1 autorského zákona per analogiam oprávněn užít soutěžní dílo pro účely zajištění průběhu soutěže, zejména k zajištění transparentnosti soutěže a veřejnosti obhajob soutěžních prací. V odůvodněném rozsahu je tedy vyhlašovatel po dobu účasti autora v soutěži oprávněn zejména:

  #list(
    [zhotovovat rozmnoženiny díla, je-li to nezbytné k seznámení účastníků soutěže, porotců nebo veřejnosti se soutěžní prací;],
    [zapůjčit originál nebo rozmnoženinu díla účastníkům soutěže, porotcům nebo veřejnosti. Přitom dbá na bezpečné nakládání s dílem;],
    [vystavovat originál nebo rozmnoženinu díla v průběhu soutěžních přehlídek a doprovodných akcí;],
    [sdělovat dílo veřejnosti v nehmotné podobě, a to především počítačovou nebo obdobnou sítí.],
  )



  Dále prohlašuji, že při tvorbě této práce jsem použil nástroj generativního modelu AI Github Copilot; https://github.com/copilot za účelem [???]. Po použití tohoto nástroje jsem provedl/a kontrolu obsahu a přebírám za něj plnou zodpovědnost.

  #v(5em)
  #grid(
    columns: (1fr, 1fr),
    align: (left, center),
    [V Praze dne: #box(line(length: 2cm, stroke: 0.8pt)) 2026],
    [
      #box(line(length: 5cm, stroke: 0.8pt)) \
      Kristián Kunc
    ],
  )
]

#pagebreak()

#heading(numbering: none, outlined: false)[Poděkování]
Fanouškům

#pagebreak()

#heading(numbering: none, outlined: false)[Anotace]
Souhrn je pomyslnou vizitkou celé práce. Po jeho přečtení by čtenáři mělo být jasné, čím se práce zabývá a jaké jsou její zásadní výstupy. Souhrn sumarizuje celou práci, tedy včetně cílů, metodiky, nejdůležitějších výsledků a závěrů. Doporučujeme odpovědět na otázky Co? Proč? Jak? a S jakým výsledkem? jste ve své práci dělali. Souhrn pište až na samotném závěru práce v rozsahu 5 až 10 vět.

#heading(numbering: none, outlined: false)[Klíčová slova]
3-5 klíčových slov oddělených středníkem v abecedním pořadí. Klíčová slova více definují zaměření práce, a proto není vhodné, aby byla totožná se slovy, která se vyskytují v názvu práce.

#heading(numbering: none, outlined: false)[Abstract]
#lorem(50)

#heading(numbering: none, outlined: false)[Keywords]
#lorem(5)


#pagebreak()

#outline(title: "Obsah")

#pagebreak()

= Úvod
#lorem(20)

= Teoretická část

TODO: intro

== Hosting a selfhosting

Při vývoji jakékoliv aplikace je potřeba zvážit způsob distribuce a nasazení. Typicky lze zvolit mezi lokálním spuštěním na zařízení uživatele nebo nasazením na server. Právě při nasazení na server se často setkáváme s pojmem "hosting". Hosting je služba, která umožňuje umístit proces aplikace na server, který je stále připojen k internetu, a tím k ní umožnit přístup odkudkoliv. Exstují různé typy hostingu:

+ VPS (Virtual Private Server) - poskytuje virtuální server, který je izolovaný od ostatních uživatelů, ale sdílí fyzický hardware s ostatními VPS. Uživatel má plnou kontrolu nad svým systémem a může instalovat vlastní software. Je to flexibilní řešení, ale vyžaduje určité technické znalosti.

+ Dedikovaný server - poskytuje fyzický server, který je zcela vyhrazen pro jednoho uživatele. Uživatel má plnou kontrolu nad hardwarem a softwarem, ale je to nákladnější řešení než VPS.

+ Cloud hosting - poskytuje škálovatelnou a flexibilní infrastrukturu. Nabízí typicky širokou škálu služeb, jako jsou virtuální servery, úložiště a databáze. Uživatel platí pouze za využité zdroje, což může být ekonomické řešení pro různé typy aplikací.

TODO: selfhosting

== Docker a kontejnerizace

Docker @merkel2014docker je platforma pro vývoj, distribuci a provozování aplikací. Kontejnerizace, kterou Docker využívá, se staví na pomezí virtualizace a holého hardwaru. Na rozdíl od tradiční virtualizace, která vytváří kompletní virtuální stroj s vlastním operačním systémem, kontejnerizace umožňuje spouštět aplikace v izolovaných prostředích, která sdílejí jádro hostitelského operačního systému. To přináší několik výhod:

+ Rychlost: Kontejnery jsou lehké a spouštějí se rychleji než virtuální stroje, protože nevyžadují načítání celého operačního systému.
+ Efektivita: Kontejnery sdílejí jádro hostitelského operačního systému, což umožňuje efektivnější využití zdrojů.
+ Přenositelnost: Kontejnery jsou přenosné mezi různými prostředími, což usnadňuje vývoj, testování a nasazení aplikací.
+ Izolace: Kontejnery poskytují izolaci mezi aplikacemi, což zvyšuje bezpečnost a stabilitu.

Filozofie Dockeru spočívá v tom, že aplikace by měla být balena s veškerými závislostmi do jednoho kontejneru, což umožňuje konzistentní běh aplikace bez ohledu na prostředí, ve kterém je nasazena. Toho se docílí deklarativním popisem prostředí a konfigurace aplikace pomocí souboru Dockerfile, který obsahuje instrukce pro sestavení kontejneru.

```dockerfile
# Volba základního obrazu (image), v tomto případě Debian Trixie (13)
FROM debian:trixie

# Instalace potřebných balíčků a závislostí
RUN apt-get update && apt-get install -y \
    python3 \ # Python 3 pro běh aplikace
    python3-pip \ # Pip pro správu Python balíčků

# Nastavení pracovního adresáře v kontejneru
WORKDIR /app

# Kopírování souborů aplikace do kontejneru
COPY . /app

# Instalace Python závislostí z requirements.txt
RUN pip3 install -r requirements.txt

# Exponování portu, na kterém aplikace běží
EXPOSE 8000

# Definice příkazu pro spuštění aplikace
CMD ["python3", "app.py"]
```

Docker obrazy (images) fungují na principu vrstev (layers), kde každá instrukce v Dockerfile vytváří novou vrstvu. Tyto vrstvy jsou ukládány a mohou být znovu použity, což zvyšuje efektivitu při sestavování. Další vrstvení také probíhá při volbě základního obrazu, jakmile více obrazů sdílí stejné vrstvy, Docker je znovu použije, což urychluje proces sestavení a snižuje velikost výsledného obrazu.

Postavený obraz lze spustit jako kontejner, který představuje jeho instanci. Kontejnery jsou izolované, ale mohou komunikovat s ostatními kontejnery a hostitelským systémem prostřednictvím sítí a svazků (volumes). To umožňuje vytvářet komplexní aplikace složené z více služeb, které spolu spolupracují.

== Existující řešení

= Implementace

== Struktura projektu

== Uživatelé a oprávnění

== Docker abstrakce

=== Template systém

=== Service

=== Síťová architektura

== Systémové kontejnery

== Uživatelské rozhraní

=== CLI

=== Webové rozhraní

== Testování

=== Unit testy

=== Zkušební nasazení

== Dokumentace

=== Docstringy

=== Zensical

= Závěr

== Dosažené výsledky

== Porování s existujícími řešeními

== Budoucí vývoj

#pagebreak()


#lorem(100)
@Madje_Typst
#lorem(30)


#bibliography("main.bib", style: "iso690-numeric-brackets-cs.csl")
