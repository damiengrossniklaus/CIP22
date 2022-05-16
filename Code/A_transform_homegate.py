# A_transform_homegate

import pandas as pd
import numpy as np
from datetime import datetime
import time





def checkif(s, kw, *stopword):
    try:
        state = False
        for sword in stopword:
            if sword in s.lower():
                return False
            else:
                state = True

        if (state == True) & (kw in s.lower()):
            return True
        else:
            return False
    except:
        return False




def generate_columns_bool(df):

    df["pets"] = df["description"].apply(lambda x: checkif(x, "haustiere erlaubt", "keine haustiere"))
    df["minergie"] = df["description"].apply(lambda x: checkif(x, "minergie"))
    df["elevator"] = df["description"].apply(lambda x: checkif(x, "lift", "kein lift", "ohne lift"))
    df["car_spot"] = df["description"].apply(lambda x: checkif(x, "parkplatz", "kein parkplatz", "ohne parkplatz"))
    df["wheelchair_access"] = df["description"].apply(lambda x: checkif(x, "rollstuhltauglich"))
    df["new_building"] = df["description"].apply(lambda x: checkif(x, "neubau"))
    df["washmachine"] = df["description"].apply(lambda x: checkif(x, "waschmaschine", "keine waschmaschine"))
    df["dishwasher"] = df["description"].apply(lambda x: checkif(x, "geschirrspühler", "kein geschirrspühler"))
    df["parcet"] = df["description"].apply(lambda x: checkif(x, "parkett"))
    df["quiet_neighboorhood"] = df["description"].apply(lambda x: checkif(x, "ruhige lage"))
    df["family_child_friendly"] = df["description"].apply(lambda x: checkif(x, "kinderfreundlich"))


    return df


def generate_columns_ratio(df):
    try:
        df["avg_room_size"] = round(df["area"] / df["rooms"], 2)
    except (ZeroDivisionError, ValueError):
        df["avg_room_size"] = 25
    try:
        df["price_sqrm"] = round(df["gross_rent"] / df["area"], 2)
        df["price_sqrm"].replace(np.inf, 0, inplace=True)
    except (ZeroDivisionError, ValueError):
        df["price_sqrm"] = 0
    try:
        df["room_price"] = round(df["gross_rent"] / df["rooms"], 2)
    except (ZeroDivisionError, ValueError):
        df["room_price"] = 0

    return df

def impute(df):
    df["plz"] = df["plz"].astype(int)

    # Entferne Zeilen, welche über keine Raumanzahl verfügen
    df.dropna(subset=['rooms'], inplace=True)

    # Imputiere 25 Quadratmeter x Raum für Objekte, welche über keine Fläche verfügen
    df['area'].fillna(df['rooms'] * 25, inplace=True)

    # Entferne Zeilen, welche weder über gross_rent noch net_rent verfügen
    df.drop(df[df['gross_rent'].isna() & df['net_rent'].isna()].index, inplace=True)

    # Ziehe Nebenkosten von 13.5% von gross_rent ab für Objekte, welche über keine net_rent verfügen
    df['net_rent'].fillna(round(df['gross_rent'] / 113.5 * 100, 2), inplace=True)

    # Schlage 13.5% der net_rent auf für Objekte, welche über keine gross_rent verfügen
    df['gross_rent'].fillna(round(df['net_rent'] * 1.135, 2), inplace=True)

    df["url_homegate"] = df["url"]
    df.drop("url", axis=1)

    return df






def make_ID(df):
    df["apt_id"] = (df["gross_rent"].astype(str) + "_" + df["area"].astype(str) + "_" + df["rooms"].astype(str) + "_" +
                   df["plz"].astype(str) + "_" + df["street"] + "_" + df["place"]).str.replace(" ", "")

    g = df.groupby("apt_id")
    df["apt_id"] += g.cumcount().astype(str).radd("_").\
        mask(g["apt_id"].transform("count")==1,"").\
        replace("_0", "")

    return df


def sort_columns(df):
    df = df[['rooms', 'area', 'gross_rent', 'net_rent', 'plz', 'street', 'place', 'build_ren_year',
                             'balcony_terrace', 'pets', 'elevator', 'car_spot', 'minergie', 'wheelchair_access',
                             'new_building', 'washmachine', 'dishwasher', 'price_sqrm', 'room_price', 'avg_room_size',
                             'quiet_neighboorhood', 'parcet', 'family_child_friendly', 'apt_id', 'url_homegate']]
    return df



def transform():
    now = datetime.strftime(datetime.fromtimestamp(time.time()), format="%Y%d%m_%H%M%S")
    print(f"starting process at {now}")
    file_path = "../Data/clean/A_homegate_newest.csv_clean"
    df_cleaned = pd.read_csv(file_path)
    df_transformed = generate_columns_bool(df_cleaned)
    df_transformed = generate_columns_ratio(df_transformed)
    df_transformed = impute(df_transformed)
    df_transformed = df_transformed.drop(["description", "objectID"], axis=1)
    df_transformed = make_ID(df_transformed)
    df_transformed = sort_columns(df_transformed)
    df_transformed.to_csv("../Data/stage/A_homegate_newest_stage.csv", index = False)
    now = datetime.strftime(datetime.fromtimestamp(time.time()), format="%Y%d%m_%H%M%S")
    df_transformed.to_csv(f"../Data/stage/archive/A_homegate_{now}_stage.csv", index=False)
    print(f"process finished at {now}. \n"
          f"files created: \n "
          f"- ../Data/stage/archive/A_homegate_{now}_stage.csv \n "
          f"- ../Data/stage/A_homegate_newest_stage.csv \n"
          f"total rows: {len(df_transformed)}"
          )



if __name__ == "__main__":
    transform()
    



