"""
Copyright 2022 © Centre Interdisciplinaire de développement en Cartographie des Océans (CIDCO), Tous droits réservés
@Samuel_Dubos
"""

from matplotlib.pyplot import colorbar, figure, imshow
from cv2 import dilate, INTER_LINEAR, resize
from numpy import inf, ndarray, ones, zeros
from math import log

# debug
from collect import *
from matplotlib.pyplot import show, plot, xlabel, ylabel
from rasterio import open
from mosaic import *
from write import *
from numpy import linspace
from tqdm import tqdm
from time import sleep


def generate_water_mask(scl: ndarray, dilatation: int) -> ndarray:
    """Generate a water mask without dilated clouds and useless pixels."""
    cloud_mask, useless_mask, water_mask = [zeros(scl.shape) for _ in range(3)]
    sleep(1)
    print_green('\nGenerate clouds and useless pixels')
    for i, row_ in enumerate(tqdm(scl)):
        for j, pixel_ in enumerate(row_):
            if pixel_ in [8, 9, 10, 11]:
                cloud_mask[i, j] = inf
            if pixel_ in [1, 2, 3, 4, 5, 7]:
                useless_mask[i, j] = inf
    cloud_mask = dilate(cloud_mask, ones((dilatation, dilatation)))
    sleep(1)
    print_green('\nGenerate water mask')
    for i, row_ in enumerate(tqdm(scl)):
        for j, pixel_ in enumerate(row_):
            if cloud_mask[i, j] == inf or useless_mask[i, j] == inf:
                water_mask[i, j] = inf
            if useless_mask[i, j] == 1:
                water_mask[i, j] = -inf
    return water_mask


def find_nodata_bounds(img: ndarray) -> [int, int, int, int]:
    """Generates the borders starting from North-West boundary, clockwise."""
    north = list(img[0])
    south = list(img[-1])
    west = list([row[0] for row in img])
    est = list([row[-1] for row in img])
    nw = img[0, 0]
    ne = img[0, -1]
    se = img[-1, -1]
    sw = img[-1, 0]

    i, j = 0, 0
    if nw == 0:
        if sw == 0:
            if ne == 0:
                while est[i] == 0:
                    i += 1
                while south[j] == 0:
                    j += 1
                return i, -1, j, -1
            else:
                while south[j] == 0:
                    j += 1
                return 0, -1, j, -1
        return 0, -1, 0, -1
    if se == 0:
        if ne == 0:
            if sw == 0:
                while west[i] != 0:
                    i += 1
                while north[j] != 0:
                    j += 1
                return 0, i, 0, j
            else:
                while north[j] != 0:
                    j += 1
                return 0, -1, 0, j
    return 0, -1, 0, -1


def apply_mask(img_, mask_):
    """Keeps only the pixels on the background of the mask."""
    result = zeros(img_.shape)
    sleep(1)
    print_green('\nApply mask')
    for i, row_ in enumerate(tqdm(mask_)):
        for j, pixel_ in enumerate(row_):
            if pixel_ == 0:
                result[i, j] = img_[i, j]
    return result


def ratio_transform(band1, band2):
    """Applies the Ratio Transform Algorithm to the bands band1 and band2."""
    result = zeros(band1.shape)
    figure('Log comp')
    v = linspace(6.75, 8.3, 2)
    plot(v, v, color='red')
    xlabel('log(Blue Costal)')
    ylabel('log(Green)')
    sleep(1)
    print_green('\nApply RTA')
    for i, row_ in enumerate(tqdm(band1)):
        for j, pixel_ in enumerate(row_):
            blue, green = band1[i, j], band2[i, j]
            n = 1
            if pixel_ != 0 and blue > 0 and green > 0 and green != 1:
                result[i, j] = log(n * blue) / log(n * green)
                plot(log(n * blue), log(n * green), 'kD', markersize=2)

    return result


def create_rta(scl, band1, band2, dilatation, scale=(False, None)):
    """Creates a new masked image with RTA value for each pixel."""
    if scale[0]:
        size = (int(band1.shape[0] / scale[1]), int(band1.shape[1] / scale[1]))
        scl = resize(scl, size, interpolation=INTER_LINEAR)
        band1 = resize(band1, size, interpolation=INTER_LINEAR)
        band2 = resize(band2, size, interpolation=INTER_LINEAR)
        water_mask = generate_water_mask(scl, dilatation)
        band1_m = apply_mask(band1, water_mask)
        band2_m = apply_mask(band2, water_mask)
    else:
        water_mask = generate_water_mask(scl, dilatation)
        water_mask = resize(water_mask, band1.shape, interpolation=INTER_LINEAR)
        band1_m = apply_mask(band1, water_mask)
        band2_m = apply_mask(band2, water_mask)
    rta_ = ratio_transform(band1_m, band2_m)
    sleep(1)
    print_green('\nCreate RTA')
    for i, row_ in enumerate(tqdm(rta_)):
        for j, pixel_ in enumerate(row_):
            if pixel_ == 0:
                rta_[i, j] = inf
    return rta_


def convert_rta(rta, m0, m1, plot=(False, None, None)):
    """Converts each RTA value into a depth in meters."""
    sleep(1)
    print_green('\nConvert RTA to Depth')
    for i, row in enumerate(tqdm(rta)):
        for j, pixel in enumerate(row):
            if pixel == 0:
                rta[i, j] = inf
            else:
                rta[i, j] = m1 * rta[i, j] - m0
    if plot:
        figure(plot[1])
        imshow(rta, plot[2])
        colorbar()


if __name__ == '__main__':

    base_path = f"/home/fundy/Documents/Constant"

    product = 'S2A_MSIL2A_20220723T153611_N0400_R111_T19UEQ_20220723T221902.SAFE'
    SCL, B2, B3, R10m, R20m = get_jp2_names(product, base_path)
    SCL, B2, B3 = open(f"{R20m}/{SCL}").read(1), open(f"{R20m}/{B2}").read(1), open(f"{R20m}/{B3}").read(1)
    RTA = create_rta(SCL, B2, B3, dilatation=2, scale=(True, 60))
    # figure(f'Full {product}')
    # imshow(RTA, 'ocean')
    # colorbar()
    # XML = f"{base_path}/{product}/MTD_MSIL2A.xml"
    # if nodata_percentage(XML) > 0.1:
    #     SCL = resize(SCL, RTA.shape)
    #     imshow(SCL)
    #     a, b, c, d = find_nodata_bounds(SCL)
    #     print(product, a, b, c, d)
    #     RTA = RTA[a:b, c:d]
    #     figure(f'Cropped {product}')
    #     imshow(RTA, 'ocean')
    #     colorbar()

    # XML = f"{base_path}/{product}/INSPIRE.xml"
    # borders = get_bounds(XML)
    # est, west, south, north = [borders[i] for i in range(4)]

    # data = []
    # for i, row in enumerate(RTA):
    #     for j, pixel in enumerate(row):
    #         if pixel != inf:
    #             lat, lng = transform_p2c(i, j, borders, RTA.shape)
    #             data.append([lat, lng, RTA[i, j]])
    # name = f'{est}_{west}|{south}_{north}'
    # head = ['Latitude', 'Longitude', 'Depth']
    # write_data(name, head, data)

    show()
