import pandas as pd
from datetime import datetime


# Runde Quadratmeterpreis
def price_sqrm_generator(df):
    df['price_sqrm'] = round(df['gross_rent'] / df['area'], 2)

    return df


# Runde Zimmerpreis
def room_price_generator(df):
    df['room_price'] = round(df['gross_rent'] / df['rooms'], 2)

    return df


# Runde Durchschnittliche Zimmergrösse
def avg_room_size_generator(df):
    df['avg_room_size'] = round(df['area'] / df['rooms'], 2)

    return df


# Zusätzliche Wohnungseigenschaften aus Beschreibung

# Funktion zum Suchen von Keywords in info-Spalte
def attribute_allocator(search_column, *keywords):
    for word in keywords:
        if word in search_column.lower():
            return True
        else:
            continue
    return False


# Suche nach Keywords
def attribute_seacher(df):
    # Ruhige Nachbarschaft
    df['quiet_neighboorhood'] = df['infos'].apply(lambda x: attribute_allocator(x, 'ruhige nachbarschaft', 'ruhig'))

    # Parkett
    df['parcet'] = df['infos'].apply(lambda x: attribute_allocator(x, 'parkett'))

    # Kinderfreundlich / Familienfreundlich
    df['family_child_friendly'] = df['infos'].apply(
        lambda x: attribute_allocator(x, 'kinderfreundlich', 'familienfreundlich'))

    # Entferne Info-Spalte, wird nicht mehr verwendet
    df.drop('infos', axis=1, inplace=True)

    return df


# Erstellung des Verbundingsattributs ID
# Initialisiere id_liste zum Prüfen vom Objekten mit gleicher ID
# Wird für Funktion id_generator benötigt
def id_list_initializer():
    global id_list
    id_list = list()


# Funktion zum Erstellen der ID-Variable
def id_generator(df):
    counter = 1
    rooms = str(df['rooms'])
    gross_rent = str(df['gross_rent'])
    area = str(df['area'])
    plz = str(df['plz'])
    street = (df['street'].replace(" ", ""))
    place = (df['place'].replace(" ", ""))
    id = f"{gross_rent}_{area}_{rooms}_{plz}_{street}_{place}"

    while id in id_list:
        id = f"{gross_rent}_{area}_{rooms}_{plz}_{street}_{place}_{counter}"
        counter += 1

    id_list.append(id)
    return id


# Erstellen der ID Spalte
def id_allocator(df):
    id_list_initializer()
    df['apt_id'] = df.apply(id_generator, axis=1)

    return df


# Sortiere die Spalten in gewünschter Reihenfolge
def sort_columns(df):
    df_final = df[['rooms', 'area', 'gross_rent', 'net_rent', 'plz', 'street', 'place', 'build_ren_year',
                             'balcony_terrace', 'pets', 'elevator', 'car_spot', 'minergie', 'wheelchair_access',
                             'new_building', 'washmachine', 'dishwasher', 'price_sqrm', 'room_price', 'avg_room_size',
                             'quiet_neighboorhood', 'parcet', 'family_child_friendly', 'apt_id', 'url_immoscout']]

    return df_final

def transform_immoscout():
    df = pd.read_csv("../Data/clean/B_immoscout_clean.csv")

    # Transform Funktionen
    price_sqrm_generator(df)
    room_price_generator(df)
    avg_room_size_generator(df)
    attribute_seacher(df)
    id_allocator(df)
    df_final = sort_columns(df)

    df_final.info()

    # Speichere Daten als .csv im Ordner data_cleaned
    now = datetime.now()
    date_time = now.strftime("%Y%d%m_%H%M%S")

    # Speichere Daten als .csv mit Datum und Zeit als Suffix
    df_final.to_csv(f"../Data/stage/archive/B_immoscout_{date_time}_stage.csv", index=False)

    # Speichere Daten als neuste Version
    df_final.to_csv("../Data/stage/B_immoscout_stage.csv", index=False)


if __name__ == '__main__':
    transform_immoscout()

