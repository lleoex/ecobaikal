# coding=utf-8
import time
import datetime
import matplotlib.pyplot as plt
import os
import subprocess
import pandas as pd
from datetime import timedelta
from dateutils import relativedelta
import argparse
# import logging
# from logging.handlers import RotatingFileHandler
from oper_tools import check_meteo, short_corr, graphShort
from settings import Settings

sets = Settings()

def ecorun(date_start, date_end, meteo_path, hydro_path, baspath, exepath, exename, ens_flag, dir_CT, dir_out,
           source_name, year_start, year_end):
    """
        Запуск расчета по модели ECOMAG

        :param date_start: дата начала расчета
        :type date_start: datetime.date
        :param date_end: дата конца расчета
        :type date_end: datetime.date
        :param meteo_path: полный путь к директории с метеоданными
        :type meteo_path: str
        :param baspath: полный путь к директории Bas
        :type baspath: str
        :param exepath: полный путь к директории model
        :type exepath: str
        :param exename: имя исполняемого файла модели
        :type exename: str
        :param ens_flag: str указатель типа расчета (diagnosis, ensemble)
        :type ens_flag: str
        :param dir_CT: str полный путь к директории с начальными условиями (контрольная точка)
        :type dir_CT: str
        :param dir_out: str полный путь к директории с результатами
        :type dir_out: str

        """

    print(date_start, date_end, meteo_path, baspath, exepath, ens_flag, dir_CT, dir_out)
    # проверка наличия директории и файла для записи - без Critery.rez не запустится ECOMAG
    newdirout = dir_out + '\\' + date_end.strftime("%Y%m%d")
    # если нет такой директории, он создаст ее сам и в ней пустой файл Critery.rez
    if not os.path.exists(newdirout):
        os.makedirs(newdirout)
        open(newdirout + '\Critery.rez', 'w').close()

    # пишем в atime.bas новые даты, дни года и продолжительность расчета
    atime = open(baspath + '\\' +'atime.bas', 'w')
    atime.truncate()
    atime.write(date_start.strftime("%d.%m.%Y") + " " + date_end.strftime("%d.%m.%Y") + '\n')
    atime.write(str(date_start.timetuple().tm_yday) + " " + str(abs(date_end - date_start).days))
    atime.close()

    # меняем значения в kpoint.bas в зависимости от варианта расчета: "0" если ансамбль, "2" если диагноз
    with open(baspath + '\kpoint.bas', 'w') as kpt:
        kpt.truncate()
        if ens_flag == 'diagnosis':
            kpt.write('2 1 1')
        elif ens_flag == 'ensemble':
            kpt.write('0 1 1')
        kpt.close()

    # читаем из pathen.bas старые настройки и меняем их по очереди
    with open(exepath + '\pathen.bas', 'r+') as pathen:
        lines = pathen.read().splitlines()
       # print(lines)
        lines[0] = baspath
        # lines[1] = baspath.replace("Bas", "Graf")
        # lines[2] = baspath.replace("e\\Bas", "e\\Result", )
        lines[1] = baspath[0:-4] + '\\Graf'
        lines[2] = baspath[0:-4] + '\\Result'
        # метеорология
        lines[3] = meteo_path
        # контрольная точка - каждый раз разная
        lines[6] = dir_CT + '\\' + date_start.strftime("%Y%m%d")
        # print(lines[6])
        # выходной каталог
        lines[5] = dir_out + '\\' + date_end.strftime("%Y%m%d")
        # print(lines[5])
        # print('init', lines)
        # перематываем файл в начало и переписываем его с новыми значениями
        pathen.seek(0)
        pathen.writelines(["%s\n" % item for item in lines])

    # запускаем расчет
    os.chdir(exepath)
    with subprocess.Popen(exepath + '\\' + exename, shell=True, stderr=subprocess.PIPE) as result:
        _, err = result.communicate()
        if err:
            print(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + err.decode("utf-8"))
        print(result)

