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

#set par(
  first-line-indent: (amount: 1.5em, all: true),
  leading: 1.5em,
  justify: true,
)



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

#title-page()
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

= Jednicka
#lorem(20)

== Další
#lorem(50)

#pagebreak()

= Dvojka
#lorem(100)
@Madje_Typst
#lorem(30)


#bibliography("main.bib", style: "iso690-numeric-brackets-cs.csl")
