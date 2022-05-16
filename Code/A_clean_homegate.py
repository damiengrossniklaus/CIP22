# A_clean_homegate

import pandas as pd
from datetime import datetime
import time
import numpy as np




def rm_space(df):
    df["place"] = df["place"].str.strip()
    return df


def missing_values(df):
    df = df.dropna(subset=["plz", "gross_rent", "place"])
    df = df[df["plz"] >= 1000]
    return df



def set_NA(df):
    df["street"] = df["street"].replace("no information", "No information")
    df["build_ren_year"] = df["build_ren_year"].replace("no information", 0)
    df["net_rent"] = df["net_rent"].replace("no information", 0)
    df["gross_rent"] = df["gross_rent"].replace("no information", 0)
    df = df.replace('no_information', np.NaN)
    df = df.replace('no information', np.NaN)
    return df


def converter(df):

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

    try:
        df["area"] = pd.to_numeric(df["area"], errors='coerce')
    except pd.errors.IntCastingNaNError:
        df["area"] = 0
    df["rooms"] = pd.to_numeric(df["rooms"], errors='coerce')

    try:
        df["plz"] = df["plz"].astype(str).apply(lambda x: x[:4])
    except ValueError:
        df["plz"] = df["plz"]

    try:
        df["objectID"] = df["objectID"].astype(str)
    except ValueError:
        df["objectID"] = df["objectID"]


    return df






def clean():
    now = datetime.strftime(datetime.fromtimestamp(time.time()), format="%y-%m-%d_%H:%M")
    print(f"starting process at {now}")
    df_cleaned = pd.read_csv(".../Data/src/A_homegate_newest_src.csv")
    df_cleaned.drop_duplicates("objectID", inplace=True)
    df_cleaned = missing_values(df_cleaned)
    df_cleaned = set_NA(df_cleaned)
    df_cleaned = rm_space(df_cleaned)
    df_cleaned = converter(df_cleaned)
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
    clean()



