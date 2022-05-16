import pandas as pd
from datetime import datetime


# Cleane Rooms
def room_cleaner(df):
    """
    Bereinigt die rooms-Spalte eines pandas.DataFrame.

    Args:
        df (pandas.Dataframe[rooms: str]): Dataframespalte mit str

    Returns:
        pandas.Dataframe[rooms: float]: Dateframe mit bereinigter rooms-spalte als float
    """
    # Ersetze "-" mit einem Leerzeichen
    # Ignoriere die Werte, welche keinen 'Zimmer' string haben.
    df['rooms'] = df['rooms'].apply(lambda x: x.replace("-", " ") if "Zimmer" in x else x)

    # Split string und tausche "," mit "." um nur noch die Anzahl der Zimmer als float zu haben.
    # Ignoriere die Werte, welche keinen 'Zimmer' string haben.
    df['rooms'] = df['rooms'].apply(lambda x: x.split()[0].replace(",", ".") if "Zimmer" in x else x)

    # Ersetze "No information" mit None
    df['rooms'] = df['rooms'].apply(lambda x: None if x == "No information" else float(x))

    return df


# Cleane Area
def area_cleaner(df):
    """
    Bereinigt the area-Spalte eines pandas.DataFrame.
    Isoliert die Zahl in Spalten mit m² und setzt None ein, wenn die Spalte dies nicht hat.

    Args:
        df (pandas.Dataframe[area: str]): Dataframespalte mit str

    Returns:
        pandas.Dataframe[rooms: float]: Dateframe mit bereinigter area-spalte als float
    """
    df['area'] = df['area'].apply(lambda x: float(x.split()[0]) if "m²" in x else None)

    return df


# Cleane gross_rent
def gross_rent_cleaner(df):
    """
    Bereinigt gross_rent-Spalte eines pandas.DataFrame.
    Entferne "CHF" vor Betrag und ".-" nach Betrag und wandle Nummer in int typ um.
    Ersetze einen String mit "Preis auf Anfrage" oder "No information" mit None.

    Args:
        df (pandas.Dataframe[gross_rent: str]): Dataframespalte mit str

    Returns:
        pandas.Dataframe[gross_rent: int]: Dateframe mit bereinigter gross_rent-spalte als int
    """
    df['gross_rent'] = df['gross_rent'].apply(
        lambda x: int(x.split("CHF")[1].split(".")[0].replace(" ", "")) if "CHF" in x else None)

    return df


# Cleane net_rent
def net_rent_cleaner(df):
    """
    Bereinigt net_rent-Spalte eines pandas.DataFrame.
    Entferne "CHF" vor Betrag und ".-" nach Betrag und wandle Nummer in Int typ um.
    Ersetze "No information" mit None.

    Args:
        df (pandas.Dataframe[net_rent: str]): Dataframespalte mit str

    Returns:
        pandas.Dataframe[net_rent: int]: Dateframe mit bereinigter net_rent-spalte als int
    """

    df['net_rent'] = df['net_rent'].apply(
        lambda x: int(x.split("CHF")[1].split(".")[0].replace(" ", "")) if "CHF" in x else None)

    return df


# Cleane build_ren_year
def build_ren_year_cleaner(df):
    """
    Bereinigt build_ren_year-Spalte eines pandas.DataFrame
    Wandle Jahreszahl in int typ um.
    Ersetze "No Information" mit None.

    Args:
        df (pandas.Dataframe[build_ren_year: str]): Dataframespalte mit str

    Returns:
        pandas.Dataframe[build_ren_year: int]: Dateframe mit bereinigter build_ren_year-spalte als int
    """

    df['build_ren_year'] = df['build_ren_year'].apply(lambda x: int(x) if "No information" not in x else 0)

    return df


# Cleane street
def plz_cleaner(df):
    """
    Ersetze "No Information" mit 0.
    Wandle plz in int typ um

    Args:
        df (pandas.Dataframe[plz: str]): Dataframespalte mit str

    Returns:
        pandas.Dataframe[plz: int]: Dateframe mit bereinigter plz-spalte als int
    """

    df['plz'].mask(df['plz'] == 'No information', 0, inplace=True)
    df['plz'] = df['plz'].astype(int)

    return df


# Komma cleaner -> ersetze Kommas in Zellen, damit es keine Probleme mit Upload in DB gibt
def comma_cleaner(df):
    """
    Ersetze "," mit "" in gesamtem Dataframe

    Args:
        df (pandas.Dataframe): Dataframe mit diversen Spalten

    Returns:
        pandas.Dataframe: Dateframe ohne Kommas
    """

    df.replace(",", "", regex=True, inplace=True)

    return df


# Überprüfe, ob Wohnungsattribute nicht doch in der Beschreibung sind.

