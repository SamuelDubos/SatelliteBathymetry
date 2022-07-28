"""
Copyright 2022 © Centre Interdisciplinaire de développement en Cartographie des Océans (CIDCO), Tous droits réservés
@Samuel_Dubos
"""

from matplotlib.pyplot import show
from acquire import Sentinel2
from rasterio import open
from pyproj import Geod
from collect import *
from process import *
from mosaic import *


def generate_data():

    dates = list(set([str(filename[:17]) for filename in listdir(raw_path)
                      if Path(f'{listdir(raw_path)}/{filename}').suffix == '.txt']))
    for date in dates:
        speed = 1500
        start, stop = get_start_stop(raw_path, date)
        pings = generate_pings(start, stop, minutes=minute)
        print(date)
        organize_data(raw_path, organized_path, date, pings, speed)
        file = f"transformed_{date}.dat"
        os.system(f'/home/fundy/Documents/main_test/transform_data.sh '
                  f'{organized_path} {date}.dat {transformed_path} {file}')


def generate_path_borders() -> [float, float, float, float]:

    lat_list, lng_list = [], []
    for file in listdir(transformed_path):
        data = read_csv(f'{transformed_path}/{file}', sep=' ').values
        for lat, lng, dep in data:
            lat_list.append(lat)
            lng_list.append(lng)
    est_bd, west_bd, south_bd, north_bd = max(lng_list), min(lng_list), min(lat_list), max(lat_list)

    return est_bd, west_bd, south_bd, north_bd


def generate_rta(source1, band1, source2, band2) -> ndarray:

    r20m, scl, source1, band1, source2, band2 = get_jp2_names(product, unzip_path, source1, band1, source2, band2)
    scl, band1, band2 = open(f"{r20m}/{scl}").read(1), open(f"{source1}/{band1}").read(1), open(f"{source2}/{band2}").read(1)
    figure('SCL')
    imshow(scl)
    rta = create_rta(scl, band1, band2, dilatation=1, scale=(True, factor))
    figure(f'Calibration')
    imshow(rta, 'ocean')

    return rta


def update_depths() -> [ndarray, list]:

    lat_list, lng_list = [], []
    xml = f"{unzip_path}/{product}/INSPIRE.xml"
    borders = get_bounds(xml)
    est, west, south, north = borders
    depths, points = zeros(size), []
    for j, file in enumerate(listdir(transformed_path)):
        # figure(f'{file}')
        d = zeros(size)
        data = read_csv(f'{transformed_path}/{file}', sep=' ').values
        for lat, lng, dep in data:
            if south < lat < north and west < lng < est:
                y, x = transform_c2p(lat, lng, borders, size)
                depths[x, y] = dep
                points.append(Point([x, y]))
                d[x, y] = dep
        # heatmap(d)

    figure('Heatmap')
    heatmap(depths)

    return depths, points


if __name__ == '__main__':

    # Initialize the paths
    base_path = "/home/fundy/Documents/main_test"
    raw_path = f'{base_path}/raw'
    organized_path = f'{base_path}/organized'
    transformed_path = f'{base_path}/transformed'
    product_path = f'{base_path}/products'
    subdirectories = ['zip_files', 'extracted_files']
    zip_path = f"{product_path}/{subdirectories[0]}"
    unzip_path = f"{product_path}/{subdirectories[1]}"
    # granule_path = f"{unzip_path}/{listdir(unzip_path)[product_index]}/GRANULE"
    l2a_path = f"{granule_path}/{listdir(granule_path)[0]}"

    # Parametrize - Set the parameters
    sat = Sentinel2("samueldubos", "5c6a7b54")
    date1 = 'NOW-7DAYS'
    date2 = 'NOW-2DAYS'
    footprint = 'POLYGON((-69 48, -58 48, -58 51, -69 51, -69 48))'
    resolution = 600
    borders_band = 'B01'
    source_1, band_1 = 'R20m', 'B02'
    source_2, band_2 = 'R20m', 'B03'

    # Acquire - Search, download and extract the products
    products = sat.search(date1, date2, footprint)
    for product in products:
        sat.download(product, zip_path)
    for product in listdir(zip_path):
        unzip(f"{zip_path}/{product}", unzip_path)

    # Process - Collect and process the products
    minute = 2
    generate_data()
    # path_borders = generate_path_borders()
    factor = 20
    RTA = generate_rta(source_1, band_1, source_2, band_2)
    size = RTA.shape
    depths_matrix, points_list = update_depths()
    borders_mask = open(f"{l2a_path}/QI_DATA/MSK_DETFOO_{borders_band}.jp2").read(1)
    borders_mask = resize(borders_mask, size)
    calibrate_rta(borders_mask, size[0], RTA, points_list, depths_matrix)

    show()
