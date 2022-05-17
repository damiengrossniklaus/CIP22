import mysql.connector as mariadb
from sqlalchemy import create_engine
import pandas as pd

# Needed to work with sqlalchemy
import pymysql
pymysql.install_as_MySQLdb()


def upload_data_to_db():
    # Connect to Mariadb
    mariadb_connection = mariadb.connect(user="admin_nathanael",
                                         password="Pa$$w0rd",
                                         host="10.177.124.137",
                                         port=3306,
                                         database="CIP",
                                         allow_local_infile=True)

    # Create cursor
    mycursor = mariadb_connection.cursor()

    # drop old table
    mycursor.execute("""DROP TABLE flatfox_table""")

    # Create table (if it doesnt eixst yet)
    mycursor.execute("""CREATE TABLE IF NOT EXISTS flatfox_table(
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
                     url_flatfox VARCHAR(150))""")


    # Load data to Mariadb
    mycursor.execute("""LOAD DATA LOCAL INFILE '../Data/stage/C_flatfox_stage.csv' 
                            INTO TABLE  flatfox_table 
                            FIELDS TERMINATED BY ',' 
                            IGNORE 1 LINES""")

    # Save changes and close
    mariadb_connection.commit()
    mariadb_connection.close()


# Load data from database and save as pandas
def get_data_from_db():
    # connect
    engine = create_engine("mariadb://admin_nathanael:Pa$$w0rd@10.177.124.137/CIP")

    # Define SQL-Query
    query = """SELECT * FROM flatfox_table;"""

    # Run query and save in pandas df
    df = pd.read_sql(query, con=engine)

    # Close connection
    engine.dispose()

    return df

def main():

    # Upload data to database:
    upload_data_to_db()

    # Download data from database
    get_data_from_db()


if __name__ == '__main__':
    main()