import mysql.connector as mariadb
from sqlalchemy import create_engine
import pandas as pd
import pymysql

# Wird benötigt, um create_engine verwenden zu können
pymysql.install_as_MySQLdb()


def upload_data_to_db():
    # Verbinde mit der MariaDB
    mariadb_connection = mariadb.connect(user="admin_damien",
                                         password="Pa$$w0rd",
                                         host="10.177.124.137",
                                         port=3306,
                                         database="CIP",
                                         allow_local_infile=True)

    # Erstelle Cursor zum Interagieren mit der MariaDB
    mycursor = mariadb_connection.cursor()

    # Drop DB
    mycursor.execute("""DROP TABLE immoscout_table""")

    # Erstelle Tabelle in MariaDB, wenn diese noch nicht existiert
    mycursor.execute("""CREATE TABLE IF NOT EXISTS immoscout_table(
                     rooms FLOAT,
                     area INT,
                     gross_rent FLOAT,
                     net_rent FLOAT,
                     plz VARCHAR(4),
                     street VARCHAR(100),
                     place VARCHAR(100),
                     build_ren_year INT,
                     balcony_terrace CHAR(5),
                     pets CHAR(5),
                     elevator CHAR(5),
                     car_spot CHAR(5),
                     minergie CHAR(5),
                     wheelchair_access CHAR(5),
                     new_building CHAR(5),
                     washmachine CHAR(5),
                     dishwasher CHAR(5),
                     price_sqrm FLOAT,
                     room_price FLOAT,
                     avg_room_size FLOAT,
                     quiet_neighboorhood CHAR(5),
                     parcet CHAR(5),
                     family_child_friendly CHAR(5),
                     apt_id VARCHAR(100),
                     url_immoscout VARCHAR(100)
                     )""")

    # Lade Daten in Tabelle auf MariaDB
    mycursor.execute("""LOAD DATA LOCAL INFILE '../Data/stage/B_immoscout_stage.csv' 
                            INTO TABLE  immoscout_table 
                            FIELDS TERMINATED BY ',' 
                            IGNORE 1 LINES""")

    # Übergebe die Änderungen an die Datenbank und schliesse Verbindung
    mariadb_connection.commit()
    mariadb_connection.close()


# Lade die Daten von der Datenbank in ein Dataframe mittels pandas
def get_data_from_db():
    # Verbinde mit der MariaDB
    engine = create_engine("mariadb://admin_damien:Pa$$w0rd@10.177.124.137/CIP")

    # Definiere SQL-Query
    query = """SELECT * FROM immoscout_table;"""

    # Führe Query aus und speichere Daten in Pandas-DataFrame
    df = pd.read_sql(query, con=engine)
    print(df)

    # Schliesse Verbindung zu MariaDB
    engine.dispose()

def main():

    # Lade Daten auf Datenbank
    upload_data_to_db()

    # Lade Daten von der Datenbank herunter
    get_data_from_db()


if __name__ == '__main__':
    main()