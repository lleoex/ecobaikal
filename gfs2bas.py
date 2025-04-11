# -*- coding: utf-8 -*-
import os
import glob
import pandas as pd
from datetime import date, datetime, timedelta
from rasterio import open as rio_open
import re
import shutil
import numpy as np
from era2bas import makeBas

def tif2df(file):
    df = pd.DataFrame()
    with rio_open(file) as rst:
        date = os.path.basename(file)[0:10]
        horizon = int(re.findall('\+(\d*).', os.path.basename(file))[0])
        row = rst.read(1).flatten()
        rst.close()
        add = pd.DataFrame(row)
        add.index += 1
        df = pd.concat([df, add.T], ignore_index=True)
        df.insert(0,'date', date)
        df.insert(1,'horizon', horizon)
    return df

def tifProc(dir):
    os.chdir(dir)
    pattern = str('*.tif')  # если нужен только один год то поставить 'ХХХХ*.tif'
    listFiles = glob.glob(pattern, recursive=True)  # Список файлов tif на каждую дату
    print(listFiles)
    df = pd.DataFrame()
    for f in listFiles:
        print(f)
        df = pd.concat([df, tif2df(f)])
    return df


def makeFcstBas(df, wd, var, date):
    '''

    :param df:
    :param wd:
    :param var:
    :param date:
    :return:
    '''

    # делаем директорию для прогнозных файлов
    directory = date.strftime("%Y%m%d")
    if not os.path.exists(wd + '/GFS/' + directory):
        os.makedirs(wd + '/GFS/' + directory)


    # делаем файл с правильным названием
    if var == 'prec':  # обработка файлов с осадками
        outfile = 'PRE' + str(df.index.min().year)[-2:] + '.bas'
        # print(outfile)
    elif var == 'temp':
        outfile = 'TEMP' + str(df.index.min().year)[-2:] + '.bas'
        # print(outfile)
    # elif var == 'hurs':
    #     outfile = 'DEF' + str(df.index.min().year)[-2:] + '.bas'

    if 'directory' in locals():
        os.chdir(wd + '/GFS/' + directory)
    else:
        os.chdir(wd)

    # добавляем NA с 1 января и до 31 декабря, если их нет
    df = append_dates(df)

    print(os.getcwd())
    # пишем в файл
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
                                                date_format='%Y%m%d', header=False, float_format='%7.2f')
        cont = cont.replace(',', ' ')
        f.write(cont)
        f.close()
    shutil.copy2('d:/EcoBaikal/Data/Meteo/GFS/MeteoStation.bas', os.getcwd())
    os.chdir(wd)


def append_dates(df):
    # print(df.head())
    # проверяем, за один ли год у нас данные
    if df.index.min().year == df.index.max().year:
        # если данные за один год, то проверяем, начинаются ли они с 1 января
        if df.index.min().month != 1: # & df.index.min().day != 1
            # если не с 1 января, то делаем пустой датафрейм с датами от 1 января до начала данных
            attic = pd.date_range(start=str(df.index.min().year) + '-01-01',
                                  end=str(df.index.min() - timedelta(days=1))).date
            attic = pd.DataFrame(attic, columns=['date'])
            attic = attic.set_index(['date'])
            # присоединяем к данным
            df = pd.concat([df, attic], ignore_index=False)
            df = df.sort_index()
        print(df.index.min().month)

        # проверяем, заканчиваются ли данные 31 декабря
        if df.index.max().month != 12:  # & df.index.max().day != 31:
            # если не до 31 декабря, то делаем пустой датафрейм с датами от конца данных до 31 декабря
            cellar = pd.date_range(start=str(df.index.max() + timedelta(days=1)),
                                   end=str(df.index.min().year) + '-12-31').date
            cellar = pd.DataFrame(cellar, columns=['date'])
            cellar = cellar.set_index(['date'])
            # присоединяем к данным
            df = pd.concat([df, cellar], ignore_index=False)
        # так как все перемешано, сортируем данные по индексу
        df = df.sort_index()
        return(df)


def workflow(wd, outDir, var, date):
    '''

    :param wd:
    :param var:
    :return:
    '''
    for v in var:
        os.chdir(wd)
        print(os.getcwd())
        df = tifProc(wd + v)
        df.index = pd.to_datetime(df['date'])
        # для GFS0
        gfs_0 = df[df['horizon'] == 0]
        makeBas(gfs_0.drop(['date', 'horizon'], axis=1), outDir + '/' + 'GFS_0', v)
        print('Подготовлены данные GFS для ', date)
        # для обычных прогнозов
        gfs = df[df.index.date == date]
        gfs['date'] = gfs.index.date + pd.to_timedelta(gfs['horizon'], 'd')
        gfs.index = gfs['date']
        gfs = gfs.drop(['date', 'horizon'], axis=1)
        makeFcstBas(gfs, outDir, v, date)
        print('Подготовлены данные GFS для ', date, ' - ', (date + timedelta(days=10)))


def gfsProc(today):
    wd = 'd:/Data/GFS/'
    outDir = 'd:/EcoBaikal/Data/Meteo/'
    var = ['temp', 'prec']

    workflow(wd, outDir, var, today)




if __name__ == "__main__":
    gfsProc(date.today())
    # однократная генерация MeteoStation.bas из tif GFS
    # MSFromTif(r'd:\EcoMeteo\GFS\baikal\t2m_above_ground\2016-10-31+9.tif')

    # генерация GFS_0 из GFS_XXXX.xlsx после R скрипта для контрольных точек
    # for v in var:
    #     os.chdir(wd + '/' + v)
    #     f = glob.glob('GFS*')
    #     print(f)
    #     for i in f:
    #         os.chdir(wd + '/' + v)
    #         df = pd.read_excel(i)
    #         df = df.loc[df['horizon'] == 0]
    #         # print(df.head())
    #         df = append_dates(df)
    #         makeFcstBas(df, r'd:\EcoBaikal\Data\Meteo\GFS_0', v)

