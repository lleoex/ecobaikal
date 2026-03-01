#!/usr/bin/env python
# coding: utf-8
import datetime
from time import strftime

import rioxarray
# import rasterio
import pandas as pd
import geopandas as gp
import os
import glob
import datetime as dt
import netCDF4
from netCDF4 import num2date
import matplotlib.pyplot as plt
import xarray as xr
# from Demos.BackupRead_BackupWrite import outfile

from settings import Settings
from era2bas import append_dates, makeBas, genMS

sets = Settings()

def read_seas_nc(file):
    '''

    :param file:
    :return:
    '''
    # print(file)
    xds = xr.open_dataset(file, decode_times=True, drop_variables='forecast_period')
    var = xds.data_vars.keys()
    df = xds.to_dataframe()
    df = df.reset_index()
    return(df)


def nc2bas(file):
    '''

    :param file:
    :return:
    '''
    df = read_seas_nc(file)
    ens = df['number'].unique()
    for s in ens:
        ldf = df[df['number'] == s]
        date_reference = pd.to_datetime(df['forecast_reference_time'].unique()).tolist()
        savepath = os.path.join(sets.S2S_BAS_DIR, date_reference[0].strftime("%Y%m%d"), str(s))
        print(savepath)
        if not os.path.exists(savepath):
            os.makedirs(savepath)

        # делаем геодатафрейм для обрезки по контуру водосбора и генерирования файла расположения точек
        gdf = gp.GeoDataFrame(ldf, geometry=gp.points_from_xy(ldf['longitude'], ldf['latitude']), crs='EPSG:4326')
        # буфер водосбора для обрезки точек (с ~20000 до 9000)
        poly = gp.read_file('D:/Data/ERA5Land/shp/baikal_basin_buff10km.shp')
        # пересечение по пространству
        gdf = gp.sjoin(gdf, poly)
        if not os.path.exists(os.path.join(savepath, 'MeteoStation.bas')):
            os.chdir(savepath)
            genMS(gdf[gdf['valid_time'] == gdf['valid_time'].min()].reset_index(drop=True))

        # генерирование файла с переменной
        if 't2m' in gdf.columns:
            savename = "TEMP" + str(date_reference[0].year)[2:4] + '.BAS'
            gdf = gdf.loc[:,['latitude', 'longitude', 'valid_time', 't2m']]
            gdf['t2m'] = gdf['t2m'] - 273.15
            gdf = gdf.pivot(columns=['latitude', 'longitude'], index='valid_time', values='t2m')
            gdf.columns = range(gdf.shape[1])
            makeBas(gdf, savepath, 'temp')
        elif 'tp' in gdf.columns:
            savename = "PRE" + str(date_reference[0].year)[2:4] + '.BAS'
            gdf = gdf.loc[:, ['latitude', 'longitude', 'valid_time', 'tp']]
            gdf['tp'] = gdf['tp'] * 1000
            gdf = gdf.pivot(columns=['latitude', 'longitude'], index='valid_time', values='tp')
            gdf = gdf.diff() # по умолчанию в прогнозе накопленная сумма за 24 часа, меняем ее на суточные суммы
            gdf.columns = range(gdf.shape[1])
            makeBas(gdf, savepath, 'prec')
        print(os.path.join(savepath, savename))

        # print(ldf.head())
    # print(df.head())






# главный модуль
if __name__ == "__main__":
    # Папки с ежедневными tif-файлами
    path_data = sets.S2S_NC_DIR
    # for var in ['temperature', 'precipitation']:
    #     path = os.path.join(path_data, '*' + var + '.nc')
    ListDir = glob.glob(os.path.join(path_data, '*.nc'), recursive=True)
    # print(ListDir)
    for file in ListDir:
        df = nc2bas(file)
        # print(path_data)