# Popis skriptu

Tento Python skript stahuje výsledky voleb do Poslanecké sněmovny 2017 z webu [volby.cz](https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ).  
Pro vybraný okres načte výsledky za všechny obce a uloží je do souboru CSV.

---

## Co skript dělá
- stáhne všechny obce v zadaném okrese
- získá základní volební statistiky  
- načte počty hlasů pro všechny strany
- sloučí vše do tabulky a uloží jako .csv  

---

## Požadavky

- Python 3.10+ (doporučeno)  
- Knihovny uvedené v requirements.txt:

  - requests – stahování HTML stránek  
  - pandas – práce s tabulkovými daty  
  - beautifulsoup4 – parsování HTML  

Instalace knihoven (pokud nejsou dosud nainstalovány):

pip install -r requirements.txt

Další použité moduly (sys, csv, urllib.parse) jsou součástí standardní knihovny Pythonu a není je tedy nutné instalovat.

---

## Spuštění programu

Skript se spouští z příkazového řádku ve tvaru:

python election_results.py "NÁZEV_OKRESU" "vystup.csv"

Příklad použití:

Chci-li stáhnout výsledky pro okres Znojmo a uložit je do souboru vysledky_Znojmo.csv, použijte:

python election_results.py "Znojmo" "vysledky_Znojmo.csv"

Po úspěšném dokončení se na obrazovce zobrazí hláška o uložení dat a ve složce se objeví soubor vysledky_Znojmo.csv.

## Možné chyby a jejich řešení

Okres 'XXXXX' nebyl nalezen v seznamu
→ zkontrolujte správný název okresu (např. "Ostrava-město" místo "Ostrava město")

ModuleNotFoundError: No module named 'requests'
→ spusť pip install requests

ModuleNotFoundError: No module named 'pandas'
→ spusť pip install pandas

ModuleNotFoundError: No module named 'bs4'
→ spusť pip install beautifulsoup4

