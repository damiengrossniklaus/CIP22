#merge.py


import pandas as pd
from datetime import datetime
import time



def mergeApts(df1, df2, df3):
    join_col = list(df1.columns)
    df = pd.merge(pd.merge(df1, df2, how="outer"),
                  df3,  how="outer")
    l1 = len(df)
    df.drop_duplicates(subset="apt_id", inplace=True)
    l2 = len(df)
    print(f"{l1-l2} rows dropped")

    s1 = set(df1["apt_id"])
    s2 = set(df1["apt_id"])
    s3 = set(df1["apt_id"])
    r1 = len(df1)
    r2 = len(df2)
    r3 = len(df3)
    intersection = len(s1 & s2) + len(s1 & s3) + len(s2 & s3) - 2 * len(s1 & s2 & s3)

    print(f"sum of rows: {r1 + r2 + r3}")

    print(f"size of intersection: {intersection}")
    #print(f"theoretical result: {r1 + r2 + r3 - intersection} ")

    print(f"actual length: {len(df)}")

    return df


def mainMerge():
    df_A = pd.read_csv("Data/data_cleaned/immoscout_stage_newest.csv")
    df_B = pd.read_csv("Data/data_cleaned/homegate_stage_newest.csv")
    df_C = pd.read_csv("Data/data_cleaned/C_flatfox_stage_newest.csv")
    df = mergeApts(df_A, df_B, df_C)
    now = datetime.strftime(datetime.fromtimestamp(time.time()), format="%y-%m-%d_%H:%M")
    #df.reset_index(drop=True)
    df.to_csv("Data/joined/df_joined_newest.csv", index=False)
    df.to_csv(f"Data/archive/df_joined_{now}.csv")
    print(f"process finished at {now}. \n"
          f"files created: \n "
          f"- Data/archive/df_joined_{now}.csv \n "
          f"- Data/df_joined_newest.csv \n"
          f"total rows: {len(df)}"
          )



if __name__ == "__main__":
    mainMerge()
