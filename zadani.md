# Studentský hosting

Vytvořte systém pro hostování webových projektů pro studenty a učitele na Gymnáziu Arabská.

## Funkcionalita

- Instalace na Linux (ideálně Ubuntu Server - stabilní a má poměrně up to date balíčky na rozdíl od Debianu)
- Registrace přes webové rozhraní, pro studenty a učitele gyarab
- Admin přístup
  - Možnost smazat, zastavit jakoukoliv službu
  - Přesun služby na jiného uživatele
  - Hromadné mazání služeb a uživatelů (ukončení studia ročníku)
    - Možnost některé služby uzamknout proti smazání (ty, co budeme chtít zachovat)
  - Přehled a základní statistiky služeb
    - Seznam běžících služeb, CPU load, HDD/RAM usage, etc.
  - Self-diagnostika
- Přístup k logům jednotlivých služeb (User) nebo i systému (Admin)

## Use cases

- Hostování
  - Statický web
  - Django aplikace
  - PHP aplikace
  - Wordpress aplikace
  - DB (PostgreSQL/MySQL), ideálně včetně PGAdmin/PHPMyAdmin
  - apod.
- Možnost nahrávání souborů
  - Synchronizace přes Git(Hub), případně implementovat nějaké CI/CD workflow
  - FTP/SFTP
  - (?) možná GoogleDisk, nebo navrhnout nějakou formu abstrakce tak, aby bylo možné další metody nahrávání souborů přidávat
- SSH přístup
  - správa SSH klíčů

## Další požadavky

- Čitelný, dobře strukturovaný, "čistý" kód
- Minimalizovat množství dependencies
- Kvalitní dokumentace, ideálně přímo v kódu (pydoc nebo podobné)
  - Automatické generování online
  - Soustředit se na dokumentaci kódu více než na "tištěnou" dokumentaci
- Zpracované detailní návody pro jednotilvé use cases
- Také nezanedbat vizuální stránku, ať to má celé pěkný, studentský "vibe":-)

## Poznámky

- Navázat spolupráci s vybraným studentem či studenty s nižších ročníků a rovnou je zaučovat ve správě systému
- Incident s jailbreaknutým dockerem (více info Dejmal Reuel 3.E / Václav Chalupníček)
  - https://github.com/gyarab/Docker_exploit
- IOČ - Aplikace pro orientační běh (Milan Koblic)
  - Bude třeba hostovat, může se na tom testovat
