"""
Copyright 2022 © Centre Interdisciplinaire de développement en Cartographie des Océans (CIDCO), Tous droits réservés
@Samuel_Dubos
"""

from pandas.core.frame import DataFrame
from pandas import concat, read_csv
from numpy import array, savetxt
from tqdm import tqdm
from iso8601 import parse_date
import sys
from datetime import timedelta


def generate_src_dataframes(base_: str, date_: str) -> [DataFrame, DataFrame, DataFrame]:
    """Generates the source Dataframes in the right format."""
    sonar = f'{base_}/{date_}_sonar.txt'
    imu = f'{base_}/{date_}_imu.txt'
    gnss = f'{base_}/{date_}_gnss.txt'
    sonar_df = read_csv(sonar, sep=';')
    imu_df = read_csv(imu, sep=';')
    gnss_df = read_csv(gnss, sep=';')

    return sonar_df, imu_df, gnss_df


def interpolate(f_a: float, f_b: float, a: str, b: str, x: str) -> float:
    """Interpolates the function f on the time-interval [a, b] for time = x."""
    x = parse_date(str(x))
    a = parse_date(str(a))
    b = parse_date(str(b))

    return f_a + (f_b - f_a) * (x - a) / (b - a)


def get_start_stop(base_path, date):

    sonar_dataframe, imu_dataframe, gnss_dataframe = generate_src_dataframes(base_path, date)
    start = max(sonar_dataframe['Timestamp'][0], imu_dataframe['Timestamp'][0], gnss_dataframe['Timestamp'][0])
    stop = min(str(sonar_dataframe['Timestamp'][len(sonar_dataframe.index) - 1]),
               str(imu_dataframe['Timestamp'][len(imu_dataframe.index) - 1]),
               str(gnss_dataframe['Timestamp'][len(gnss_dataframe.index) - 1]))

    return start, stop


def generate_interpolated_out_dataframe(pings: list, gnss_df: DataFrame, imu_df: DataFrame) -> DataFrame:
    """Generates an interpolated DataFrame over a given pings list."""
    columns = ['Heading', 'Pitch', 'Roll', 'Latitude', 'Longitude', 'EllipsoidalHeight']
    df_out = DataFrame(columns=columns)
    imu_index, gnss_index = 0, 0

    for ping in tqdm(pings):

        while imu_index + 1 < len(imu_df.index) and imu_df['Timestamp'][imu_index + 1] < ping:
            imu_index += 1

        if imu_index >= len(imu_df.index) - 1:
            sys.stderr.write(f'\nNo attitude available for ping {ping} with '
                             f'gnss_index = {gnss_index} and imu_index = {imu_index}.')
            break

        while gnss_index + 1 < len(gnss_df.index) and gnss_df['Timestamp'][gnss_index + 1] < ping:
            gnss_index += 1

        if gnss_index >= len(gnss_df.index) - 1:
            sys.stderr.write(f'No position available for ping {ping} with '
                             f'gnss_index = {gnss_index} and imu_index = {imu_index}.')
            break

        if imu_df['Timestamp'][imu_index] > ping or gnss_df['Timestamp'][gnss_index] > ping:
            sys.stderr.write(f'Rejecting ping {ping} with '
                             f'gnss_index = {gnss_index} and imu_index = {imu_index}.')
            continue

        heading_col, pitch_col, roll_col = imu_df['Heading'], imu_df['Pitch'], imu_df['Roll']
        latitude_col, longitude_col, height_col = gnss_df['Latitude'], gnss_df['Longitude'], gnss_df['EllipsoidalHeight']

        before_heading, after_heading = heading_col[imu_index], heading_col[imu_index + 1]
        before_pitch, after_pitch = pitch_col[imu_index], pitch_col[imu_index + 1]
        before_roll, after_roll = roll_col[imu_index], roll_col[imu_index + 1]
        before_latitude, after_latitude = latitude_col[gnss_index], latitude_col[gnss_index + 1]
        before_longitude, after_longitude = longitude_col[gnss_index], longitude_col[gnss_index + 1]
        before_height, after_height = height_col[gnss_index], height_col[gnss_index + 1]

        imu_time, gnss_time = imu_df['Timestamp'], gnss_df['Timestamp']

        heading = interpolate(before_heading, after_heading, imu_time[imu_index], imu_time[imu_index + 1], ping)
        pitch = interpolate(before_pitch, after_pitch, imu_time[imu_index], imu_time[imu_index + 1], ping)
        roll = interpolate(before_roll, after_roll, imu_time[imu_index], imu_time[imu_index + 1], ping)
        latitude = interpolate(before_latitude, after_latitude, gnss_time[gnss_index], gnss_time[gnss_index + 1], ping)
        longitude = interpolate(before_longitude, after_longitude, gnss_time[gnss_index], gnss_time[gnss_index + 1],
                                ping)
        height = interpolate(before_height, after_height, gnss_time[gnss_index], gnss_time[gnss_index + 1], ping)

        data = [heading, pitch, roll, latitude, longitude, height]
        new_row = DataFrame(data=array([data]), columns=columns)
        df_out = concat([df_out, new_row], ignore_index=True)

    return df_out


def generate_pings(start, stop, days=0, hours=0, minutes=0, seconds=0, microseconds=0):

    dates, date = [], start
    while date < stop:
        dates.append(date)
        date = parse_date(date)
        date = date + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)
        date = str(date)

    return dates


def organize_data(base_path, target_path, date, pings, speed):

    sonar_dataframe, imu_dataframe, gnss_dataframe = generate_src_dataframes(base_path, date)
    temporary_dataframe = generate_interpolated_out_dataframe(pings, gnss_dataframe, imu_dataframe)
    temporary_dataframe['TravelTime'] = 2 * temporary_dataframe['EllipsoidalHeight'] / speed
    columns = ['TravelTime', 'Latitude', 'Longitude', 'EllipsoidalHeight', 'Heading', 'Pitch', 'Roll']
    data_frame = temporary_dataframe[columns]
    savetxt(f'{target_path}/{date}.dat', data_frame.values)

    est_bd = max(gnss_dataframe['Longitude'])
    west_bd = min(gnss_dataframe['Longitude'])
    south_bd = min(gnss_dataframe['Latitude'])
    north_bd = max(gnss_dataframe['Latitude'])

    return est_bd, west_bd, south_bd, north_bd


if __name__ == '__main__':

    base_path = '/home/fundy/Documents/main_test/raw'
    ref = '2022.06.01_065424'
    sonar_data_frame, imu_data_frame, gnss_data_frame = generate_src_dataframes(base_path, ref)
    start, stop = get_start_stop(base_path, ref)
    Pings = generate_pings(start, stop, minutes=5)
    df = generate_interpolated_out_dataframe(Pings, gnss_data_frame, imu_data_frame)
    print(df)

    # pings = generate_pings('2022-07-16 14:00:00.000000', '2022-07-16 23:00:00.000000',
    #                        hours=2, minutes=27, seconds=13, microseconds=681231)
    # print(pings)

    # organize_data(base_path, '/home/fundy/Documents/main_test', date, Pings, 1500)
