import pandas as pd
import geopandas as gpd
from geopandas.tools import geocode
from matplotlib import cm
from sqlalchemy import create_engine
import pymysql

pymysql.install_as_MySQLdb()

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

    return df




def mainMap():
    #loading spatial files
    gemeinde = gpd.read_file("Data/geodata/SHAPEFILE_LV95_LN02/swissBOUNDARIES3D_1_3_TLM_HOHEITSGEBIET.shp")
    kantone = gpd.read_file("Data/geodata/SHAPEFILE_LV95_LN02/swissBOUNDARIES3D_1_3_TLM_KANTONSGEBIET.shp")
    plz_be = pd.read_csv('Data/geodata/plz_be.csv')
    best_apts = pd.read_excel('../Data/results/results_question2.xlsx')


    #Projektion konvertieren, filtern nach Kanton Bern
    gemeinden_bern = gemeinde[gemeinde["KANTONSNUM"] == 2].to_crs('epsg:4326')
    kanton_bern = kantone[kantone['KANTONSNUM'] == 2].to_crs('epsg:4326')


    #joining plz to city name
    gemeinden_bern.merge(plz_be, left_on='NAME', right_on='ORTBEZ18', how='left')

    #creating new row for geocoding:
    best_apts['address'] = best_apts['street'] + ", " + best_apts['place']

    #forward geocoding:
    best_apts_geo = geocode(best_apts.address) #, provider='photon'

    #joining dataframes
    best_apts = best_apts.merge(best_apts_geo, left_index=True, right_index=True, how='left')

    best_apts = gpd.GeoDataFrame(best_apts, crs="EPSG:4326", geometry='geometry')
    joined_df = best_apts.sjoin(gemeinden_bern)
    print(joined_df.info())
    df_visual = joined_df[['address_x', 'rooms', 'area', 'gross_rent', 'overall_rank', 'url_immoscout', 'url_homegate', 'url_flatfox', 'geometry']]
    df_visual= gpd.GeoDataFrame(df_visual,
                                      crs='EPSG:4326',
                                      geometry='geometry')

    new_columns = {'address_x': 'Adresse', 'rooms': 'Zimmer', 'area': 'Fläche', 'overall_rank':'Platzierung',
                   'gross_rent': 'Mietpreis', 'url_immoscout':'Immoscout',
                   'url_homegate':'Homegate', 'url_flatfox':'FlatFox', 'geometry':'geometry'}
    df_visual.rename(columns=new_columns, inplace=True)


    df_visual['Fläche'] = df_visual['Fläche'].astype(str) + " m2"
    df_visual['Mietpreis'] = "CHF " + df_visual['Mietpreis'].astype(str) + ".--"
    df_visual["Platzierung"] = df_visual["Platzierung"].round(0)



    df_visual["Immoscout"] = "<a href=" + df_visual["Immoscout"] + ">immoscout.ch</a>"
    df_visual["Homegate"] = "<a href=" + df_visual["Homegate"] + ">homegate.ch</a>"
    df_visual["FlatFox"] = "<a href=" + df_visual["FlatFox"] + ">flatfox.ch</a>"



    #creating plot

    #first layer for outlines Kanton Bern
    m = kanton_bern.explore(
        tiles="cartodbpositron",
        scheme="naturalbreaks",
        tooltip=False,
        style_kwds=dict(color="#10E694", fill=False),
        name="kanton"
    )

    #adding points to the second layer
    df_visual.explore(
        m=m,
        column="Platzierung",
        scheme="naturalbreaks",
        popup=True,
        legend=True,
        tooltip=["Adresse", "Zimmer", "Fläche", "Mietpreis", "Platzierung", "Immoscout", "Homegate", "FlatFox"],
        cmap="cool",
        marker_kwds=dict(radius=7, fill=True),
        name="gemeinden"
    )


    #saving file as html :)
    m.save('Data/results/question_2_map.html')


if __name__ == "__main__":
    mainMap()