def ecocycle(dates, lead, params):
    """

    :param dates:       список со всеми датами начала расчета
    :param lead:        заблаговременность
    :param params:      список с параметрами
    :return:
    """
    # проверка на совпадение директорий для КТ и результатов
    if params['dir_CT'] == params['dir_out']:
        print('Директории для сохранения начальных условий и результатов расчета совпадают. Пожалуйста, измените!')
        quit()

    # меняем значения в basin.bas в зависимости от типа прогноза: 4 створа если краткосрочный, 1 если долгосрочный
    with open(params['baspath'] + '/basin.bas', 'w') as bas:
        bas.truncate()
        bas.write('4 \n 1 2 3 4')
        bas.close()

    # цикл по всем пришедшим датам
    for date in dates:
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        # расчет по ERA5Land
        model_end = date - timedelta(days=8)
        # проверка на наличие КТ для начала расчета
        fn = params['dir_CT'] + '\\' + model_end.strftime("%Y%m%d") + '\\INPCURV.BAS'
        # print(fn)
        # if os.path.isfile(fn) == False:
        # расчет КТ при ее отсутствии
        print('Отсутствует контрольная точка. Выполняется расчет')
        if not os.path.isfile(params['dir_CT'] + '\\' +
                              datetime.date(model_end.year, 4, 1).strftime("%Y%m%d") +
                              '\\INPCURV.BAS'):
            model_start = datetime.date(model_end.year, 1, 1)
        elif not os.path.isfile(params['dir_CT'] + '\\' +
                              datetime.date(model_end.year, 1, 1).strftime("%Y%m%d") +
                              '\\INPCURV.BAS'):
            model_start = datetime.date(2022, 1, 1)
        else:
            model_start = datetime.date(model_end.year, 4, 1)

        old_meteo = params['meteo_path']
        params['meteo_path'] = params['meteo_path'] + '\\Eraland\\'
        old_dir_out = params['dir_out']
        params['dir_out'] = params['dir_CT']
        print('ERA5Land', model_start, model_end, params['meteo_path'], params['dir_out'])
        ecorun(model_start, model_end, **params)
        params['dir_out'] = old_dir_out  # возвращаем директорию для результатов Archive/002/RES
        params['meteo_path'] = old_meteo  # возвращаем общий путь, откуда берем метео

        # расчет по GFS_0
        model_start = model_end
        model_end = date
        # КТ по GFS0 для начала расчета
        old_meteo = params['meteo_path'] # сохраняем общий путь, откуда берем метео
        params['meteo_path'] = params['meteo_path'] + '\\GFS\\' # меняем путь, откуда берем метео - из GFS0
        old_dir_out = params['dir_out'] # сохраняем директорию для результатов Archive/002/RES
        params['dir_out'] = params['dir_CT'] # меняем директорию вывода на Archive/002/CT
        print('GFS_0', model_start, model_end, params['meteo_path'], params['dir_out'])
        ecorun(model_start, model_end, **params) # расчет по GFS0
        params['dir_out'] = old_dir_out # возвращаем директорию для результатов Archive/002/RES
        params['meteo_path'] = old_meteo # возвращаем общий путь, откуда берем метео


        # сам прогноз
        # print(r'Старт прогноза')
        # для метеорологических (не ансамблевых) прогнозов меняем папку с метео на нужную, сохраняя старую
        old_meteo = params['meteo_path']
        params['meteo_path'] = params['meteo_path'] + '\\GFS\\' + date.strftime("%Y%m%d") + '\\'
        model_start = date
        model_end = model_start + datetime.timedelta(days=lead)
        print(r'Старт прогноза по GFS', model_start, model_end, params['meteo_path'], params['dir_out'])
        # первый расчет прогноза без коррекции
        ecorun(model_start, model_end, **params)

        # коррекция и запись sbrosXX.bas
        short_corr(date=date)
        # запуск прогноза с заливкой sbrosXX.bas
        # меняем значения в inflow.bas в зависимости от варианта расчета: "0" если прогноз створам, "4" если в Байкал
        with open(params['baspath'] + '\inflow.bas', 'w') as sbros:
            sbros.truncate()
            sbros.write(' 3 \n 1 2 3')
            sbros.close()

        # второй расчет прогноза с коррекцией
        ecorun(model_start, model_end, **params)
        # выключаем сбросы в inflow.bas
        with open(params['baspath'] + '\inflow.bas', 'w') as sbros:
            sbros.truncate()
            sbros.write(' 0 \n 1 2 3')
            sbros.close()
        params['meteo_path'] = old_meteo

        # graphShort(params['dir_out'] + '/' + model_end.strftime("%Y%m%d") + '/' + params['source_name'])


def read_params(param_path):
    with open(param_path) as f:
        params = dict(x.rstrip().split(",", 1) for x in f)
    f.close()
    return params


def datelist(date_start, date_end, freq_type, freq):
    # массив для всех дат
    dates_arr = []

    if freq_type == 'days':
        freq_type = 'D'
    elif freq_type == 'months':
        freq_type = 'MS'
    elif freq_type == 'years':
        freq_type = 'AS-MAR'

    ds = datetime.datetime.strptime(date_start, "%Y-%m-%d")
    de = datetime.datetime.strptime(date_end, "%Y-%m-%d")
    # цикл для генерирования дат
    for year in range(ds.year, de.year + 1, 1):
        ffreq = freq + freq_type
        dates = pd.date_range(start=datetime.date(year=year, month=ds.month, day=ds.day),
                              end=datetime.date(year=year, month=de.month, day=de.day),
                              freq=ffreq)
        for dt in dates:
            dates_arr.append(dt.strftime("%Y-%m-%d"))
    return dates_arr


# главный модуль
if __name__ == "__main__":
    os.chdir(r'd:\EcoBaikal\model')
    params = read_params('baikal_x+10.txt')
    # dates = []
    # for y in range(int(params['year_start']), int(params['year_end']) + 1):
    #     dates.append(datelist(str(y) + '-05-01', str(y) + '-10-31', 'D', '1'))
    # dates = [day for days in dates for day in days]
    # print(dates)
    # print(params['year_start'], params['year_end'])
    # ecocycle(dates, 10, params)
    ecocycle(['2025-05-22'], 10, params)
