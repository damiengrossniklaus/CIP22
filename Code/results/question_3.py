#question_3.py

import pandas as pd
import matplotlib.pyplot as plt
import xlsxwriter
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sqlalchemy import create_engine
import pymysql

pymysql.install_as_MySQLdb()


# Lade die Daten von der Datenbank in ein Dataframe mittels pandas
def get_data_from_db(table):
    '''

    :param table: str: Exakter Tabellenname
    :return: pd.DataFrame: DataFrame der Tabelle
    '''
    # Erstelle User Credentials
    user = "admin_olivier"
    password="Pa$$w0rd@"

    # Verbinde mit der MariaDB
    engine = create_engine(f"mariadb://{user}:{password}10.177.124.137/CIP")

    # Definiere SQL-Query
    query = f"""SELECT * FROM {table};"""

    # Führe Query aus und speichere Daten in Pandas-DataFrame
    df = pd.read_sql(query, con=engine)

    # Schliesse Verbindung zu MariaDB
    engine.dispose()
    print(df.head())
    print(df.info())

    return df



def urban_vs_rural_price_sqrm(df_apt, df_pop):
    '''

    :param df_apt: pandas.DataFrame: Informationen zu den Mietobjekten
    :param df_pop: pandas.DataFrame: Informationen zu Gemeinden, PLZ
    :return: pandas.DataFrame: DataFrame mit Mittwelwerten des Quadratmeterpreises für städische
                               und für ländliche Regionen
    '''

    df_pop['Plz'] = df_pop['Plz'].astype(str)
    df_apt['plz'] = df_apt['plz'].astype(str)

    df_combined = df_apt.merge(df_pop, left_on='plz', right_on='Plz')
    df_combined['urban_rural'] = df_combined['Total'].apply(lambda x: 'urban' if x >= 10000 else 'rural')

    df_combined = df_combined[df_combined['price_sqrm'] > 0]
    df_result3_a = df_combined[['urban_rural', 'price_sqrm']].groupby(['urban_rural']).mean().reset_index()

    plt.hist(df_combined[df_combined['urban_rural'] == "urban"]['price_sqrm'], alpha=0.5, bins=25, label="urban")
    plt.hist(df_combined[df_combined['urban_rural'] == "rural"]['price_sqrm'], alpha=0.5, bins=25, range = (0, 100), label="rural")
    plt.legend(['urban', 'rural'])
    plt.show()

  
    urban_price_sqrm = df_combined[df_combined['urban_rural'] == 'urban']['price_sqrm'].dropna()
    rural_price_sqrm = df_combined[df_combined['urban_rural'] == 'rural']['price_sqrm'].dropna()
    print(f'The result of an T-test for independant samples: {stats.ttest_ind(urban_price_sqrm, rural_price_sqrm)}')
    print('Das Resultat des T-Tests sowie die beiden Histogramme zeigen, dass die städtlichkeit einer Ortschaft \n'
    'alleine keinen signifikanten Einfluss auf den Quadratmeterpreis haben.')


    return df_result3_a


