import pandas as pd
import numpy as np
import re
from C_scrape_flatfox import name_curr_file
pd.options.mode.chained_assignment = None


# replace:
def repl_str(col):
    """replace unwanted strings in int columns."""
    col2 = col.replace("CHF ", "", regex=True
                       ).replace("’", "", regex=True
                                 ).astype(dtype=float, errors="ignore")
    return col2

# Add the desired variables, i.e. columns:

def create_new_var(str_rep, column, df):
    """Create new boolean variable for occurrence of attributes (e.g., balcony) in 'infos' col"""
    new_column = []
    str_rep = str_rep.lower().strip()
    for string in df[column]:
        try:
            if str_rep in string.lower().strip():
                new_column.append(True)
            else:
                new_column.append(False)
        except AttributeError:  # error occurs with empty cells
            new_column.append(False)

    return new_column



def if_str_contains(str_desc, attr):
    """Function to find if attributes occur in text (incl. negation)."""
    # convert all to lowercase:
    str_desc = str_desc.lower()
    attr = attr.lower()

    # find all forms of occurences of this word in the text (return False otherwise):
    if re.findall(fr'\b{attr}.*?\b', str_desc):
        words_list = re.findall(fr'\b{attr}.*?\b', str_desc)

        # define negations:
        negation = ['kein', 'keine', 'keines', 'keiner', 'ohne']

        # get all combinations of both lists:
        neg_attr = []
        [[neg_attr.append(j + ' ' + i) for j in negation] for i in words_list]
        #return neg_attr
        # if one of the neg_attr combinations is in the text, return False, otherwise True:
        if any(neg_word in str_desc for neg_word in neg_attr):
            return False
        else:
            return True
    else:
        return False


def check_description(old_col_name, attr, new_colname, df):
    """Check if the attributes occur in description and not in infos; write new
    boolean column (True if attribute is in either infos or description)."""
    df_flatfox = df
    df_flatfox[f'{old_col_name}_check'] = \
        df_flatfox.apply(lambda x: if_str_contains(x['description'], attr), axis=1)
    df_flatfox[new_colname] = \
        df_flatfox[f'{old_col_name}_check'] | df_flatfox[old_col_name]    # True if contained in either infos or desc
    return df_flatfox