# Erstellen der dafür benötigten Funktionen
def attribute_with_info_comparer(df_col, keyword, *stopword):
    """
    Prüfe ob Keyword in pandas.DataFrame-Spalte vorhanden und stopwords NICHT vorhanden sind.

    Args:
        df_col (pandas.DataFrame[str]): Dataframe-Spalte mit str
        keyword (str): Suchword, welches vorhanden sein soll
        *stopword (str). Argumentliste von stopwörtern mit variabler Länge

    Returns:
        bool
    """
    state = False
    for word in stopword:
        if word in df_col.lower():
            return False
        else:
            state = True
    if (state == True) & (keyword in df_col.lower()):
        return True
    else:
        return False


def attribute_comparer(df_new_column, df_old_column):
    """
    Vergleiche gespcrapte Spalte mit Keywordsuch-Spalte

    Args:
        df_new_column (pandas.DataFrame[bool]): Erste neue Vergleichs-Spalte
        df_old_column (pandas.DataFrame[bool]): Zweite alte Vergleichs-Spalte

    Returns:
        bool
    """
    if df_new_column == True:
        return True
    else:
        return df_old_column


# Überprüfe jede Wohnungsattributspalte
def attribute_cleaner(df):
    """
    Überprüft 'info' Spalte nach Keywords und vergleicht diese mit den Spalten
    'balcony_terrace','pets',
    'elevator','car_spot',
    'minergie','wheelchair_access',
    'new_building','washmachine',
    'dishwasher'

    Args:
        df (pandas.DataFrame): pandas.DataFrame mit Spalten 'info',
                                'balcony_terrace','pets',
                                'elevator','car_spot',
                                'minergie','wheelchair_access',
                                'new_building','washmachine',
                                'dishwasher'
    Returns:
        df (pandas.DataFrame): Mit 'info'-Spalte abgeglichenes pandas.DataFrame mit Spalten
                                'balcony_terrace','pets',
                                'elevator','car_spot',
                                'minergie','wheelchair_access',
                                'new_building','washmachine',
                                'dishwasher'
    """

    # Überprüfe balcony_terrace
    # Suche nach Keywords und Stopwords
    df['balcony_terrace_new'] = df['infos'].apply(
        lambda x: attribute_with_info_comparer(x, 'balkon', 'kein balkon', 'keine terasse'))
    # Vergleiche gespcrapte Spalte mit Keywordsuch-Spalte
    df['balcony_terrace_final'] = df.apply(lambda x: attribute_comparer(x['balcony_terrace_new'], x['balcony_terrace']),
                                           axis=1)

    # Überprüfe pets
    # Suche nach Keywords und Stopwords
    df['pets_new'] = df['infos'].apply(lambda x: attribute_with_info_comparer(x, 'haustiere', 'keine haustiere'))
    # Vergleiche gespcrapte Spalte mit Keywordsuch-Spalte
    df['pets_final'] = df.apply(lambda x: attribute_comparer(x['pets_new'], x['pets']), axis=1)

    # Überprüfe elevator
    # Suche nach Keywords und Stopwords
    df['elevator_new'] = df['infos'].apply(
        lambda x: attribute_with_info_comparer(x, 'lift', 'kein lift', 'ohne lift', 'keinen lift'))
    # Vergleiche gescrapte Spalte mit Keywordsuch-Spalte
    df['elevator_final'] = df.apply(lambda x: attribute_comparer(x['elevator_new'], x['elevator']), axis=1)

    # Überprüfe car_spot
    # Suche nach Keywords und Stopwords
    df['car_spot_new'] = df['infos'].apply(
        lambda x: attribute_with_info_comparer(x, 'parkplatz', 'kein parkplatz', 'ohne parkplatz', 'keinen parkplatz'))
    # Vergleiche gescrapte Spalte mit Keywordsuch-Spalte
    df['car_spot_final'] = df.apply(lambda x: attribute_comparer(x['car_spot_new'], x['car_spot']), axis=1)

    # Überprüfe minergie
    # Suche nach Keywords und Stopwords
    df['minergie_new'] = df['infos'].apply(
        lambda x: attribute_with_info_comparer(x, 'minergie', 'kein minergie', 'ohne minergie', 'keine minergie'))
    # Vergleiche gescrapte Spalte mit Keywordsuch-Spalte
    df['minergie_final'] = df.apply(lambda x: attribute_comparer(x['minergie_new'], x['minergie']), axis=1)

    # Überprüfe wheelchair_access
    # Suche nach Keywords und Stopwords
    df['wheelchair_access_new'] = df['infos'].apply(
        lambda x: attribute_with_info_comparer(x, 'rollsuhlgängig', 'nicht rollstuhlgängig', 'ohne rollstuhlzugang'))
    # Vergleiche gescrapte Spalte mit Keywordsuch-Spalte
    df['wheelchair_access_final'] = df.apply(
        lambda x: attribute_comparer(x['wheelchair_access_new'], x['wheelchair_access']), axis=1)

    # Überprüfe new_building
    # Suche nach Keywords und Stopwords
    df['new_building_new'] = df['infos'].apply(lambda x: attribute_with_info_comparer(x, 'neubau', 'altbau'))
    # Vergleiche gescrapte Spalte mit Keywordsuch-Spalte
    df['new_building_final'] = df.apply(lambda x: attribute_comparer(x['new_building_new'], x['new_building']), axis=1)

    # Überprüfe washmachine
    # Suche nach Keywords und Stopwords
    df['washmachine_new'] = df['infos'].apply(
        lambda x: attribute_with_info_comparer(x, 'waschmaschine', 'keine waschmaschine', 'ohne waschmaschine'))
    # Vergleiche gescrapte Spalte mit Keywordsuch-Spalte
    df['washmachine_final'] = df.apply(lambda x: attribute_comparer(x['washmachine_new'], x['washmachine']), axis=1)

    # Überprüfe dishwasher
    # Suche nach Keywords und Stopwords
    df['dishwasher_new'] = df['infos'].apply(
        lambda x: attribute_with_info_comparer(x, 'geschirrspühler', 'kein geschirrspühler', 'ohne geschirrspühler'))
    # Vergleiche gescrapte Spalte mit Keywordsuch-Spalte
    df['dishwasher_final'] = df.apply(lambda x: attribute_comparer(x['dishwasher_new'], x['dishwasher']), axis=1)

    # Erstelle finales Dataframe (lösche Spalten, welche nicht mehr benötigt werden)
    df.drop(['balcony_terrace', 'balcony_terrace_new',
                  'pets', 'pets_new',
                  'elevator', 'elevator_new',
                  'car_spot', 'car_spot_new',
                  'minergie', 'minergie_new',
                  'wheelchair_access', 'wheelchair_access_new',
                  'new_building', 'new_building_new',
                  'washmachine', 'washmachine_new',
                  'dishwasher', 'dishwasher_new'], axis=1, inplace=True)

    # Ändere Spaltennamen der finalen Spalten zurück
    df.rename(columns={'balcony_terrace_final': 'balcony_terrace',
                            'pets_final': 'pets',
                            'elevator_final': 'elevator',
                            'car_spot_final': 'car_spot',
                            'minergie_final': 'minergie',
                            'wheelchair_access_final': 'wheelchair_access',
                            'new_building_final': 'new_building',
                            'washmachine_final': 'washmachine',
                            'dishwasher_final': 'dishwasher'}, inplace=True)

    return df