def price_demographic(df_apt, df_pop):
    '''

    :param df_apt: pandas.DataFrame: Informationen zu den Mietobjekten
    :param df_pop: pandas.DataFrame: Informationen zu Gemeinden, PLZ
    :return: pandas.DataFrame: DataFrame mit 2 Spalten: eigentliche Werte der Mietpreise sowie die Vorhersagewerte
                               dieser Preise.
    '''
    df_pop['Plz'] = df_pop['Plz'].astype(str)
    df_apt['plz'] = df_apt['plz'].astype(str)


    df_apt = df_apt[['plz', 'price_sqrm']].groupby(['plz']).mean().reset_index()

    df_combined = df_apt.merge(df_pop, right_on='Plz', left_on='plz', how='left')
    df_combined.drop('Plz', axis=1, inplace=True)


    #to remove colinearities, all predictor columns except for the "Total" column are divided by the Total column.
    df_combined_new = df_combined.iloc[:, :].dropna()
    df_combined_new.iloc[:, 3:] = df_combined.iloc[:, 3:].div(df_combined_new.Total, axis=0)

    #splitting dataset in predictor (x) and dependent variable (y):
    x = df_combined_new.drop(['plz', 'price_sqrm'], axis=1)
    y = df_combined_new['price_sqrm']



    #splitting data into train and test data:
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    #creating the model:
    linreg = LinearRegression()
    # fitting the training data
    linreg.fit(x_train, y_train)

    #predicting prices:
    y_prediction = linreg.predict(x_test)

    df_pred_vs_test = pd.DataFrame.from_dict({'test': y_test, 'prediction': y_prediction})
    print('-' * 50  + '\n'
    'Resultate der multiplen linearen Regression: ')
    print(f'r2: {r2_score(y_test, y_prediction)}')
    print(f'mse: {mean_squared_error(y_test, y_prediction)}')
    print(f'rsme: {mean_squared_error(y_test, y_prediction)**0.5}')
    print('-' * 50)


    return df_pred_vs_test


def writeExcel(df_result_3a, df_result_3b):
    '''

    :param df_result_3a: pandas.DataFrame: Resultat der Frage 3a
    :param df_result_3b: pandas.DataFrame: Resultat der Frage 3b
    :return: Erstellt eine Excel Datei mit zwei Tabellenblättern:
                        Blatt 1: Resultat Frage 3a mit Diagram
                        Blatt 2: Resultat Frage 3b
    '''

    # Erstellen der Excel Arbeitsmappe
    result3 = '../../Data/results/question_3.xlsx'
    workbook = xlsxwriter.Workbook(result3)

    # Start Zeile und Spalte. Diese werden für beide Blätter benutzt.
    start_row = 0
    start_col = 0

    # Erstellen des Arbeitsblattes 1
    result3_a = workbook.add_worksheet('results_3a')

    # Den Dataframe in ein Excel Arbeitsblatt schreiben:
    result3_a.write_row(start_row, start_col, df_result_3a.columns)
    for i, column in enumerate(df_result_3a.columns, start=start_col):
        result3_a.write_column(start_row + 1, i, df_result_3a[column])

    # Hinzufügen eines Diagramms im Arbeitsblatt:
    # Definition des Typs: Säulendiagram.
    chart = workbook.add_chart({'type': 'column'})

    # Hinzufügen der Daten, welche für das Diagram verwendet werden sollen:
    chart.add_series({'categories': f'=results_3a!$A$2:$A{len(df_result_3a) + 1}',
                      'values': f'=results_3a!$B$2:$B{len(df_result_3a) + 1}',
                      'name': '=results_3a!$A1'})

    # Formatieren der Achse, Titel hinzufügen
    chart.set_y_axis({'min': 0, 'max': 25})
    chart.set_title({'name':'Quadratmeterpreis in ländlichen und urbanen Regionen'})

    # Diagram einfügen
    result3_a.insert_chart('D5', chart)

    #Neues Arbeitsblatt einfügen
    result3_b = workbook.add_worksheet('results_3b')
    result3_b.write_row(start_row, start_col, df_result_3b.columns)

    # Den Dataframe in ein Excel Arbeitsblatt schreiben:
    for i, column in enumerate(df_result_3b.columns, start=start_col):
        result3_b.write_column(start_row + 1, i, df_result_3b[column])

    workbook.close()



def main_question_3():
    df_apartements = get_data_from_db("All_objects_clean_table")
    df_population = get_data_from_db("population_table")
    
    df_result_3a = urban_vs_rural_price_sqrm(df_apt=df_apartements, df_pop=df_population)
    df_result_3b = price_demographic(df_apt=df_apartements, df_pop=df_population)
    writeExcel(df_result_3a, df_result_3b)
    print("process finished, excel file : ")





if __name__ == "__main__":
    main_question_3()