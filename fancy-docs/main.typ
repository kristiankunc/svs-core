#set page(
  paper: "a4",
  margin: (x: 1.8cm, y: 1.5cm),
)
#set text(
  font: "New Computer Modern",
  size: 12pt,
)
#set heading(numbering: "1.")

#set par(
  first-line-indent: 1em,
  spacing: 0.65em,
  justify: true,
)


#let title-page() = {
  align(center)[
    #text(size: 18pt, weight: "bold")[STŘEDOŠKOLSKÁ ODBORNÁ ČINNOST]
    #v(10pt)
    #text(size: 14pt)[Obor: Informatika]

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

Prohlašuji, že jsem svou práci SOČ vypracoval/a samostatně a použil/a jsem pouze prameny a literaturu uvedené v seznamu bibliografických záznamů.

Beru na vědomí, že nejpozději odevzdáním slovesné vědecké práce do veřejné soutěže Středoškolská odborná činnost, stejně jako odevzdáním jejích příloh a dalších připojených děl, např. audiovizuálních, fotografických, výtvarných, architektonických apod. (dále jen „soutěžní dílo“), dochází ke zveřejnění díla podle § 4 odst. 1 zákona č. 121/2000 Sb., autorského zákona, ve znění pozdějších předpisů (dále jen „autorský zákon“). Totéž platí pro pozdější odevzdání doplněného, změněného, upraveného nebo opraveného díla.

Beru na vědomí, že zveřejněním díla, jehož součástí je vynález, se tento vynález stává součástí stavu techniky podle § 5 odst. 1, 2 zákona č. 527/1990 Sb., o vynálezech, průmyslových vzorech a zlepšovacích návrzích, ve znění pozdějších předpisů (dále jen „patentový zákon“), což zakládá překážku pro udělení patentu podle § 3 odst. 1 patentového zákona.

Beru na vědomí, že vyhlašovatel soutěže je podle § 61 odst. 1 autorského zákona per analogiam oprávněn užít soutěžní dílo pro účely zajištění průběhu soutěže, zejména k zajištění transparentnosti soutěže a veřejnosti obhajob soutěžních prací. V odůvodněném rozsahu je tedy vyhlašovatel po dobu účasti autora v soutěži oprávněn zejména:

#list(
  [zhotovovat rozmnoženiny díla, je-li to nezbytné k seznámení účastníků soutěže, porotců nebo veřejnosti se soutěžní prací;],
  [zapůjčit originál nebo rozmnoženinu díla účastníkům soutěže, porotcům nebo veřejnosti. Přitom dbá na bezpečné nakládání s dílem;],
  [vystavovat originál nebo rozmnoženinu díla v průběhu soutěžních přehlídek a doprovodných akcí;],
  [sdělovat dílo veřejnosti v nehmotné podobě, a to především počítačovou nebo obdobnou sítí.],
)



Dále prohlašuji, že při tvorbě této práce jsem použil/a nástroj generativního modelu AI [NÁZEV APLIKACE; WEBOVÁ ADRESA APLIKACE] za účelem [DŮVOD]. Po použití tohoto nástroje jsem provedl/a kontrolu obsahu a přebírám za něj plnou zodpovědnost.

#v(5em)
#grid(
  columns: (1fr, 1fr),
  align: (left, center, right),
  [V Praze \_\_. \_\_. 2026: #box(line(length: 3cm, stroke: (dash: "dotted")))],
)

#pagebreak()

#heading(numbering: none, outlined: false)[Poděkování]
Fanouškům

#pagebreak()

#heading(numbering: none, outlined: false)[Abstrakty]

#pagebreak()

#outline(title: "Obsah")

#pagebreak()

= Jednicka
#lorem(20)

== Další
#lorem(50)

= Dvojka
#lorem(100)
