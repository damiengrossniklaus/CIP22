# A_scrape_homegate.py
import pandas
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import time
from datetime import datetime
from headers import header




def get_urls(url: str) -> list[str]:
    '''
    Erstellt eine Liste mit URLs, welche gescraped werden sollen.

    :param url: str: Homegate URL mit Suchkriterium (Kanton Bern)
    :return: list[str]: Liste mit URLs welche jeweils mehrere (ca. 20) Mietobjekte aufführen.
    '''
    # Der gesamte HTML Code der url wird in homegate_url gespeichert:

    homegate_html = requests.get(url, headers=header()).text

    #Der HTML Code wird mithilfe eines lxml Parsers für bs4 leserlich gemacht:
    homegate_soup = BeautifulSoup(homegate_html, "lxml")
    maxpage = int(homegate_soup.find_all("div",
                               class_="HgPaginationSelector_paginatorBox_15QHK")[-1].text.replace("12...", ""))

    #Initialisieren einer leeren Liste
    homegate_urls = []
    #Loop von 1 bis maxpage + 1: erstellt URLs
    for i in range(maxpage + 1):
        homegate_url = f"https://www.homegate.ch/mieten/immobilien/kanton-bern/trefferliste?ep={i}"
        homegate_urls.append(homegate_url)

    return homegate_urls



def get_object_links(homegate_urls: list) -> list[str]:
    '''
    Erstellt eine Liste mit Mietobjekt-URLs, welche gescraped werden sollen.

    :param homegate_urls: list[str]: Liste mit urls, welche jeweils ungefähr* 20 Mietobjekte enthalten.
    *ungefähr weil teils Werbeseiten dazwischen schalten oder nicht alle Seiten bis nach unten "gefüllt" sind.
    :return: list[str]: Liste mit urls zu den einzelnen Mietobjektseiten.
    '''

    # Initialisieren einer leeren Liste
    print('-' * 50 + "\n"  
          "Collecting URLs...")

    object_links = []

    #Loop der durch die einzelnen urls aus get_object_urls iteriert.
    for homegate_url in homegate_urls:
        #jede url wird mithilfe von requests.get beim server angefragt und mit der text methode "gesäubert".
        #Zusätzlich wird mit headers = header() einer von drei headern eingesetzt, dies soll zufällig geschehen.
        homegate_html = requests.get(homegate_url, headers = header()).text
        #Mit bs4 wird der Code lesbar und scrapebar gemacht. Es wird wieder ein lxml parser eingesetzt.
        homegate_soup = BeautifulSoup(homegate_html, "lxml")

        #Bezahlte Angebote werden in einer anderen Klasse geführt als unbezahlte. Deshabl werden zwei Loops
        #durchgeführt.
        for i in homegate_soup.find_all("a", class_="ListItemTopPremium_itemLink_11yOE"):
            object_links.append("https://www.homegate.ch" + i.get("href"))
        for i in homegate_soup.find_all("a", class_="ListItem_itemLink_30Did"):
            object_links.append("https://www.homegate.ch" + i.get("href"))

    print(f"Finished collecting URLs. {len(object_links)} URLs collected. \n"
          '-' * 50)

    return object_links



