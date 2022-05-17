from sqlalchemy import create_engine
import pandas as pd

# Needed to work with sqlalchemy
import pymysql
pymysql.install_as_MySQLdb()


# Lade die Daten von der Datenbank in ein Dataframe mittels pandas
def load_data_into_db():

    # Lade Daten als Dataframe
    df = pd.read_csv("../Data/additional_data_clean/additional_data_wide.csv")

    # Verbinde mit der MariaDB
    engine = create_engine("mariadb://admin_damien:Pa$$w0rd@10.177.124.137/CIP")

    # Lade Daten auf MariaDB
    df.to_sql('population_table', con=engine)

    # Schliesse Verbindung zu MariaDB
    engine.dispose()


# Lade die Daten von der Datenbank in ein Dataframe mittels pandas
def get_data_from_db():
    # Verbinde mit der MariaDB
    engine = create_engine("mariadb://admin_damien:Pa$$w0rd@10.177.124.137/CIP")

    # Definiere SQL-Query
    query = """SELECT * FROM population_table;"""

    # Führe Query aus und speichere Daten in Pandas-DataFrame
    df = pd.read_sql(query, con=engine)

    # Schliesse Verbindung zu MariaDB
    engine.dispose()

    return df

def main():

    # Lade Daten auf Datenbank
    load_data_into_db()

    # Lade Daten von der Datenbank herunter
    df = get_data_from_db()
    print(df)

if __name__ == '__main__':
    main()