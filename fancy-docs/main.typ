#set page(
  paper: "a4",
  margin: (left: 3cm, right: 2.5cm, y: 1.5cm),
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
      Rok: 2026
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
      #text(size: 14pt)[Únor 2026]
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

+ `VPS (Virtual Private Server, virtuální privátní server)` - poskytuje virtuální server, který je izolovaný od ostatních uživatelů, ale sdílí fyzický hardware s ostatními `VPS`. Uživatel má plnou kontrolu nad svým systémem a může instalovat vlastní software. Je to flexibilní řešení, ale vyžaduje určité technické znalosti.

+ Dedikovaný server - poskytuje fyzický server, který je zcela vyhrazen pro jednoho uživatele. Uživatel má plnou kontrolu nad hardwarem a softwarem, ale je to nákladnější řešení než VPS.

+ Cloud hosting - poskytuje škálovatelnou a flexibilní infrastrukturu. Nabízí typicky širokou škálu služeb, jako jsou virtuální servery, úložiště a databáze. Uživatel platí pouze za využité zdroje, což může být ekonomické řešení pro různé typy aplikací.

+ `Selfhosting` - znamená, že uživatel sám hostuje svou aplikaci na svém vlastním zařízení nebo serveru. To může být výhodné z hlediska kontroly nad daty a konfigurací, ale vyžaduje technické znalosti a zajištění bezpečnosti a dostupnosti.

== Docker a kontejnerizace

`Docker` @merkel2014docker je platforma pro vývoj, distribuci a provozování aplikací. Kontejnerizace, kterou Docker využívá, se staví na pomezí virtualizace a holého hardwaru. Na rozdíl od tradiční virtualizace, která vytváří kompletní virtuální stroj s vlastním operačním systémem, kontejnerizace umožňuje spouštět aplikace v izolovaných prostředích, která sdílejí jádro hostitelského operačního systému. To přináší několik výhod:

+ Rychlost: Kontejnery jsou lehké a spouštějí se rychleji než virtuální stroje, protože nevyžadují načítání celého operačního systému.
+ Efektivita: Kontejnery sdílejí jádro hostitelského operačního systému, což umožňuje efektivnější využití zdrojů.
+ Přenositelnost: Kontejnery jsou přenosné mezi různými prostředími, což usnadňuje vývoj, testování a nasazení aplikací.
+ Izolace: Kontejnery poskytují izolaci mezi aplikacemi, což zvyšuje bezpečnost a stabilitu.

Filozofie `Dockeru` spočívá v tom, že aplikace by měla být balena s veškerými závislostmi do jednoho kontejneru, což umožňuje konzistentní běh aplikace bez ohledu na prostředí, ve kterém je nasazena. Toho se docílí deklarativním popisem prostředí a konfigurace aplikace pomocí souboru _Dockerfile_, který obsahuje instrukce pro sestavení _Docker image_.

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

_Docker image_ funguje na principu vrstev. Každá instrukce v souboru _Dockerfile_ vytváří novou vrstvu, která je uložena a může být znovu použita při dalším sestavení. Tento mechanismus zvyšuje efektivitu sestavování. Vrstvení probíhá také při použití základního _image_. Pokud více _Docker images_ sdílí stejné vrstvy, Docker je neukládá duplicitně, ale znovu je využije. Tím dochází ke zrychlení sestavení a snížení velikosti výsledné _Docker image_

Postavený _image_ lze spustit jako kontejner, který představuje jeho instanci. Kontejnery jsou izolované, ale mohou komunikovat s ostatními kontejnery a hostitelským systémem prostřednictvím _volumes_ a síťí. _Volumes_ umožňují sdílet data mezi kontejnery a hostitelským systémem, což je užitečné pro uchovávání dat nebo konfigurace mimo kontejner. Síťové možnosti Dockeru umožňují kontejnerům komunikovat mezi sebou a hostitelským adaptérem.

TODO: extend?

== Existující řešení

Uživatelských rozrhaní pro správu `Dockeru` existuje nespočet. Mezi nejznámější patří `Portainer` @portainerDocs, který nabízí webové rozhraní pro správu celého systému a je schopen zastopit příkazovou řádku ve většině případů.

