import pandas as pd


test_df = pd.read_csv("../Data/additional_data_clean/additional_data_wide.csv")
test_df.to_csv("../Data/src/testDELETE.csv")