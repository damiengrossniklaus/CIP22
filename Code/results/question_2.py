import pandas as pd
from sqlalchemy import create_engine

# Wird benötigt, um create_engine verwenden zu können
import pymysql
pymysql.install_as_MySQLdb()


# Lade die Daten von der Datenbank in ein Dataframe mittels pandas
def get_data_from_db():
    # Verbinde mit der MariaDB
    engine = create_engine("mariadb://admin_damien:Pa$$w0rd@10.177.124.137/CIP")

    # Definiere SQL-Query
    query = """SELECT * FROM All_objects_clean_table;"""

    # Führe Query aus und speichere Daten in Pandas-DataFrame
    df = pd.read_sql(query, con=engine)

    # Schliesse Verbindung zu MariaDB
    engine.dispose()

    return df


def map_region(df):
    # Erstelle region-Spalte gesützt auf plz der Objekte
    d = {"plz_id": ["25", "26", "27", "32", "30", "36", "31", "33",
                    "45", "47", "49", "34", "35", "61", "37", "38"],
         "region": ["Seeland", "Seeland", "Seeland", "Seeland",
                    "Bern Stadt/Agglo", "Mittelland", "Mittelland",
                    "Oberaargau", "Oberaargau", "Oberaargau", "Oberaargau",
                    "Emmental", "Emmental", "Emmental", "Oberland West", "Oberland Ost"]}

    df_right = pd.DataFrame.from_dict(d)

    df["plz_id"] = df["plz"].astype(str).str[0:2]

    df = df.merge(df_right, on="plz_id")

    return df


def price_sqrm_rank(df):

    # Erstelle dict mit durchsch. Quadratmeterpreis pro Region
    median_dict = dict(df.groupby('region')['price_sqrm'].median())

    # Mappe durchsch. Quadratmeterpreis pro Objekt nach Region
    df['avg_price_sqrm'] = df['region'].map(median_dict)

    # Berechne Differenzspalte zum durchschnittlichen Mietpreis pro Region pro Objekt
    df['avg_price_sqrm_diff'] = df['price_sqrm'] - df['avg_price_sqrm']

    # Verteile Ränge der Quadrameterpreisdifferenz pro Objekt und Region zu.
    # Rang 1 == Höchste Minusdifferenz
    df['price_sqrm_rank'] = df.groupby('region')['avg_price_sqrm_diff'].rank(method='max')

    return df


def area_rank(df):

    # Erstelle dict mit durchsch. Fläche pro Region
    median_dict = dict(df.groupby('region')['area'].median())

    # Mappe durchsch. Fläche pro Objekt nach Region
    df['avg_area'] = df['region'].map(median_dict)

    # Berechne Differenzspalte zur durchschnittlichen Fläche der Region pro Objekt
    df['avg_area_diff'] = df['area'] - df['avg_area']

    # Verteile Ränge der Flächendifferenz pro Objekt und Region zu.
    # Rang 1 == Höchste Positivdifferenz
    df['area_rank'] = df.groupby('region')['avg_area_diff'].rank(method='max', ascending=False)

    return df


def attribute_rank(df):

    # Spalten mit Wohnungsattributen
    attribute_list = ['pets', 'elevator', 'car_spot',
                    'minergie', 'wheelchair_access', 'new_building', 'washmachine',
                    'dishwasher', 'quiet_neighboorhood', 'parcet', 'family_child_friendly']

    # Ändere Datentyp der Spalten zu Bool
    df[attribute_list] = df[attribute_list].applymap(lambda x: True if x == 'True' else False)

    # Summiere die Anzahl an vorhandenen Wohnungsattributen
    # True == 1, False == 0
    df['attribute_score'] = df.loc[:, attribute_list].sum(axis=1)

    # Verteile Ränge der Wohnungsattributen pro Objekt und Region zu.
    # Rang 1 == am meisten Wohnugsattribute vorhanden
    df['attribute_rank'] = df.groupby('region')['attribute_score'].rank(method='max', ascending=False)

    return df