Nicméně, většina těchto řešení je navržena pro profesionální a neimplementují žádnou abstrakci nad `Dockerem`, což může být pro méně zkušené uživatele komplikované, protože stále vyžadují kompletní znalost `Dockeru` a jeho konceptů.

= Implementace

Projekt je implementován v programovacím jazyce `Python 3.13` a využivá framework `Django 6` pro vývoj webováho rozhraní.

== Struktura projektu

Projekt je rozdělen do několika hlavních částí:
+ `svs-core` - obsahuje samotnou aplikaci a všechny funkční částí.
+ `web` - obsahuje webové rozhraní pro správu a interakci s aplikací.
+ `docs` - obsahuje uživatelskou dokumentaci a další doprovodné materiály.

Jádro aplikace je publikováno jako `pip` balíček (https://pypi.org/project/svs-core/), což umožňuje snadnou distribuci a instalaci. Projekt je open-source a jeho zdrojový kód je dostupný na GitHubu (https://github.com/kristiankunc/svs-core). Projekt je licencován pod licencí `GPL-3.0` @gplv3.

Aplikace závisí na `PostgreSQL` databázi pro ukládání dat, `Docker engine` pro správu kontejnerů a `Caddy` pro reverzní proxy a správu SSL certifikátů.

== Uživatelé a oprávnění

Každý uživatel aplikace je identifikován svým uživatelským jménem v databázi. Na tento účet je pak navázán systémový uživatel se stejným jménem. Tento uživatelský učet je použit pro připojení přes `SSH (Secure Shell)` a nastavování oprávnění.

Uživatelé jsou rozděleni do dvou hlavních skupin: `admin` a `user`. `Admin` má plný přístup ke všem funkcím a nastavením aplikace, zatímco `user` má omezený přístup pouze k funkcím, které jsou nezbytné pro běžné používání.

=== Linux oprávnění

Běžný systémový uživatel nemá přímý přístup k
_Docker engine_, ten je zabezpečený pomocí systémové skupiny `docker`. Tento přístup by totiž umožnil uživateli prakticky získat `root` oprávnění na celém systému @dockerdAttackSurface. Proto je na vykonávání citlivých operací používan systémový uživatel `svs`, který má všechna potřebná oprávnění. Tento uživatel vytváří a spravuje kontejnery, sítě, soubory a další zdroje potřebné pro běh aplikace.

Na tohoto uživatele aplikace interně přepíná pomocí `sudo` a spouští všechny citlivé operace pod jeho účtem. Běžní uživatelé ale nemají k tomuto uživateli přímý přístpup a nemohou se k němu přihlásit, což zajišťuje bezpečnost systému.

== Docker abstrakce

Pro zjednodušení práce s `Dockerem` a skrytí jeho komplexity před uživatelem, je vytvořena vlastní vrstva abstrakce, která schová mnohé komplexní koncepty `Dockeru` a poskytuje jednodušší pro jeho správu.

=== Šablony

Vzhledem k tomu, že každá uživatelská služba, která by měla být spuštěná v `Dockeru`, by potřebovala vlastní _Dockerfile_, je vytvořen systém šablon, které umožňují definovat různé typy šlužby a jejich konfigurace. Tyto šablony jsou definovány pomocí `JSON` souborů, které obsahují všechny potřebné informace pro sestavení a spuštění kontejneru, včetně konfigurace sítě, portů a dalších parametrů.

Šablony jsou navrženy tak, aby byly snadno rozšiřitelné a přizpůsobitelné pro různé typy služeb. Uživatelé mohou vytvářet vlastní šablony nebo upravovat stávající, což umožňuje velkou flexibilitu při správě svých služeb.

Tyto šablony se dělí na dvě kategorie

==== Statické šablony

Statické šablony nezávisí na zdrojovém kódu dodaným uživatelem. Jsou předem definované a používají již existujicí _Docker images_. Jsou vhodné pro běh služeb, které nevyžadují žádnou specifickou konfiguraci nebo přizpůsobení, jako jsou například databáze, webové servery nebo jiné běžné služby.

==== Dynamické šablony

Dynamické šablony jsou navrženy tak, aby umožňovaly větší flexibilitu a přizpůsobení. Tyto šablony typicky závisí na zdrojovém kódu a výsledný _Docker image_ je sestaven pro každou uživatelskou službu individuálně. Jsou vhodné pro běh vlastních aplikací, které vyžadují specifickou konfiguraci nebo závislosti, které nejsou pokryty statickými šablonami.

=== Service

=== Síťová architektura

== Systémové kontejnery

== Uživatelské rozhraní

=== CLI

=== Webové rozhraní

== Testování

TODO: intro

=== jednotkové testy

Zdrojový kód obsahuje množství jedntkových testů, které ověřují správnou funkčnost jednotlivých funkcí a metod. Tyto testy jsou navrženy tak, aby pokryly co největší část kódu a odhalily případné chyby v logice.

Testy jsou zajištěny knihovnou `Pytest` @pytest. Jednotkové testy jsou organizovány do samostatných souborů a adresářů, které odpovídají struktuře projektu. Každý test kontroluje konkrétní aspekt funkcionality, například správné zpracování vstupů, očekávané výstupy nebo chování v případě chyb.

Jednotkové testování funguje na principu izolace, což znamená, že každý test by měl být nezávislý na ostatních testech a neměl by ovlivňovat stav systému. Proto se často používá maskování externích závislostí, jako jsou databáze, síťové služby nebo systémové volání. U těchto závislostí se pak ověří, zda jsou volány s očekávanými parametry, což zajišťuje, že testovaná funkce správně interaguje s okolním systémem.

V ukázce níže se nachází test pro funkci `create_user`, která je zodpovědná za vytvoření nového uživatele v systému. Test ověřuje, že uživatel je správně vytvořen a uložen do databáze, a také kontroluje, že jsou volány správné funkce pro vytvoření `Docker` sítě a systémového uživatele.

```python
def test_create_user_success(
  self, mock_docker_network_create, mock_system_user_create
):
  username = "testuser"
  password = "password123"

  # Volání testované metody pro vytvoření uživatele
  user = User.create(name=username, password=password)

  # Kontrola základních atributů uživatele
  assert user.name == username
  assert User.objects.get(name=username) is not None

  # Kontrola zavolání závislostí (Docker síť a systémový uživatel)
  mock_docker_network_create.assert_called_once_with(
    username,
    labels={"svs_user": username},
  )
  mock_system_user_create.assert_called_once_with(username, password, False)
```

=== Zkušební nasazení

Gyarab zkušební nasazení.

== Distribuce

Pip

== Dokumentace

=== Docstringy

V rámci zachování udržitelného a přehledného kódu do budoucna, je kód osazen rozsáhlou dokumentací. Dokumentace je psána přímo v kódu pomocí konvence `docstring` @pep257docstrings. `Docstringy` jsou speciální textové řetězce, které se umisťují na začátek modulů, tříd a metod a slouží k popisu jejich účelu, funkcionality a způsobu použití. Konkrétně jsou použity `Google style docstrings` @googleDocstringStyle.

V ukázce níže se nachází `docstring` pro funkci `get_uid`, která vrací _UID (User ID, uživatelské ID)_ pro zadané uživatelské jméno. `docstring` obsahuje popis funkce, její argumenty, návratovou hodnotu a možné výjimky, které může funkce vyvolat.

```python
def get_uid(username: str) -> int:
  """Returns the UID of the specified username.

  Args:
    username (str): The username to look up.

  Returns:
    int: The UID of the user.

  Raises:
    KeyError: If the user does not exist.
  """
  ...
```

Tento typ dokumentace je rozšířený a zjednodušuje pochopení kódu pro jeho uživatele a rychlou referenci.

=== Zensical

Pro stavbu uživatelské dokumentace je použit generátor `Zensical` @zensical. Ten umožňuje psát dokumentaci v jazyku `Markdown`, který je následně zpracován do přehledné a strukturované formy na statcikém webu.

Hlavní výhodou využití generátorů dokumentace, je automatické generování dokumentace z `docstringů` a dalších zdrojů, což zajišťuje, že dokumentace je vždy aktuální a konzistentní s kódem.

Kromě referenční dokumentace, obsahuje uživatelská dokumentace také instalační instrukce, návody k použití, seznam změn a další důležité informace pro uživatele.


= Závěr

== Dosažené výsledky

== Porování s existujícími řešeními

== Budoucí vývoj

#pagebreak()


#lorem(100)
@Madje_Typst
#lorem(30)


#bibliography("main.bib", style: "iso690-numeric-brackets-cs.csl")
