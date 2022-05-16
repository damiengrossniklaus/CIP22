import pandas as pd

# Lade Daten in ein Dataframe und returne dieses
def load_data():
    df = pd.read_excel('../Data/additional_data_dirty/staendige_wohnbevoelkerung.xlsx', skiprows=2, nrows=3183)
    print(df)
    return df

def clean_data(df):
    # Erstelle Dataframe im wide-Format (ändere Spaltennamen)
    df_wide = df.rename(columns={'Unnamed: 0': 'Plz'})

    # Erstelle Dataframe im long-Format
    # Ändere Spaltennamen
    df_long = df.rename(columns={'Unnamed: 0': 'Plz'})

    # Erstelle Total-Spalte Dateframe
    total_df = df_long[['Plz', 'Total']]

    # Transformiere Staatsangehörigkeit Spalten in einzelne Spalte
    staats_df = pd.melt(df_long, id_vars='Plz', value_vars=['Schweiz', 'Ausland'], var_name='staatsangehoerigkeit',
                        value_name='Personen_staat')

    # Transformiere Geschlecht Spalten in einzelne Spalte
    gender_df = pd.melt(df_long, id_vars='Plz', value_vars=['Mann', 'Frau'], var_name='geschlecht',
                        value_name='Personen_geschlecht')

    # Transformiere Zivilstand Spalten in einzelne Spalte
    zivilstand_df = pd.melt(df_long, id_vars='Plz',
                            value_vars=['Ledig', 'Verheiratet', 'Verwitwet', 'Geschieden', 'Unverheiratet',
                                        'In eingetragener Partnerschaft', 'Aufgelöste Partnerschaft'],
                            var_name='zivilstand', value_name='Personen_zivilstand')

    # Transformiere Altersgruppen Spalten in einzelne Spalte
    altersgruppe_df = pd.melt(df_long, id_vars='Plz', value_vars=['0-4', '5-9',
                                                             '10-14', '15-19', '20-24', '25-29', '30-34', '35-39',
                                                             '40-44', '45-49',
                                                             '50-54', '55-59', '60-64', '65-69', '70-74', '75-79',
                                                             '80-84', '85-89',
                                                             '90 und mehr'], var_name='altersgruppe',
                              value_name='Personen_altersgruppe')

    # Joine die erstellten Dataframes mit long-Format zu einem Dataframe
    df_join = pd.merge(total_df, staats_df, on='Plz')

    df_join1 = pd.merge(df_join, gender_df, on='Plz')

    df_join2 = pd.merge(df_join1, zivilstand_df, on='Plz')

    df_long = pd.merge(df_join2, altersgruppe_df, on='Plz')

    return df_wide, df_long


def main():
    df = load_data()
    df_wide, df_long = clean_data(df)

    # Speichere Dataframes als CSV-Datei
    df_wide.to_csv("../Data/additional_data_clean/additional_data_wide.csv", index=False)
    df_long.to_csv("../Data/additional_data_clean/additional_data_long.csv", index=False)


if __name__ == '__main__':
    main()