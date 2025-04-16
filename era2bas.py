# -*- coding: utf-8 -*-
#%%
import datetime

import matplotlib.pyplot
import rioxarray
import geopandas as gp
import glob
import pandas as pd
import os

from settings import Settings

sets = Settings()


def tif2df(filePath:str, var:str):
    '''

    :param wd:
    :param filePath:
    :param var:
    :return:
    '''
    # print(x)
    d = datetime.datetime.strptime(filePath[filePath.rfind('\\') + 1:filePath.find('.')], '%Y%m%d') # Извлекаем из названия дату (без расширения), переводим её в нужный формат
    # переводим tif в df
    grd = rioxarray.open_rasterio(filePath) # Открываем текущий tif-файл
    df = grd[0].to_dataframe(name='value').reset_index()[['y', 'x', 'value']]# преобразуем его во фрейм
    grd.close() # закрываем растр, освобождаем память
    del grd
    # делаем gdf
    df = gp.GeoDataFrame(df, geometry=gp.points_from_xy(df['x'], df['y']), crs='EPSG:4326')
    # буфер водосбора для обрезки точек (с ~20000 до 9000)
    poly = gp.read_file(os.path.join(sets.ERA_TIFF_DIR,'shp','baikal_basin_buff10km.shp')).to_crs(crs=4326)
    # пересечение по пространству
    df = gp.sjoin(df, poly)
    # вытаскиваем каждую третью точку (для оптимизации размера), только значения без координат
    df = df.iloc[::3, :]
    if var == 'prec':  # обработка файлов с осадками
        df['value'] = df['value'] * 1000
    elif var == 'temp':
        df['value'] = df['value'] - 273.15
    # print(df.head())
    dat = df['value'].T # транспонируем в строку
    dat = pd.concat([pd.Series(d), dat], ignore_index=False) # добавляем дату как первый элемент
    # print(dat)
    return dat
    del(dat)


def append_dates(df):
    # print(df.head())
    # проверяем, за один ли год у нас данные
    if df.index.min().year == df.index.max().year:
        # если данные за один год, то проверяем, начинаются ли они с 1 января
        if df.index.min().month != 1: # & df.index.min().day != 1
            # если не с 1 января, то делаем пустой датафрейм с датами от 1 января до начала данных
            attic = pd.date_range(start=str(df.index.min().year) + '-01-01',
                                  end=str(df.index.min() - datetime.timedelta(days=1)))
            attic = pd.DataFrame(attic, columns=['date'])
            attic = attic.set_index(['date'])
            # присоединяем к данным
            # df = df.append(attic)
            df = pd.concat([df, attic], ignore_index=False)

        # проверяем, заканчиваются ли данные 31 декабря
        if df.index.max().month != 12:  # & df.index.max().day != 31:
            # если не до 31 декабря, то делаем пустой датафрейм с датами от конца данных до 31 декабря
            cellar = pd.date_range(start=str(df.index.max() + datetime.timedelta(days=1)),
                                   end=str(df.index.min().year) + '-12-31')
            cellar = pd.DataFrame(cellar, columns=['date'])
            cellar = cellar.set_index(['date'])
            # присоединяем к данным
            df = pd.concat([df, cellar], ignore_index=False)
    # так как все перемешано, сортируем данные по индексу
        df = df.sort_index()
        return(df)


def MSFromTif(x, toDir):
    '''

    :param x:
    :return:
    '''
    # путь до файла
    wd = dir_path = os.path.dirname(os.path.realpath(x))
    os.chdir(wd)
    # print(wd)
    grd = rioxarray.open_rasterio(x) # Открываем текущий tif-файл
    df = grd[0].to_dataframe(name='value').reset_index()[['y', 'x', 'value']]# преобразуем его во фрейм
    grd.close() # закрываем растр, освобождаем память
    del grd
    # делаем gdf
    df = gp.GeoDataFrame(df, geometry=gp.points_from_xy(df['x'], df['y']), crs='EPSG:4326')
    # буфер водосбора для обрезки точек (с ~20000 до 9000)
    poly = gp.read_file('D:/Data/ERA5Land/shp/baikal_basin_buff10km.shp')
    # пересечение по пространству
    df = gp.sjoin(df, poly)
    # вытаскиваем каждую третью точку (для оптимизации размера), только значения без координат
    df = df.iloc[::3, :]
    # делаем MeteoStation.bas
    os.chdir(toDir)
    genMS(df)


