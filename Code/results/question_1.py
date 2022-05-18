from sqlalchemy import create_engine
import pymysql
pymysql.install_as_MySQLdb()

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

def get_data_from_db():
    """Load data from MariaDB and save to df"""

    # Connect
    engine = create_engine("mariadb://admin_nathanael:Pa$$w0rd@10.177.124.137/CIP")

    # deploy query and save in df
    df = pd.read_sql("""SELECT * FROM All_objects_clean_table;""", con=engine)
    engine.dispose()
    return df

# Get data
df_heatmap = get_data_from_db()

df_heatmap.replace("True", int("1"), regex=True, inplace=True)
df_heatmap.replace("False", int("0"), regex=True, inplace=True)

map_dat = 'geodata/PLZO_SHP_LV03/PLZO_PLZ.shp'
regions = gpd.read_file(map_dat)

# read plz file and convert to list
plz_be = pd.read_csv(r'geodata/plz_be_list.csv')
plz_be_list = plz_be['x'].tolist()


def create_heatmap(attr = 'apt_id', stat = 'count'):

    if stat == 'count':
        data_by_plz = df_heatmap[['plz', attr]].groupby('plz').count().reset_index()
    elif stat == 'mean':
        data_by_plz = df_heatmap[['plz', attr]].groupby('plz').mean().reset_index()
    else:
        raise ValueError("stat must be either count or mean")

    print(data_by_plz.columns)
    data_by_plz['plz'] = data_by_plz['plz'].astype(dtype=int)

    regions_be = regions[regions['PLZ'].isin(plz_be_list)]
    regions_be = regions_be.rename(columns={'PLZ': 'plz'})

    # join data frames:
    merged = regions_be.merge(data_by_plz, on='plz', how='outer')
    merged = merged.reset_index()

    figure_be, axis_fig = plt.subplots(1, figsize=(12, 10))
    axis_fig.axis('off')

    if stat == 'count':
        axis_fig.set_title('Number of renting objects in the canton of Bern, by PLZ',
                           fontdict={'fontsize': '18', 'fontweight' : '3'})
    elif stat == 'mean':
        axis_fig.set_title(f'Average ({attr}) of renting objects in the canton of Bern, by PLZ',
                           fontdict={'fontsize': '14', 'fontweight': '3'})
    color = 'Reds'

    vmin, vmax = 0, max(data_by_plz[attr])
    sm = plt.cm.ScalarMappable(cmap=color, norm=plt.Normalize(vmin=vmin, vmax=vmax))

    cbar = figure_be.colorbar(sm, fraction=0.02)
    cbar.ax.tick_params(labelsize=10)
    merged.plot(attr, cmap = color, missing_kwds={'color': 'lightgrey'},
                linewidth=0.1, ax = axis_fig, edgecolor='black',  figsize=(12,10))

    figure_be.savefig(f"../../Data/results/results_question1_{attr}.jpeg", format='jpeg')

    #plt.show()


if __name__ == "__main__":
    create_heatmap('rooms', 'mean')

