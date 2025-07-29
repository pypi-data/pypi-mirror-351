def initialize_data():
    from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
    from platformdirs import user_data_dir
    import os

    directory = user_data_dir('ExoRM')
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Confirmed Exoplanet Query
    table = NasaExoplanetArchive.query_criteria(
        table = 'PS',
        select = 'pl_name, pl_bmasse, pl_rade, disc_year, pl_controv_flag'
    )

    data = table.to_pandas()

    data.to_csv(os.path.join(directory, 'exoplanet_data.csv'), index = False)

    # Creating Radius and Mass Data
    data = data[data['pl_controv_flag'] == 0]
    data['radius'] = data['pl_rade']
    data['mass'] = data['pl_bmasse']
    data['name'] = data['pl_name']
    data = data[data['radius'].notna() & data['mass'].notna()]

    data = data.sort_values(by = ['pl_name', 'disc_year'], ascending = [True, False])
    data = data.drop_duplicates(subset = 'pl_name').reset_index(drop = True)

    rm = data[['name', 'radius', 'mass']]
    rm.to_csv(os.path.join(directory, 'exoplanet_rm.csv'), index = False)