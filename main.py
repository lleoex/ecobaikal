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
from ecobaikal_longterm import ecocycle as ec_lt, ens_stat
import oper_tools

from settings import Settings

sets = Settings()

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
    today = datetime.date(2022, 5, 11)
    print(today)
    # загрузка расходов воды по FTP от En+
    #     getQEnPlusApi(today)
    # загрузка ERA5Land до даты Х-8
    # if oper_tools.check_meteo('D:/EcoBaikal/Data/Meteo/Eraland', today - datetime.timedelta(days=8)) == False:
    #     getEra(today)
    #     # сделать bas из tifов ERA5Land
    #     eraProc()
    # else:
    #     print('Данные по реанализу на дату выпуска прогноза уже есть в архиве.')
    # # загрузка GFS на даты Х-8 - Х+10
    # if oper_tools.check_meteo('D:/EcoBaikal/Data/Meteo/GFS/' + today.strftime(format='%Y%m%d'), today) == False:
    #     getGFS(today)
    #     # сделать bas из tifов GFS
    #     gfsProc(today)
    # else:
    #     print('Данные по метеопрогнозам на дату выпуска прогноза уже есть в архиве.')


# запуск Х+0 - Х+10
#     os.chdir(r'd:\EcoBaikal\model')
#     params = read_params('baikal_x+10.txt')
#     ec_st([today], 10, params)
# графика Х+10

    # oper_tools.graphShort(os.path.join(sets.SHORT_RES, '/', today.strftime('%Y%m%d'), '/', sets.SOURCE_NAME))
# рассылка Х+10


# долгосрочный прогноз
#     params = read_params(os.path.join(sets.ROOT_DIR, sets.MODEL_DIR, 'baikal_x+60.txt'))
#     ec_lt([today + datetime.timedelta(days=10)], 2, params)
    ens = sets.ROOT_DIR + '/' + sets.LONG_RES + '/' + str(datetime.date(today.year, today.month + 3, 1).strftime('%Y%m%d')) + '_ens.txt'
    ens_stat(ens)







