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

    return df


def mainMerge():
    df_A = pd.read_csv("../Data/stage/B_immoscout_stage.csv")
    df_B = pd.read_csv("../Data/stage/A_homegate_stage.csv")
    df_C = pd.read_csv("../Data/stage/C_flatfox_stage.csv")
    df = mergeApts(df_A, df_B, df_C)
    now = datetime.strftime(datetime.fromtimestamp(time.time()), format="%y-%m-%d_%H:%M")
    #df.reset_index(drop=True)
    df.to_csv("../Data/joined/df_joined_stage.csv", index=False)
    df.to_csv(f"../Data/joined/archive/df_joined_stage_{now}.csv")
    print(f"process finished at {now}. \n"
          f"files created: \n "
          f"- Data/joined/archive/df_stage_{now}.csv \n "
          f"- Data/joined/df_joined_stage.csv \n"
          f"total rows: {len(df)}"
          )



if __name__ == "__main__":
    mainMerge()