# Imputationen und NA-Handling
def na_handling(df):
    """
    Bereinigt NA's im pandas.Dataframe.

    Args:
        df (pandas.DataFrame): pandas.DataFrame mit Spalten 'rooms',
                                'area','gross_rent',
                                'net_rent','build_ren_year'

    Returns:
        df (pandas.DataFrame): pandas.DataFrame mit Spalten 'rooms',
                                'area','gross_rent',
                                'net_rent','build_ren_year' ohne NA
    """

    # Entferne Zeilen, welche über keine Raumanzahl verfügen
    df.dropna(subset=['rooms'], inplace=True)

    # Imputiere 25 Quadratmeter x Raum für Objekte, welche über keine Fläche verfügen
    df['area'].fillna(df['rooms'] * 25, inplace=True)

    # Entferne Zeilen, welche weder über gross_rent noch net_rent verfügen
    df.drop(df[df['gross_rent'].isna() & df['net_rent'].isna()].index, inplace=True)

    # Ziehe Nebenkosten von 13.5% von gross_rent ab für Objekte, welche über keine net_rent verfügen
    df['net_rent'].fillna(df['gross_rent'] / 113.5 * 100, inplace=True)

    # Schlage 13.5% der net_rent auf für Objekte, welche über keine gross_rent verfügen
    df['gross_rent'].fillna(df['net_rent'] * 1.135, inplace=True)

    # Wandle gross_rent und net_rent in Datentyp int um
    df['net_rent'] = df['net_rent'].astype(int)
    df['gross_rent'] = df['gross_rent'].astype(int)

    # Setzte build_rent_year auf 0 für Objekte, welche kein build_ren_year verfügen
    df['build_ren_year'].fillna(0, inplace=True)

    # Setze Index-Spalte zurück
    df.reset_index(drop=True, inplace=True)

    return df



def clean_immoscout():
    df = pd.read_csv('../Data/src/B_immoscout_src.csv')

    # Cleaning Funktionen
    room_cleaner(df)
    area_cleaner(df)
    gross_rent_cleaner(df)
    net_rent_cleaner(df)
    build_ren_year_cleaner(df)
    plz_cleaner(df)
    comma_cleaner(df)
    attribute_cleaner(df)
    na_handling(df)

    df.info()

    # Speichere Daten als .csv im Ordner data_cleaned
    now = datetime.now()
    date_time = now.strftime("%Y%d%m_%H%M%S")

    # Speichere Daten als .csv mit Datum und Zeit als Suffix
    df.to_csv(f"../Data/clean/archive/B_immoscout_{date_time}_clean.csv", index=False)

    # Speichere Daten als neuste Version
    df.to_csv("../Data/clean/B_immoscout_clean.csv", index=False)


if __name__ == '__main__':
    clean_immoscout()