def parse_object_links(object_links: list[str]) -> pandas.DataFrame:
    '''
    Erstellt einen pandas.DataFrame mit Attributen zu einzelnen Mietobjekten.

    :param object_links: list[str]: Liste mit URLs zu den Mietobjekten
    :return: pandas.DataFrame: Dataframe mit len(object_links) rows und 25 columns.
    '''
    apartments = []
    ap_counter = 1
    page_counter = 1
    for i in object_links:
        start_time = time.time()

        # Initiierung eines leeren Dictionaries für jedes Apartement
        d = {}

        # Die URL zum Mietobjekt wird dem Dict. hinzugefügt:
        d["url"] = i

        # Anfrage für Resource "i":
        # Mit headers = header() wird die header Funktion aufgerufen, welche zufällig einen header zurückgiebt.
        # Dies aufgrund einer Restriktion von homegate.ch. So soll eine Sperrung umgangen werden.
        ap = requests.get(i, headers = header()).text

        # Parsen des HTMLs mittels lxml-Parser:
        ap_soup = BeautifulSoup(ap, "lxml")



        # Homegate schränkt die Anzahl aufrufe pro Client stark ein. Alle par Seitenaufrufe wird ein
        # Turing Test durchgeführt. Das If-Statement soll diese Seite erkennen, falls "Attention required" im HTML Code
        #erscheint, soll das Skript pausiert werden und nach 4 Minuten erneut probiert werden.
        if "Attention Required!" in ap_soup.text:
            now = datetime.strftime(datetime.fromtimestamp(time.time()), format = "%H:%M:%S")
            print(f"cloudflare error, {ap_counter} apartements scraped at {now}")

            time.sleep(240)
            ap = requests.get(i, headers = header()).text
            # parsing the html code using lxml-parser:
            ap_soup = BeautifulSoup(ap, "lxml")



        # Erstellen von (Listen mit) Elementen:
        address = ap_soup.find_all("address", class_="AddressDetails_address_3Uq1m")
        gross_rent = ap_soup.find("div", class_="SpotlightAttributes_value_2njuM")
        rooms = ap_soup.find_all("div", class_="SpotlightAttributes_value_2njuM")
        area = ap_soup.find_all("div", class_="SpotlightAttributes_value_2njuM")
        balcony = ap_soup.find_all("ul", class_="FeaturesFurnishings_list_1HzQj")
        build_year = ap_soup.find_all(class_="CoreAttributes_coreAttributes_2UrTf")
        description = ap_soup.find(class_="hg-listing-details")
        listingID = ap_soup.find(class_="ListingTechReferences_techReferencesList_3qCPT")
        if description != None:
            description = description.text

            # Die Nettomiete wird nicht immer aufgeführt und die Struktur nicht immer dieselbe. Die RegEx soll die
            # 5 folgenden Charaktere wiedergeben und diese dem Dict hinzufügen.
            if "Nettomiete" in description:
                try:
                    net_rent = re.search("Nettomiete:CHF (.{5})", description).group(1)
                    d["net_rent"] = net_rent
                except AttributeError:
                    d["net_rent"] = "no information"
            else:
                d["net_rent"] = "no information"




        # Iterieren durch die Address-Liste. Die genaue Adresse ist nicht immer gegeben. Deshalb
        # wird nach dem Trennkomma gesucht, welches Strassenname und PLZ/Ort trennt und dann mittels RegEx
        # zum Dictionary hinzugefügt.
        for i in address:
            if "," in i.text:
                d["plz"] = re.sub("\D+", "", i.text.split(",")[1])
                d["place"] = re.sub("\d+", "", i.text.split(",")[1])
                d["street"] = i.text.split(",")[0]
            else:
                d["street"] = "no information"
                d["place"] = re.sub("\d+", "", i.text.split(",")[0])
                d["plz"] = re.sub("\D+", "", i.text.split(",")[0])

        # Hinzufügen der Bruttomiete zum Dictionary, wie bei der Nettomiete mittels Regex.
        if gross_rent != None:
            try:
                d["gross_rent"] = float(re.sub("\D+", "", gross_rent.text))
            except ValueError:
                d["gross_rent"] = "no information"


        # Hinzufügen der Zimmerzahl zum Dict
        if len(rooms) > 0:
            try:
                d["rooms"] = float(rooms[1].text)
            except (IndexError, ValueError):
                d["rooms"] = "no information"
        else:
            d["rooms"] = "no information"

        # Die Fläche ist nicht immer gegeben, deshalb wird zuerst die Länge der Liste geprüft. Wenn diese
        # 3 Elemente lang ist, wird das dritte Element extrahiert, gesplittet und dann in einen flaot64 umgewandelt.
        if len(area) == 3:
            d["area"] = float(area[2].text.split(" ")[1])
        else:
            d["area"] = 0

        # Es soll nach dem letzten Rennovationsjahr gesucht werden. Wenn es kein Rennovationsjahr gibt, soll
        # das Bauhjahr stattdessen verwendet werden. Wenn keines gegeben ist, soll "no information" dem Dict
        # hinzugefügt werden.

        for i in build_year:
            if "Renovationsjahr" in i.text:
                try:
                    d["build_ren_year"] = int(re.search("Renovationsjahr: (\d{4})", i.text).group(1))
                except:
                    AttributeError
            elif "Baujahr" in str(build_year):
                try:
                    d["build_ren_year"] = int(re.search("Baujahr: (\d{4})", i.text).group(1))
                except:
                    AttributeError
            else:
                d["build_ren_year"] = "no information"

        # Balkon wird als bool dem Dict hinzugefügt.
        if "Balkon / Terrasse" in str(balcony):
            d["balcony_terrace"] = True
        else:
            d["balcony_terrace"] = False


        #Die gesamte Description wird dem Dictionary hinzugefügt.
        d["description"] = description

        # Um Duplikate zu vermeiden, wird die Inseratenummer mittels RegEx dem Dict hinzugefügt.
        try:
            d["objectID"] = re.search("Inseratenummer(\d*)", listingID.text).group(1)
        except AttributeError:
            d["objectID"] = "no information"


        # Der Dict wird der apartments Liste hinzugefügt.
        apartments.append(d)


        # Da das Sktipt sehr lange lädt, soll der Status des Skripts angezeigt werden.
        # Der Fortschritt soll alle 20 Objekte (alle Seiten) angezeigt werden, zudem soll die
        # geschätzte verbleibende Zeit ausgerechnet werden und der aktuellen Zeit dazugezählt werden.
        progress = round(ap_counter / len(object_links) * 100, 0)
        now1 = time.time()
        elapsed = now1 - start_time
        tpa = elapsed / ap_counter
        est_time = datetime.strftime(
            datetime.fromtimestamp(now1 + tpa * (len(object_links) - ap_counter) +
                                   (240 * (len(object_links) - ap_counter) / 45)),
            format="%H:%M:%S"
        )


        if ap_counter % 20 == 0:
            print(f"{page_counter} ({progress} %) page(s) scraped. \n"
                  f"Estimated finishing Time: {est_time}")
            page_counter += 1
            ap_counter += 1
        else:
            ap_counter += 1

    df_apartments = pd.DataFrame(apartments)

    return df_apartments


def scrape_homegate():
    '''
    Erstellt zwei Dateien in den jeweiligen Directories: :
    - homegate_src_newest.csv
    - homegate_src_timestamp.csv

    Wobei "timestamp" ein Platzhalter für die aktuelle Zeit im Format %Y%d%m_%H%M%S ist.


    '''

    homegate_url = "https://www.homegate.ch/mieten/immobilien/kanton-bern/trefferliste?ep=1"
    l_pages = get_urls(homegate_url)
    l_apartements = get_object_links(l_pages)
    df_apartments = parse_object_links(l_apartements)
    file_creation = datetime.strftime(datetime.fromtimestamp(time.time()), format="%y-%m-%d_%H:%M")

    df_apartments.to_csv(f"../Data/src/archive/A_homegate_{file_creation}_src.csv", index=False)
    df_apartments.to_csv("../Data/src/A_homegate_newest_src.csv", index=False)

    print(f"process finished at {now}. \n"
          f"files created: \n "
          f"- ../Data/src/archive/A_homegate_{now}_src.csv \n "
          f"- ../Data/src/A_homegate_newest_src.csv \n"
          f"total rows: {len(df_apartments)}"






if __name__ == "__main__":
    scrape_homegate()