def genMS(df):
    '''

    :param df:
    :return:
    '''
    print('Generating MS file in ' + os.getcwd())
    las = "+proj=laea +lat_0=45 +lon_0=100 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +R=6371200"
    print('type', type(df))
    df = df.to_crs(las)
    df['H'] = 0
    df['Name'] = df.index
    df['lon'] = df['geometry'].x
    df['lat'] = df['geometry'].y
    # пишем в файл
    with open('MeteoStation.bas', 'w') as f:
        f.write(r'Number, X_AS, Y_AS, H, Name' + '\n')
        f.write(str(len(df.index)) + '\n')
        contents = df[['lon', 'lat', 'H', 'Name']].sort_index().reset_index().to_csv(na_rep=' -99.00',
                                                                                     header=False,
                                                                        float_format='%7.2f',
                                                                        index=False, lineterminator='\n')
        f.write(contents)
        f.close()

def makeBas(df, wd, var):
    '''

    :param df:
    :param wd:
    :param var:
    :return:
    '''
    # print(df + ' ' + var)
    # делаем файл с правильным названием
    if var == 'prec':  # обработка файлов с осадками
        outfile = 'PRE' + str(df.index.min().year)[-2:] + '.bas'
    elif var == 'temp':
        outfile = 'TEMP' + str(df.index.min().year)[-2:] + '.bas'

    # добавляем NA с 1 января и до 31 декабря, если их нет
    df = append_dates(df)

    # пишем в файл
    os.chdir(wd)
    with open(outfile, 'w') as f:

        # пишем в него хэдер
        if var == 'prec':
            f.write(r'Precipitation, mm' + '\n')
        elif var == 'temp':
            f.write(r'Temperature, oC' + '\n')
        # elif var == 'd2m':
        #     f.write(r'Deficit, hPa' + '\n')
        # количество станций и дней в файле
        f.write(str(len(df.columns)) + ' ' + str(len(df.index)) + '\n')
        # номера всех станций
        f.write(','.join([str(x) for x in df.columns.values]) + '\n')
        # три
        f.write('\n')
        # пустых
        f.write('\n')
        # строки
        f.write('\n')
        # данные, причем в виде форматированной строки и заменяем в них запятую на пробел
        cont = df.astype(float).round(3).to_csv(na_rep=' -99.00', lineterminator='\n',
                                                date_format='%Y%m%d', header=False,
                                                float_format='%7.2f')
        cont = cont.replace(',', ' ')
        f.write(cont)
        f.close()


def workflow(dt:datetime, fromDir, toDir, var):
    '''
    :param fromDir:
    :param toDir:
    :param var:
    :return:
    '''


    # добавить разбивку по годам исходных файлов
    for v in var:
        vardir = os.path.join(fromDir, v)
        #os.chdir(fromDir)
        #os.chdir(fromDir + '/' + i)
        # print(os.getcwd())
        pattern = vardir + '/' + f'{dt.year}*.tif' # если нужен только один год то поставить 'ХХХХ*.tif' - изменить
        ListFiles = glob.glob(pattern, recursive=True)  # Список файлов tif на каждую дату
        print(ListFiles)
        all_df = pd.DataFrame()  # пустой список для записи фреймов за каждую дату
        for f in ListFiles:  # цикл по файлам
            print(f)
            # если нет MeteoStation.bas в toDir, то делаем его
            if not os.path.isfile(toDir + '/MeteoStation.bas'):
                #MSFromTif(f, toDir)
                #os.chdir(fromDir)
                print()
            dat = tif2df(f, v)
            all_df = pd.concat([all_df, dat], axis=1, ignore_index=True)
        all_df = all_df.T
        # print(all_df.head())
        all_df.index = all_df[0]
        all_df.drop(0, axis=1, inplace=True)
        # all_df.to_csv(i + '.csv', sep = ';')
        for y in all_df.index.year.unique():
            makeBas(all_df.loc[str(y)], toDir, v)


def eraProc(dt:datetime):
    # all files in wd
    fromDir = sets.ERA_TIFF_DIR
    toDir = sets.ERA_BAS_DIR
    var = ['temp', 'prec']
    workflow(dt, fromDir, toDir, var)


# главный модуль
if __name__ == "__main__":
    # all files in wd
    fromDir = 'D:/Data/ERA5Land/'
    toDir = 'D:/EcoBaikal/Data/Meteo/Eraland/'
    var = ['temp', 'prec']
    workflow(datetime.date(2024, 1, 1), fromDir, toDir, var)

    # one specific file
    # df = pd.read_csv(r'd:/EcoMeteo/Era5Land/baikal/total_precipitation/total_precipitation_1997.csv',
    #                  index_col='0', sep=';', parse_dates=['0'])
    # makeBas(df, r'd:/EcoMeteo/Era5Land/baikal/', 'total_precipitation')

