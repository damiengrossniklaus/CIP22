import pandas as pd
import statsmodels.formula.api as smf
from sqlalchemy import create_engine
import pymysql
pymysql.install_as_MySQLdb()

def get_data_from_db():
    """Load data from MariaDB and save to df"""

    # Connect
    engine = create_engine("mariadb://admin_nathanael:Pa$$w0rd@10.177.124.137/CIP")

    # deploy query and save in df
    df = pd.read_sql("""SELECT * FROM All_objects_clean_table;""", con=engine)
    engine.dispose()
    return df


df_analysis = get_data_from_db()

df_analysis.replace("True", True, regex=True, inplace=True)
df_analysis.replace("False", False, regex=True, inplace=True)



#df_normal = pd.read_csv(r'df_joined_newest_analysis.csv')
#print(df_joined.info())

# regression analyis: which variables can be used to predict the gross_rent?
# drop the variables that we do not need: plz, place, street, avg_room_size, price_sqrm, room_price
df_analysis.drop(['net_rent', 'street', 'avg_room_size',
                  'price_sqrm', 'room_price', 'build_ren_year'], axis=1, inplace=True)

# drop all non-boolean variables (for analysis later):
df_analysis_bool = df_analysis.copy()
df_analysis_bool.drop(['rooms', 'area', 'gross_rent', 'plz', 'apt_id', 'url_immoscout',
                                     'url_homegate', 'url_flatfox', 'place'], axis=1, inplace=True)


def coef_regression(col):

    reg_model = smf.ols(f'gross_rent ~ rooms + area + {col}', data=df_ana_single)
    reg_model_result = reg_model.fit()
    coef_reg_mod = reg_model_result.params[1].round(2)

    return coef_reg_mod


car_spot_price = []
reg_vars = {'plz': [], 'place':[], 'N': [] }
bool_dict = {key:[] for key in df_analysis_bool.columns}
reg_output = {**reg_vars, **bool_dict}



for i in set(df_analysis['plz']):

    df_ana_single = df_analysis.loc[(df_analysis['plz'] == i)]
    N = len(df_ana_single)
    place = df_ana_single['place'].iloc[0]

    # dict comprehension to append coefficients of regression result:
    {key: reg_output[key].append(coef_regression(key)) for key in df_analysis_bool.columns}
    
    reg_output['plz'].append(i)
    reg_output['place'].append(place)
    reg_output['N'].append(N)

df_res = pd.DataFrame(reg_output)

# filter all plz under 20:
df_res_filt = df_res.loc[(df_res['N'] >= 20)]


# write .csv file:
df_res_filt.to_excel(r'../../Data/results/results_supplementary_question.xlsx', index = False)


