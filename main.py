# coding=utf-8
import time
import datetime
import os
from time import strftime

import pandas as pd

from EE_export import getEra, getGFS
from era2bas import eraProc
from gfs2bas import gfsProc
# пример функции
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def getQEnPlusApi(date):
    '''

    :param date:
    :return:
    '''
    print('Запрашиваем данные о расходах воды за ', date)
    try:
        df = pd.read_excel('D:/Data/Hydro/' + date.strftime(format='%Y-%m-%d') + '_расчетный_среднесуточный.xlsx',
                           header=None, names=['date', 'post', 'lev', 'q'], skiprows=1)
    except FileNotFoundError:
        sendNoQAlert(date)
        exit()
    else:
        print("Данные о расходах за ", date, " получены")
    finally:
        print("Процедура получения расходов за ", date, " завершена")

    print(df.head())


def sendNoQAlert(date):
    '''

    :param date:
    :return:
    '''
    print('Нет данных по расходам воды за ', date)


# Основной скрипт запуска цепочки бесшовного прогноза.
if __name__ == '__main__':
    print_hi('PyCharm')
    # today =  datetime.date.today()
    today = datetime.date(2025, 4, 2)
    print(today)
# загрузка расходов воды по FTP от En+
#     getQEnPlusApi(today)
# загрузка ERA5Land до даты Х-8
#     getEra(today)
# сделать bas из tifов ERA5Land
#     eraProc()
# загрузка GFS на даты Х-8 - Х+10
#     getGFS(today)
# сделать bas из tifов GFS
#     gfsProc(today)