def main():
    filename_dirty = name_curr_file('C_flatfox_', '.csv', '_src')
    df_flatfox = pd.read_csv(rf'../Data/src/{filename_dirty}')

    # filter (only objects in the canton of Bern):
    # import plz list of canton of bern
    plz_be = pd.read_csv(r'results/geodata/plz_be_list.csv')
    plz_be_list = plz_be['x'].tolist()

    # filter plz based on list:
    df_flatfox = df_flatfox[df_flatfox['plz'].isin(plz_be_list)]

    #print(plz_be_list)
    #print(type(plz_be_list))




    # reset index after filtering:
    df_flatfox = df_flatfox.reset_index(drop=True)

    # drop unnecessary columns:
    df_flatfox.drop(['Webseite:', 'Bezugstermin:', 'Preiseinheit:', 'Referenz:', 'Dokumente:',
                     'Kubatur:', 'Grundstücksfläche:', 'Mindestnutzfläche:',
                     'Besonderes:', 'Nutzfläche:', 'Miete:'], axis=1, inplace=True)

    # rename columns:
    df_flatfox.rename(columns={'Unnamed: 0': 'id_obj',
                               'title: ': 'title',
                               'Bruttomiete (inkl. NK):': 'gross_rent',
                               'Nettomiete (exkl. NK):': 'net_rent',
                               'Nebenkosten:': 'utilities',
                               'Baujahr:': 'build_year',
                               'Anzahl Zimmer:': 'rooms',
                               'Ausstattung:': 'infos',
                               'Wohnfläche:': 'area',
                               'Etage:': 'floor',
                               'url': 'url_flatfox'},  # floor is kept to check for duplicates (see below)
                      inplace=True, errors='raise')


    # clean all clos in CHF:
    df_flatfox[["gross_rent", "net_rent", "utilities"]] = df_flatfox[["gross_rent", "net_rent", "utilities"]].apply(
        repl_str)

    # replace ½ sympbols:
    df_flatfox = df_flatfox.replace(' ½', '.5', regex=True)

    # replace square meters:
    df_flatfox['area'] = df_flatfox['area'].replace('m²', '', regex=True).astype(float)

    # change number of rooms to float:
    df_flatfox['rooms'] = df_flatfox['rooms'].astype(dtype=float)

    # change to int:
    df_flatfox['plz'] = df_flatfox['plz'].astype(dtype=int)

    #### Create new columns:

    # rennovation year and build year are separate columns, take together (use most current date):

    list_year = []
    for i in range(len(df_flatfox)):
        if not np.isnan(df_flatfox['Renovationsjahr:'][i]):
            list_year.append(df_flatfox['Renovationsjahr:'][i])
        elif not np.isnan(df_flatfox['build_year'][i]):
            list_year.append(df_flatfox['build_year'][i])
        else:
            list_year.append(0)

    df_flatfox['build_ren_year'] = list_year

    # Check all unique values in infos-column, how much information is contained in this col?:
    #df_infos = df_flatfox[df_flatfox['infos'].notnull()]  # drop NaNs first
    #df_infos = df_infos.reset_index()

    #lst_attrs = []
    #[[lst_attrs.append(i.strip()) for i in df_infos['infos'][j].split(",")] for j in range(len(df_infos['infos']))]
    #set_attrs = set(lst_attrs)

    # have a look at all possible entries of this column:
    # [print(i) for i in set_attrs]

    # Not all desired variables are contained in info. Add the desired variables, i.e. columns:

    df_flatfox['balcony_terrace_infos'] = create_new_var("Balkon/Sitzplatz", 'infos', df_flatfox)
    df_flatfox['pets_infos'] = create_new_var("Haustiere", 'infos', df_flatfox)
    df_flatfox['elevator_infos'] = create_new_var("Lift", 'infos', df_flatfox)
    df_flatfox['car_spot_infos'] = create_new_var("Parkplatz", 'infos', df_flatfox)
    df_flatfox['minergie_infos'] = create_new_var("Minergie", 'infos', df_flatfox)
    df_flatfox['wheelchair_access_infos'] = create_new_var("Rollstuhlgängig", 'infos', df_flatfox)
    df_flatfox['washmachine_infos'] = create_new_var("Waschmaschine", 'infos', df_flatfox)
    df_flatfox['dishwasher_infos'] = create_new_var("Geschirrspüler", 'infos', df_flatfox)

    # Search for Neubau and other variables in description:

    df_flatfox['new_building'] = df_flatfox.apply(lambda x: if_str_contains(x['description'], "Neubau"), axis=1)
    df_flatfox['quiet_neighboorhood'] = df_flatfox.apply(lambda x: if_str_contains(x['description'], "ruhige Nachbarschaft"), axis=1)
    df_flatfox['parcet'] = df_flatfox.apply(lambda x: if_str_contains(x['description'], "Parkett"), axis=1)
    df_flatfox['dishwasher'] = df_flatfox.apply(lambda x: if_str_contains(x['description'], "Geschirrspüler"), axis=1)
    df_flatfox['family_child_friendly'] = df_flatfox.apply(lambda x: if_str_contains(x['description'], "Kinderfreundlich"), axis=1)

    # Check if any attributes (of infos-col) are in description, but not in infos:

    check_description('balcony_terrace_infos', 'Balkon', 'balcony_terrace', df_flatfox )
    check_description('pets_infos', 'Haustiere', 'pets', df_flatfox )
    check_description('elevator_infos', 'Lift', 'elevator', df_flatfox )
    check_description('car_spot_infos', 'Parkplatz', 'car_spot', df_flatfox )
    check_description('minergie_infos', 'Minergie', 'minergie', df_flatfox )
    check_description('wheelchair_access_infos', 'Rollstuhlgängig', 'wheelchair_access', df_flatfox )
    check_description('washmachine_infos', 'Waschmaschine', 'washmachine', df_flatfox )

    # drop no longer needed cols:
    df_flatfox = df_flatfox.loc[:, ~df_flatfox.columns.str.endswith('_infos')]
    df_flatfox = df_flatfox.loc[:, ~df_flatfox.columns.str.endswith('_check')]

    # drop last unnecessary columns:
    df_flatfox.drop(['id_obj','Renovationsjahr:', 'build_year'], axis=1, inplace=True)

    ### NA handling:

    # drop rows if rooms are missing;
    df_flatfox = df_flatfox.dropna(subset=['rooms'])

    # lose those that have no information about rent:
    df_flatfox = df_flatfox.dropna(subset=['gross_rent', 'utilities', 'net_rent'], how='all')

    # look at missings pattern:
    df_missings = df_flatfox[['gross_rent', 'utilities','net_rent']]

    #df_missings = df_missings.dropna(how = 'all')
    #null_data = df_missings[df_missings.isnull().any(axis=1)]
    #print(df_flatfox.isna().sum())

    # if two of three are given, add:
    df_flatfox['gross_rent_new'] = df_flatfox.apply(
        lambda row: row['net_rent']+row['utilities'] if np.isnan(row['gross_rent']) else row['gross_rent'],
        axis=1)

    df_flatfox['net_rent_new'] = df_flatfox.apply(
        lambda row: row['gross_rent']-row['utilities'] if np.isnan(row['net_rent']) else row['net_rent'],
        axis=1)

    # if only net rent or gross rent are given, calculate:
    df_flatfox['gross_rent_new'] = df_flatfox.apply(
        lambda row: row['net_rent']*1.135 if np.isnan(row['gross_rent']) and
                                             np.isnan(row['utilities']) else row['gross_rent'],
        axis=1)

    df_flatfox['net_rent_new'] = df_flatfox.apply(
        lambda row: row['gross_rent']/113.5*100 if (np.isnan(row['net_rent']) and
                                                    np.isnan(row['utilities'])) else row['net_rent'],
        axis=1)

    #print(df_flatfox.isna().sum())

    # area missing variables: approximate with 25m^2 per room:

    df_flatfox['area'] = df_flatfox.apply(
        lambda row: row['rooms']*25 if np.isnan(row['area']) else row['area'], axis=1)


    # check how many missings:
    #gross_rent_null_before = sum(pd.isnull(df_flatfox["net_rent"]))


    df_missings2 = df_flatfox[['gross_rent_new', 'utilities','net_rent_new']]
    null_data2 = df_missings2[df_missings.isnull().any(axis=1)]
    #print(null_data2)

    # drop old gross and net rent columns and rename the new vars:
    df_flatfox.drop(['gross_rent', 'net_rent', 'infos', 'description', 'floor', 'title'], axis=1, inplace=True)

    df_flatfox.rename(columns={'gross_rent_new': 'gross_rent',
                       'net_rent_new': 'net_rent'},
              inplace=True, errors='raise')

    df_flatfox['utilities'] = df_flatfox['gross_rent'] - df_flatfox['net_rent']

    # price per square meters:
    df_flatfox['price_sqrm'] = df_flatfox['gross_rent'] / df_flatfox['area']

    # price per rooms:
    df_flatfox['room_price'] = df_flatfox['gross_rent'] / df_flatfox['rooms']

    # average room size:
    df_flatfox['avg_room_size'] = df_flatfox['area'] / df_flatfox['rooms']

    # outlier analysis:
    #print(df_flatfox.sort_values("gross_rent", ascending=True).head(5))

    df_flatfox = df_flatfox.round({'price_sqrm': 2, 'room_price': 2, 'avg_room_size': 2})


    # convert appropriate columns to int:
    df_flatfox[['gross_rent', 'utilities','net_rent', 'build_ren_year']] = \
        df_flatfox[['gross_rent', 'utilities','net_rent', 'build_ren_year']].astype(dtype=int)



    #print(df_flatfox.isna().sum())

    # replace Nas in street with "No information" so upload into DB wont convert to "0":
    df_flatfox['street'] = df_flatfox['street'].fillna("No information")


    # create apt_id:
    df_flatfox['apt_id'] = df_flatfox.apply(
        lambda row: f"{row['gross_rent']}_{row['area']}_{row['rooms']}_"
                    f"{row['plz']}_{row['street'].strip().replace('.', '').replace(' ', '')}_{row['place']}",
        axis = 1)

    df_flatfox.replace(",", "", regex=True, inplace=True)

    # remove all non-digit and non-character elements:
    # result = re.sub('[\W_]+', '', ini_string)

    # find duplicates:
    #print(df_flatfox[df_flatfox.duplicated('apt_id')])

    # add a count of the number of duplicates to the primary key for all duplicates:
    df_flatfox['dupli_number'] = df_flatfox.groupby('apt_id').cumcount().add(1)-1

    df_flatfox['apt_id'] = df_flatfox.apply(
        lambda row: f"{row['apt_id']}_{row['dupli_number']}" if row['dupli_number'] != 0 else row['apt_id'],
        axis=1)

    df_flatfox.drop(['dupli_number'], axis=1, inplace=True)


    # reorder columns:
    df_flatfox = df_flatfox[['rooms', 'area', 'gross_rent', 'net_rent', 'plz', 'street', 'place', 'build_ren_year',
                             'balcony_terrace', 'pets', 'elevator', 'car_spot', 'minergie', 'wheelchair_access',
                             'new_building', 'washmachine', 'dishwasher', 'price_sqrm', 'room_price', 'avg_room_size',
                             'quiet_neighboorhood', 'parcet', 'family_child_friendly', 'apt_id', 'url_flatfox']]


    # write file:
    df_flatfox.to_csv("../Data/stage/C_flatfox_stage.csv", index = False)
    #df_flatfox.info()


if __name__ == "__main__":
    main()




