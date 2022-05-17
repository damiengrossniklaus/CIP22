from random import randint
import pandas
import requests
from bs4 import BeautifulSoup
from lxml import etree
import re
import pandas as pd
import time
from datetime import datetime
import logging
from headers import header

# Spezifiziere Logging Setup
logging.basicConfig(level=logging.INFO, filename="Log/Immoscout_log.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")


def get_urls() -> list[str]:
    """"
    Erstelle eine Liste mit den Links der Übersichtsseiten der Objekte.

    Returns:
        list[str]: Liste mit Links der Übersichtsseiten

    """

    url = 'https://www.immoscout24.ch/de/immobilien/mieten/kanton-bern?pn=1'

    # Finde maximale Seite
    r = requests.get(url, headers=header()) # Der Header wird zufällig aus headers.py generiert
    soup = BeautifulSoup(r.content, 'lxml')
    max_page = int(soup.find_all('div', class_="Box-cYFBPY Flex-feqWzG dpEUFz dCDRxm")[0].text.split("…")[1])

    # Erstelle Liste mit Url's der Seiten
    urls = list()
    for x in range(1, max_page + 1):
        urls.append(f"https://www.immoscout24.ch/de/immobilien/mieten/kanton-bern?pn={x}")

    return urls


def get_object_links(urls: list[str]) -> list[str]:
    """
    Erstelle eine Liste mit den Links der einzelnen Objekte pro Seite.

    Args:
        urls (list[str]): Liste der Objekt-Übersichtsseiten.

    Returns:
        list[string]: Liste mit Links der einzelnen Objekte
    """

    object_links = list()
    for url in urls: # Iteriere durch die Übersichtsseiten und finde alle einzelnen Objekte
        r = requests.get(url, headers=header()) # Der Header wird zufällig aus headers.py generiert
        soup = BeautifulSoup(r.content, 'lxml')
        objects = soup.find_all('article', class_='Wrapper__WrapperStyled-gUcoSG XNoam')
        # Pro Objekt in der Übersichtsseite suche die href und füge sie der objekt_links-Liste hinzu
        for rent_object in objects:
            href = rent_object.find('a', class_='Wrapper__A-kVOWTT lfjjIW').attrs['href']
            if "neubau" in href:  # Objekt mit Link "../de/neubau*/stuck*" --> disallow --> scrape nicht!
                continue
            else:
                object_links.append("https://www.immoscout24.ch" + href)

    return object_links


