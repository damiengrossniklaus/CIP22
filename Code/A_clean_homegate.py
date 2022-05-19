# A_clean_homegate

import pandas as pd
from datetime import datetime
import time
import numpy as np




def rm_space(df):
    '''
    Entfernt Leerschläge bei "Place"
    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    '''''
    df["place"] = df["place"].str.strip()
    return df


def missing_values(df):
    '''
    Sucht fehlende Werte und ersetzt diese mit recovery Werten, falls keine recovery
    Werte verfügbar sind wir die Zeile gedropt.
    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    '''
    #erstellen der recovery variablen
    df['r_plz'] = df['description'].str.extract(r'Gemeinde-Ratgeber für (\d{4})').astype(float)
    df['r_place'] = df['description'].str.extract(r'Gemeinde-Ratgeber für \d{4} ([^[V]+)')

    #ersetzen der eigentlichen variablen mit den recov. variablen wenn plz > 1000
    df['place'].mask(df['plz'] < 1000, df['r_place'], inplace=True)
    df['plz'].mask(df['plz'] < 1000, df['r_plz'], inplace=True)

    #droppen der values
    df.drop(df[(df['gross_rent'].isna()) & (df['net_rent'].isna())].index, inplace=True)
    df.drop(df[(df['plz'].isna()) & (df['r_plz'].isna())].index, inplace=True)

    #droppen der recovery variablen
    df.drop(['r_plz', 'r_place'], axis=1, inplace=True)




    return df



def set_NA(df):
    '''
    Ersetzt "no information" mit besseren werten um weiter zu rechnen.
    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    '''

    #Bei den meisen Attributen soll no_information mit np.NaN ersetzt werden, bei anderen mit 0
    # oder anderen strings.
    df["street"] = df["street"].replace("no information", "No information")
    df["build_ren_year"] = df["build_ren_year"].replace("no information", 0)
    df["net_rent"] = df["net_rent"].replace("no information", 0)
    df["gross_rent"] = df["gross_rent"].replace("no information", 0)
    df = df.replace('no_information', np.NaN)
    df = df.replace('no information', np.NaN)
    return df


def converter(df):
    '''
    Konvertiert Strings welche als Zahl gelesen werden sollten zu Zahlen.
    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    '''


    # Mietpreise sollen alle als numeric gelesen werden, um im transform schritt weitere Kennzahlen berechnen zu können.
    try:
        df["gross_rent"] = df["gross_rent"].replace("’", "", regex=True)
        df["gross_rent"] = df["gross_rent"].replace(".–", "", regex=True)
        df["gross_rent"] = df["gross_rent"].replace(np.NaN, 0)
        df["gross_rent"] = df["gross_rent"].replace("no information", 0)
        df["gross_rent"] = pd.to_numeric(df["gross_rent"],
                                         errors="coerce", downcast="integer")
    except pd.errors.IntCastingNaNError:
        df["gross_rent"] = 0

    try:
        df["net_rent"] = df["net_rent"].replace("’", "", regex=True)
        df["net_rent"] = df["net_rent"].replace(".–", "", regex=True)
        df["net_rent"] = df["net_rent"].replace(np.NaN, 0)
        df["net_rent"] = df["net_rent"].replace("no information", 0)
        df["net_rent"] = pd.to_numeric(df["net_rent"],
                                       errors="coerce", downcast="integer")
    except (pd.errors.IntCastingNaNError, ValueError):
        df["net_rent"] = 0


    #auch Area ist eine Zahl und soll als solche gelesen werden.
    try:
        df["area"] = pd.to_numeric(df["area"], errors='coerce')
    except pd.errors.IntCastingNaNError:
        df["area"] = 0
    df["rooms"] = pd.to_numeric(df["rooms"], errors='coerce')


    #Plz wird immer wieder als float gelesen hier soll sie als string sein
    try:
        df["plz"] = df["plz"].astype(str).apply(lambda x: x[:4])
    except ValueError:
        df["plz"] = df["plz"]

    #ObjectID als string.
    try:
        df["objectID"] = df["objectID"].astype(str)
    except ValueError:
        df["objectID"] = df["objectID"]


    return df



def rm_outlier(df):
    '''
    Einige Objekte werden pro Tag vermietet, deshalb werden diese Mietpreise mit 30 multipliziert.
    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    '''

    #Wenn der mietpreis unter 100 liegt, wird davon ausgegangen dass es eine tagesmiete ist.
    df['net_rent'].mask(df['net_rent'] < 100, df['net_rent'] * 30, inplace=True)
    df['gross_rent'].mask(df['net_rent'] < 100, df['gross_rent'] * 30, inplace=True)
    return df







def clean_homegate():
    now = datetime.strftime(datetime.fromtimestamp(time.time()), format="%y-%m-%d_%H:%M")
    print(f"starting process at {now}")
    df_cleaned = pd.read_csv("../Data/src/A_homegate_newest_src.csv")
    df_cleaned.drop_duplicates("objectID", inplace=True)
    df_cleaned = missing_values(df_cleaned)
    df_cleaned = set_NA(df_cleaned)
    df_cleaned = rm_space(df_cleaned)
    df_cleaned = converter(df_cleaned)
    df_cleaned = rm_outlier(df_cleaned)
    df_cleaned.to_csv("../Data/clean/A_homegate_newest_clean.csv", index=False)
    now = datetime.strftime(datetime.fromtimestamp(time.time()), format="%y-%m-%d_%H:%M")
    df_cleaned.to_csv(f"../Data/clean/archive/A_homegate_{now}_clean.csv", index=False)
    print(f"process finished at {now}. \n"
          f"files created: \n "
          f"- ../Data/clean/archive/A_homegate_{now}_clean.csv \n "
          f"- ../Data/clean/A_homegate_newest_clean.csv \n"
          f"total rows: {len(df_cleaned)}"
          )







if __name__ == "__main__":
    clean_homegate()