def calculate_combined_rank_score(df):

    # Berechne durschn. Ranking der drei ranking spalten
    df['object_rank_score'] = (df['price_sqrm_rank'] + df['area_rank'] + df['attribute_rank'])/3

    return df


def create_ranking_df(df):

    # Sortiere Objekte pro Region nach deren Objektenrang aufsteigend und
    # gebe top 10 Objekte pro Region in einem Dataframe wieder
    df_grouped = df.groupby('region').apply(lambda x: x.sort_values(['object_rank_score']).head(10))

    # Erstelle Spalte mit Ranking gesützt auf top-Objekt DataFrame
    df_grouped['overall_rank'] = df_grouped['object_rank_score'].rank(method='max')

    df_grouped.sort_values('overall_rank', inplace=True)
    df_grouped.reset_index(inplace=True, drop=True, level=1)

    return df_grouped


def create_region_rank_df(df):

    # Sortiere Objekte pro Region nach deren Objektenrang aufsteigend und
    # gebe top 10 Objekte pro Region in einem Dataframe wieder
    df_grouped = df.groupby('region').apply(lambda x: x.sort_values(['object_rank_score']))
    df_grouped.reset_index(inplace=True, drop=True, level=1)

    # Erstelle Dataframe pro Region
    df_bern_aglo = df_grouped.loc[('Bern Stadt/Agglo'), :]
    df_seeland =  df_grouped.loc[('Seeland'), :]
    df_mittelland = df_grouped.loc[('Mittelland'), :]
    df_oberaargau = df_grouped.loc[('Oberaargau'), :]
    df_emmental = df_grouped.loc[('Emmental'), :]
    df_oberland_west = df_grouped.loc[('Oberland West'), :]
    df_oberland_ost = df_grouped.loc[('Oberland Ost'), :]

    return df_bern_aglo, df_seeland, df_mittelland, df_oberaargau, df_emmental, \
           df_oberland_west, df_oberland_ost


def excel_sheets_writer(df_list, sheet_name_list, file_name):
    # Erstelle writer zum Überschreiben der Excel-Datei
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    # Iteriere durch df und Blattnamen und schreibe die df's jeweils in ein separates Excel-Blatt
    for df, sheet in zip(df_list, sheet_name_list):
        df.to_excel(writer, sheet_name=sheet, startrow=0, startcol=0)
    writer.save()


def answer_second_question():

    # Lade Daten und erstelle Dataframe mit Regionen-Spalte
    df = get_data_from_db()
    df_region = map_region(df)
    print(df)

    # Berechne Ränge
    price_sqrm_rank(df_region)
    area_rank(df_region)
    attribute_rank(df_region)

    # Kombiniere Ränge
    calculate_combined_rank_score(df_region)

    # Erstelle Ranking Dataframe und Speichere Daten in Excel.
    df_final = create_ranking_df(df_region)


    # Erstelle Ranking Dataframe der einzelnen Regionen
    df_bern_aglo, df_seeland, df_mittelland, df_oberaargau, df_emmental, df_oberland_west, df_oberland_ost  = create_region_rank_df(df_region)


    # Speichere die einzelnen Dataframes in second_question.xlsx
    # Erstelle Dataframe-Liste und Blattnamen-Liste
    df_list = [df_final, df_bern_aglo, df_seeland, df_mittelland,
               df_oberaargau, df_emmental, df_oberland_west, df_oberland_ost]

    sheet_name_list = ['Gesamtübersicht', 'Bern Stadt-Agglo', 'Seeland', 'Mittelland',
                       'Oberaargau', 'Emmental', 'Oberland West', 'Oberland Ost']

    # Führe Funktion aus und schreibe Resultate in Excel-Datei
    excel_sheets_writer(df_list, sheet_name_list, '../../Data/results/results_question2.xlsx')

    print("Resultate wurden in Excel-Datei geschrieben!")


if __name__ == "__main__":
    answer_second_question()

