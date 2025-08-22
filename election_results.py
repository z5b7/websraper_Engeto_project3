"""
main.py: třetí projekt do Engeto Online Python Akademie

author: Zdeněk Brabec
email: brabecz57@gmail.com
"""


import requests
import pandas as pd
from bs4 import BeautifulSoup
import sys
import csv
from urllib.parse import urljoin


BASE_URL = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"

# Stáhne obsah stránky ve formátu HTML.
def download_html(url: str) -> str:
    response = requests.get(url)
    response.encoding = "utf-8"
    return response.text

# Vytvoří slovník okresů a jejich URL z hlavní stránky voleb.
def extract_districts(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    districts = {}
    
    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) > 2:
            name = cols[1].text.strip()
            link_tag = cols[3].find("a")
            if link_tag and "href" in link_tag.attrs:
                url = urljoin(BASE_URL, link_tag["href"])
                districts[name] = url
                
    return districts

# Získá seznam obcí v okresu s jejich kódy a odkazy.
def extract_towns(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    towns = []
    
    for row in soup.find_all("tr")[2:]:
        cols = row.find_all("td")
        if len(cols) >= 2:
            link_tag = cols[0].find("a")
            if link_tag and "href" in link_tag.attrs:
                code = link_tag.text.strip()
                name = cols[1].text.strip()
                url = urljoin(BASE_URL, link_tag["href"])
                towns.append({"Kód obce": code, "Název obce": name, "Odkaz": url})
    
    return towns

# Parsuje základní volební statistiky obce: voliči, vydané obálky, platné hlasy.
def parse_basic_stats(soup: BeautifulSoup) -> dict[str, int] | None:
    tables = soup.find_all("table")
    if len(tables) < 3:
        return None

    cells = tables[0].find_all("td")
    try:
        return {
            "Voliči": int(cells[3].text.strip().replace("\xa0", "").replace(" ", "")),
            "Vydané obálky": int(cells[4].text.strip().replace("\xa0", "").replace(" ", "")),
            "Platné hlasy": int(cells[7].text.strip().replace("\xa0", "").replace(" ", "")),
        }
    except (IndexError, ValueError):
        return None

# Získá výsledky hlasování pro jednotlivé politické strany.
def parse_party_votes(soup: BeautifulSoup) -> dict[str, int]:
    tables = soup.find_all("table")
    votes = {}
    
    for table in tables[1:]:
        rows = table.find_all("tr")[2:]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                party = cols[1].text.strip()
                try:
                    count = int(cols[2].text.strip().replace("\xa0", "").replace(" ", ""))
                    votes[party] = count
                except ValueError:
                    continue

    return votes

# Kompletně stáhne a zpracuje výsledky hlasování pro jednu obec.
def get_town_results(town_url: str) -> dict[str, int | dict[str, int]] | None:
    html = download_html(town_url)
    soup = BeautifulSoup(html, "html.parser")
    
    stats = parse_basic_stats(soup)
    if not stats:
        return None

    stats["Hlasy stran"] = parse_party_votes(soup)
    return stats

# Zpracuje data všech obcí v rámci okresu.
def process_district(district_name: str, district_url: str) -> list[dict[str, int]]:
    print(f"Probíhá stahování dat pro okres: {district_name}...")
    
    html = download_html(district_url)
    towns = extract_towns(html)

    results = []
    parties_set = set()

    for town in towns:
        data = get_town_results(town["Odkaz"])
        if data:
            entry = {
                "Kód obce": town["Kód obce"],
                "Název obce": town["Název obce"],
                "Voliči": data["Voliči"],
                "Vydané obálky": data["Vydané obálky"],
                "Platné hlasy": data["Platné hlasy"],
            }
            for party, votes in data["Hlasy stran"].items():
                entry[party] = votes
                parties_set.add(party)
            results.append(entry)

    for entry in results:
        for party in parties_set:
            entry.setdefault(party, 0)

    return results

# Uložení dat do CSV souboru
def export_to_csv(data: list[dict], filepath: str) -> None:
    df = pd.DataFrame(data)
    df.sort_values(by="Název obce", inplace=True)
    df.to_csv(filepath, index=False, encoding="utf-8-sig", sep=";", quoting=csv.QUOTE_NONNUMERIC)
    print(f"Soubor byl úspěšně uložen do: {filepath}")

# Hlavní vstupní bod skriptu - přijímá název okresu a výstupní soubor z argumentů příkazové řádky.
def main() -> None:
    if len(sys.argv) != 3:
        print("Použití: python skript.py 'NÁZEV OKRESU' 'VÝSTUPNÍ SOUBOR.CSV'")
        sys.exit(1)

    district = sys.argv[1]
    output = sys.argv[2]

    main_page_html = download_html(BASE_URL)
    districts = extract_districts(main_page_html)

    if district not in districts:
        print(f"Okres '{district}' nebyl nalezen v seznamu.")
        sys.exit(1)

    data = process_district(district, districts[district])
    export_to_csv(data, output)

if __name__ == "__main__":
    main()