def parse_object_links(object_links: list[str]) -> pandas.DataFrame:
    """
    Erstelle eine Liste von Dictionaries,
    in welchem jeweils die Attribute der Objekte als Key-Value-Pair gespeichert werden.
    Wandle die finale Liste in ein pandas.DataFrame um und returne dieses.

    Args:
        object_links (list[str]): Liste mit Links der einzelnen Objekte

    Returns:
        pandas.DataFrame: Dataframe mit gescrapten Objekten als Zeilen
    """

    counter = 1 # Zähler Objekte
    page_counter = 1 # Seitenzähler
    appartments = list()

    # Iteriere durch die Links der einzelnen Objekte
    for link in object_links:
        r = requests.get(link, headers=header()) # Der Header wird zufällig aus headers.py generiert
        soup = BeautifulSoup(r.content, 'lxml')
        d = dict()


        # Wenn Objekt nicht mehr verfügbar ist, gehe zum nächsten Objekt
        try:
            not_found = soup.find('h1', text=re.compile('^Objekt nicht mehr verfügbar$')).text
            logging.info(f"Objekt nicht mehr verfügbar: {link}")
            print(f"Objekt nicht mehr verfügbar: {link}")
            continue
        except AttributeError:

            # Rooms
            try:
                # Finde entsprechendes h2 und schaue, ob Zimmer darin erwähnt werden
                rooms = soup.find('h2', class_='Box-cYFBPY ghNSES').text.split(", ")
                if any("Zimmer" in element for element in rooms):
                    d['rooms'] = rooms[0].strip()
                else:
                    d['rooms'] = "No information" # Falls information nicht vorhanden
            except AttributeError as e:
                try:
                    # Falls anderes Layout der Seite und Zimmer sich in einem h1 befinden
                    # Bsp. «BEFRISTETE 3-Zimmerwohnung - Wohnen in der Nähe des Inselspitals»
                    # Suche mit regex nach den Zimmern im h1 text
                    title_heading = soup.find('h1', class_='Box-cYFBPY ehDvcN MainInfo__TitelHeading-n5gykx-1 eSWghm').text
                    d['rooms'] = re.search('\d(.*)-Zimmer', title_heading).group(0)
                    logging.error(f"{e} für rooms - rooms nicht in h2 {link}")
                except AttributeError as e:
                    logging.error(f"{e} für rooms - No Information AttributeError {link}")
                    d['rooms'] = "No information"  # Falls information nicht vorhanden

            # Area
            # Suche in der Tabelle (td's) nach der Zelle mit Wert Wohnfläche
            # nehme das nächste Element = Wert für Wohnfläche
            try:
                d['area'] = soup.find('td', text=re.compile('^Wohnfläche$')).next_sibling.text
            except AttributeError as e:  # Falls Information nicht vorhanden ist.
                logging.error(f"{e} for area - No Information Attribute {link}")
                d['area'] = "No information"

            # Gross rent
            # Suche im entsprechenden h2 nach gross_rent als Text
            try:
                d['gross_rent'] = soup.find('h2', class_='Box-cYFBPY gvrgZr').text.strip()
            except AttributeError as e:
                logging.error(f"{e} for gross_rent - No Information Attribute {link}")
                d['gross_rent'] = "No information"  # Falls Information nicht vorhanden ist

            # Net rent
            # Finde net rent mittels xpath
            try:
                dom = etree.HTML(str(soup))
                d['net_rent'] = dom.xpath('//*[@id="root"]/div[2]/main/div/div[1]/div[2]/div[1]/section/article[4]/table/tbody/tr[3]/td[2]')[0].text.strip().split('\n')[0]
            except IndexError as e:  # Falls Information nicht vorhanden ist.
                logging.error(f"{e} for net_rent - No Information Index {link}")
                d['net_rent'] = "No information"

            # Address
            try:
                # Suche nach p element, in welchem die Adresse ist
                address = soup.find('p', class_='Box-cYFBPY kvbwBB').get_text(separator='\n').split('\n')
                # Schaue wie lange die Adress-Liste (Strasse nicht immer vorhanden)
                if len(address) == 5:
                    d['plz'] = soup.find('p', class_='Box-cYFBPY kvbwBB').get_text(separator='\n').split('\n')[1]
                    d['street'] = soup.find('p', class_='Box-cYFBPY kvbwBB').get_text(separator='\n').split('\n')[0]
                    d['place'] = soup.find('p', class_='Box-cYFBPY kvbwBB').get_text(separator='\n').split('\n')[3]
                else:
                    d['plz'] = soup.find('p', class_='Box-cYFBPY kvbwBB').get_text(separator='\n').split('\n')[0]
                    d['street'] = "No information"
                    d['place'] = soup.find('p', class_='Box-cYFBPY kvbwBB').get_text(separator='\n').split('\n')[2]
            except (AttributeError, IndexError) as e:  # Falls Information nicht vorhanden ist.
                logging.error(f"{e} for Address - No Information {link}")
                d['plz'] = "No information"
                d['street'] = "No information"
                d['place'] = "No information"

            # Build-/Renovation date
            # Suche in der Tabelle (td's) nach der Zelle mit Text Letzte Renovation
            # nehme das nächste Element = Wert für Letzte Renovation
            try:
                d['build_ren_year'] = soup.find('td', text=re.compile('^Letzte Renovation$')).next_sibling.text
            except AttributeError:  # Suche nach Baujahr, wenn letzte Renovation nicht vorhanden.
                try:
                    d['build_ren_year'] = soup.find('td', text=re.compile('^Baujahr$')).next_sibling.text
                except AttributeError:  # Falls Information nicht vorhanden ist.
                    d['build_ren_year'] = "No information"

            # Infos
            # Suche in nach h2 mit Text Beschreibung
            # nehme das nächste Element = Wert für Beschreibung
            try:
                d['infos'] = soup.find('h2', text=re.compile('^Beschreibung$')).next_sibling.text
            except AttributeError:  # Falls Information nicht vorhanden ist.
                d['infos'] = "No information"

            # Balcony Terrace
            # Suche in der Tabelle (td's) nach der Zelle mit Text Balkon/Terrasse/Sitzplatz
            try:
                if soup.find('td', text=re.compile('^Balkon/Terrasse/Sitzplatz$')):
                    d['balcony_terrace'] = True
                else:
                    d['balcony_terrace'] = False
            except AttributeError:  # Falls Information nicht vorhanden ist.
                d['balcony_terrace'] = "No information"

            # Pets
            # Suche in der Tabelle (td's) nach der Zelle mit Text Haustiere erlaubt
            try:
                if soup.find('td', text=re.compile('^Haustiere erlaubt$')):
                    d['pets'] = True
                else:
                    d['pets'] = False
            except AttributeError:  # Falls Information nicht vorhanden ist.
                d['pets'] = "No information"

            # Elevator
            # Suche in der Tabelle (td's) nach der Zelle mit Text Lift
            try:
                if soup.find('td', text=re.compile('^Lift$')):
                    d['elevator'] = True
                else:
                    d['elevator'] = False
            except AttributeError:  # Falls Information nicht vorhanden ist.
                d['elevator'] = "No information"

            # Car spot
            # Suche in der Tabelle (td's) nach der Zelle mit Text Parkplatz
            try:
                if soup.find('td', text=re.compile('^Parkplatz$')):
                    d['car_spot'] = True
                else:
                    d['car_spot'] = False
            except AttributeError:  # Falls Information nicht vorhanden ist.
                d['car_spot'] = "No information"

            # Minergie
            # Suche in der Tabelle (td's) nach der Zelle mit Text Niedrigenergie-Bauweise
            try:
                if soup.find('td', text=re.compile('^Niedrigenergie-Bauweise$')):
                    d['minergie'] = True
                else:
                    d['minergie'] = False
            except AttributeError:  # Falls Information nicht vorhanden ist.
                d['minergie'] = "No information"

            # Wheelchair access
            # Suche in der Tabelle (td's) nach der Zelle mit Text Rollstuhlgängig
            try:
                if soup.find('td', text=re.compile('^Rollstuhlgängig$')):
                    d['wheelchair_access'] = True
                else:
                    d['wheelchair_access'] = False
            except AttributeError:  # Falls Information nicht vorhanden ist.
                d['wheelchair_access'] = "No information"

            # New Building
            # Suche in der Tabelle (td's) nach der Zelle mit Text Neubau
            try:
                if soup.find('td', text=re.compile('^Neubau$')):
                    d['new_building'] = True
                else:
                    d['new_building'] = False
            except AttributeError:  # Falls Information nicht vorhanden ist.
                d['new_building'] = "No information"

            # Washmachine
            # Suche in der Tabelle (td's) nach der Zelle mit Text Waschmaschine
            try:
                if soup.find('td', text=re.compile('^Waschmaschine$')):
                    d['washmachine'] = True
                else:
                    d['washmachine'] = False
            except AttributeError:  # Falls Information nicht vorhanden ist.
                d['washmachine'] = "No information"

            # Dishwasher
            # Suche in der Tabelle (td's) nach der Zelle mit Text Geschirrspühler
            try:
                if soup.find('td', text=re.compile('^Geschirrspüler$')):
                    d['dishwasher'] = True
                else:
                    d['dishwasher'] = False
            except AttributeError:  # Falls Information nicht vorhanden ist.
                d['dishwasher'] = "No information"

            # URL
            d['url_immoscout'] = link

        appartments.append(d)
        print(f"Objekt {counter} gescrapped!")

        # Warte zwischen 2-5 Sekunden mit dem nächsten Request,
        # wenn eine ganze Seite (24 Objekte) gescraped wurden.
        if counter % 24 == 0:
            print(f"Seite {page_counter} gescrapped!")
            page_counter += 1
            counter += 1
            time.sleep(randint(2, 5))
        else:
            counter += 1

    df = pd.DataFrame(appartments)
    return df


def scrape_immoscout():
    # Speichere Startzeit
    start_time = time.time()

    # Führe Funktionen zum Scrappen aus und erstelle Dataframe aus Daten.
    urls = get_urls()
    object_links = get_object_links(urls)
    df = parse_object_links(object_links)

    # Speichere Daten als .csv mit Datum und Zeit als Suffix
    now = datetime.now()
    date_time = now.strftime("%Y%d%m_%H%M%S")
    my_filename = "../Data/src/archive/B_immoscout_" + date_time + "_src.csv"
    df.to_csv(my_filename, index=False)
    # Speichere Daten als neuste Version
    df.to_csv("../Data/src/B_immoscout_src.csv", index=False)

    # Berechne Zeit des Programms in Minuten und Sekunden
    minutes = int((time.time() - start_time) / 60)
    seconds = int(round(((time.time() - start_time) / 60 - minutes) * 60, 0))
    print(f"--- {minutes} Minuten und {seconds} Sekunden ---")


if __name__ == '__main__':
    scrape_immoscout()
