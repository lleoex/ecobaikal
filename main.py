# coding=utf-8
import time
import datetime
import os
from time import strftime
import pandas as pd
from EE_export import getEra, getGFS
from era2bas import eraProc
from gfs2bas import gfsProc
from ecobaikal_shortterm import read_params, ecocycle as ec_st
import oper_tools

def getQEnPlusApi(date):
    '''

    :param date:
    :return:
    '''
    print('Запрашиваем данные о расходах воды за ', date)
    try:
        # df = pd.read_excel('D:/Data/Hydro/' + date.strftime(format='%Y-%m-%d') + '_расчетный_среднесуточный.xlsx',
        #                    header=None, names=['date', 'post', 'lev', 'q'], skiprows=1)
        df = pd.read_excel('D:/Data/Hydro/buryat_q_2022.xlsx')
    except FileNotFoundError:
        sendNoQAlert(date)
        exit()
    else:
        if df[df['date'].dt.date == date].shape[0] > 0:
            print("Данные о расходах за ", date, " получены")
        else:
            print("Файл расходов есть. В файле нет данных о расходах за ", date)
            sendNoQAlert(date)
    finally:
        print("Процедура получения расходов за ", date, " завершена")
    print(df.head())


def sendNoQAlert(date):
    '''

    :param date:
    :return:
    '''
    print('Не получены данные о расходах воды за ', date)


# Основной скрипт запуска цепочки бесшовного прогноза.
if __name__ == '__main__':
    # today =  datetime.date.today()
    today = datetime.date(2022, 4, 13)
    print(today)
# загрузка расходов воды по FTP от En+
    getQEnPlusApi(today)
# загрузка ERA5Land до даты Х-8
    getEra(today)
# сделать bas из tifов ERA5Land
    eraProc()
# загрузка GFS на даты Х-8 - Х+10
    getGFS(today)
# сделать bas из tifов GFS
    gfsProc(today)
# запуск Х+0 - Х+10
    os.chdir(r'd:\EcoBaikal\model')
    params = read_params('baikal_x+10.txt')
    ec_st([today], 10, params)
# коррекция Х+10
    date = today + datetime.timedelta(days=10)
    pathCoeff = 'd:/EcoBaikal/Basin/Baik/Bas/X10_corr.bas'
    pathFactQ = 'd:/Data/Hydro/buryat_q_2022.xlsx'
    oper_tools.short_corr(date, pathCoeff, pathFactQ)
# графика Х+10

# рассылка Х+10







