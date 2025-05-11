# coding=utf-8
import time
import datetime
import matplotlib.pyplot as plt
import os
import subprocess
import pandas as pd
import numpy as np
import argparse
from settings import Settings
sets = Settings()

# однократный запуск ECOMAG diagnosis
def ecoens(date_start, date_end, year_ens_start, year_ens_end, meteo_path, hydro_path, baspath, exepath, exename,
           source_name, ens_flag, dir_CT, dir_out):
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
    :param source_name: имя расчетного файла ECOMAG, например 'QCURVMalinovka                     .txt'
    :type source_name: str
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

    # меняем значения в kpoint.bas в зависимости от варианта расчета: "0" если ансамбль, "2" если диагноз
    with open(baspath + '\kpoint.bas', 'w') as kpt:
        kpt.truncate()
        if ens_flag == 'diagnosis':
            kpt.write('2 1 1')
        elif ens_flag == 'ensemble':
            kpt.write('0 1 1')
        kpt.close()

    # меняем значения в basin.bas в зависимости от типа прогноза: 4 створа если краткосрочный, 1 если долгосрочный
    with open(baspath + '/basin.bas', 'w') as bas:
        bas.truncate()
        bas.write('1 \n 4 3 2 1')
        bas.close()

    # читаем из pathen.bas старые настройки и меняем их по очереди
    with open(exepath + '\pathen.bas', 'r+') as pathen:
        lines = pathen.read().splitlines()
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
        pathen.close()

    ens = pd.DataFrame()
    ens['date'] = pd.date_range(date_start, date_end)
    # print(ens['date'])
    ens_years = int(year_ens_end) - int(year_ens_start)
    for k, i in enumerate(range(int(year_ens_start), int(year_ens_end) + 1, 1)):
        ens_start = datetime.datetime(year=i, month=date_start.month, day=date_start.day)
        ens_end = datetime.datetime(year=i, month=date_end.month, day=date_end.day)
        print(ens_start.strftime("%d.%m.%Y") + " " + ens_end.strftime("%d.%m.%Y") + '\n')

        # пишем в atime.bas новые даты, дни года и продолжительность расчета
        atime = open(baspath + '\\' + 'atime.bas', 'w')
        atime.truncate()
        atime.write(ens_start.strftime("%d.%m.%Y") + " " + ens_end.strftime("%d.%m.%Y") + '\n')
        atime.write(str(ens_start.timetuple().tm_yday) + " " + str(abs(ens_end - ens_start).days))
        atime.close()
        # запускаем расчет
        os.chdir(exepath)
        # with subprocess.Popen(exepath + exename, shell=True, ) as result:
        #     print(result)
        with subprocess.Popen(exepath + '\\' + exename, shell=True, stderr=subprocess.PIPE) as result:
            _, err = result.communicate()
            if err:
                print(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + err.decode("utf-8"))
                # app_log.error(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + err.decode("utf-8"))

            print(result)

        os.chdir(dir_out + '\\' + date_end.strftime("%Y%m%d"))
        f = pd.read_csv(source_name, skiprows=1, sep=r"\s+", names=['date', 'fact', str(i)], header=None)
        # f = pd.read_csv('GidrEd.txt', skiprows=1, sep=r"\s+", header=None, names=['date', 'gorb', 'chebo'])
        if k == 0:
            ens['fact'] = f['fact']
        ens[i] = f[str(i)]
        # print(ens.head())

    # ens['Qmean'] = ens.iloc[:, ens.columns != 'fact'].mean(axis=1)
    ens['Qmean'] = ens.loc[:, ens.columns != 'date'].mean(axis=1)
    # ens = ens.sort_index(axis=1)
    # print(ens)
    ens.to_csv(dir_out + '\\' + date_end.strftime("%Y%m%d") + '\\' + date_end.strftime("%Y%m%d") + '_ens.txt')

    # pic = ens.plot(legend=False, x='date', figsize=(5, 5), sort_columns=True)
    # pic.lines[date_start.year - ens_start.year + 1].set_linewidth(2)
    # pic.lines[date_start.year - ens_start.year + 1].set_color('blue')
    # pic.lines[date_start.year - ens_start.year + 1].set_zorder(100)
    # pic.lines[-1].set_linewidth(3)
    # pic.lines[-1].set_color('red')
    # pic.lines[-1].set_zorder(120)
    # pic.set_title(str(date_start.year))
    # plt.savefig(dir_out + '\\' + date_end.strftime("%Y%m%d") + '\\' + date_end.strftime("%Y%m%d") + '_ens.png')
    # plt.close()


# REV-ESP для ECOMAG
def eco_revesp(date_start, date_end, year_ens_start, year_ens_end, meteo_path, baspath, exepath, exename, source_name,
               ens_flag, dir_CT, dir_out):
    """
    Запуск расчета по модели ECOMAG с изменяемыми контрольными точками и неизменной метеорологией

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
    :param source_name: имя расчетного файла ECOMAG, например 'QCURVMalinovka                     .txt'
    :type source_name: str
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

    # меняем значения в kpoint.bas в зависимости от варианта расчета: "0" если ансамбль, "2" если диагноз
    with open(baspath + '\kpoint.bas', 'w') as kpt:
        kpt.truncate()
        if ens_flag == 'diagnosis':
            kpt.write('2 1 1')
        elif ens_flag == 'ensemble':
            kpt.write('0 1 1')
        kpt.close()

    ens = pd.DataFrame()
    ens['date'] = pd.date_range(date_start, date_end)
    # print(ens['date'])
    ens_years = int(year_ens_end) - int(year_ens_start)
    for i in range(int(year_ens_start), int(year_ens_end), 1):
        # читаем из pathen.bas старые настройки и меняем их по очереди
        with open(exepath + '\pathen.bas', 'r+') as pathen:
            lines = pathen.read().splitlines()
            # метеорология
            lines[3] = meteo_path
            # контрольная точка - каждый раз разная
            lines[6] = dir_CT + '\\' + datetime.datetime(year=i, month=date_start.month, day=date_start.day).strftime(
                "%Y%m%d")
            print(lines[6])
            # выходной каталог
            lines[5] = dir_out + '\\' + date_end.strftime("%Y%m%d")
            # print(lines[5])
            # print('init', lines)
            # перематываем файл в начало и переписываем его с новыми значениями
            pathen.seek(0)
            pathen.writelines(["%s\n" % item for item in lines])

        ens_start = datetime.datetime(year=i, month=date_start.month, day=date_start.day)
        ens_end = datetime.datetime(year=i, month=date_end.month, day=date_end.day)
        print(ens_start.strftime("%d.%m.%Y") + " " + ens_end.strftime("%d.%m.%Y") + '\n')

        # пишем в atime.bas новые даты, дни года и продолжительность расчета
        atime = open(baspath + '\\' + 'atime.bas', 'w')
        atime.truncate()
        atime.write(date_start.strftime("%d.%m.%Y") + " " + date_end.strftime("%d.%m.%Y") + '\n')
        atime.write(str(date_start.timetuple().tm_yday) + " " + str(abs(date_end - date_start).days))
        print(date_start.strftime("%d.%m.%Y") + " " + date_end.strftime("%d.%m.%Y") + '\n')
        print(str(date_start.timetuple().tm_yday) + " " + str(abs(date_end - date_start).days))
        atime.close()
        # запускаем расчет
        os.chdir(exepath)
        with subprocess.Popen(exepath + exename, shell=True, ) as result:
            print(result)

        os.chdir(dir_out + '\\' + date_end.strftime("%Y%m%d"))
        f = pd.read_csv(source_name, skiprows=1, sep=r"\s+", names=['date', 'fact', str(i)], header=None)
        # print(f)
        if i == int(year_ens_start):
            ens['fact'] = f['fact']
        ens[i] = f[str(i)]

    ens['Qmean'] = ens.mean(axis=1)
    print(ens)
    ens.to_csv(dir_out + '\\' + date_end.strftime("%Y%m%d") + '\\' + date_end.strftime("%Y%m%d") + '_ens.txt')

    # pic = ens.plot(legend=False, x='date', figsize=(5, 5))
    # pic.lines[1].set_linewidth(3)
    # pic.lines[1].set_color('blue')
    # pic.lines[-1].set_linewidth(3)
    # pic.lines[-1].set_color('red')
    # pic.set_title(str(date_start.year))
    # plt.savefig(dir_out + '\\' + date_end.strftime("%Y%m%d") + '\\' + date_end.strftime("%Y%m%d") + '_rev_ens.png')
    # plt.close()


def ecorun(date_start, date_end, meteo_path, hydro_path, baspath, exepath, exename, ens_flag, dir_CT, dir_out,
           source_name, year_ens_start, year_ens_end):
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
    # atime = open(r'd:\EcoVolga\Basin\Chebok1\Bas\atime.bas', 'w')
    # atime = open(r'd:\ecopechora\Basin\Dvina\bas\atime.bas', 'w')
    atime = open(baspath + '\\' + 'atime.bas', 'w')
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
            # app_log.error(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + err.decode("utf-8"))

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
    # цикл по всем пришедшим датам
    for date in dates:
        if (type(date) == 'str'):
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        # check_meteo(params['meteo_path'], date)
        # проверка на наличие КТ для начала расчета
        # проверка на наличие КТ для начала расчета
        fn = params['dir_CT'] + '\\' + date.strftime("%Y%m%d") + '\\' + params['source_name']
        # print(fn)
        if os.path.isfile(fn) == False:
            # расчет КТ при ее отсутствии
            print('Отсутствует контрольная точка. Выполняется расчет')
            # меняем значения в kpoint.bas в зависимости от варианта расчета: "0" если ансамбль, "2" если диагноз
            with open(params['baspath'] + '\kpoint.bas', 'w') as kpt:
                kpt.truncate()
                kpt.write('2 0 1')
                kpt.close()
            # app_log.error(datetime.datetime.now().strftime(
            #     "%d.%m.%Y %H:%M:%S") + ' Отсутствует контрольная точка. Выполняется расчет')
            if not os.path.isfile(
                    params['dir_CT'] + '\\' + datetime.date(date.year, 5, 1).strftime("%Y%m%d") + '\\' + params[
                        'source_name']):
                if not os.path.isfile(params['dir_CT'] + '\\' + datetime.date(date.year - 1, date.month, 1).strftime(
                        "%Y%m%d") + '\\' + params['source_name']):
                    model_start = datetime.date(2025, 1, 1)
                else:
                    model_start = datetime.date(date.year - 1, date.month, 1)
            else:
                model_start = datetime.date(date.year, 5, 1)
            model_end = date
            old_dir_out = params['dir_out']
            params['dir_out'] = params['dir_CT']
            print(model_start, model_end)
            # app_log.error(
            #     'Расчет контрольной точки ' + model_start.strftime("%d.%m.%Y") + " - " + model_end.strftime("%d.%m.%Y"))
            ecorun(model_start, model_end, **params)
            params['dir_out'] = old_dir_out
        # сам расчет
        print(r'Старт прогноза')

        # для метеорологических (не ансамблевых) прогнозов меняем папку с метео на нужную, сохраняя старую
        # old_meteo = params['meteo_path']
        # params['meteo_path'] = params['meteo_path'] + '\\' + date.strftime("%Y%m%d")
        # для метеорологических (не ансамблевых) прогнозов
        # ecorun(model_start, model_end, **params)
        # params['meteo_path'] = old_meteo

        model_start = date
        # конец прогноза - конец месяца, следующего за месяцем старта прогноза
        # model_end = model_start + relativedelta(**lead) # так было
        # if model_start.month < 10:
        # model_end = datetime.date(model_start.year, model_start.month + lead.get('months'), 1)
        model_end = datetime.date(date.year, date.month + lead, 1)
        # else:
        #     model_end = datetime.date(model_start.year + 1, abs(model_start.month + lead.get('months') - 12), 1)

        print(model_start, model_end)
        # app_log.error(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + ' Старт прогноза' + ", начало: " +
        #               model_start.strftime("%d.%m.%Y") + ", окончание: " + model_end.strftime("%d.%m.%Y"))
        ecoens(model_start, model_end, **params)


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
                              end=datetime.date(year=year, month=de.month, day=ds.day),
                              freq=ffreq)
        for dt in dates:
            dates_arr.append(dt.strftime("%Y-%m-%d"))
    return dates_arr




# главный модуль
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Запуск ансамблевого расчета по модели ECOMAG')
    parser.add_argument('--date_start', type=str, nargs='?', help='Дата начала расчета гггг-мм-дд', required=True)
    parser.add_argument('--date_end', type=str, nargs='?', help='Дата окончания расчета гггг-мм-дд')
    parser.add_argument('--single', action='store_true', help='Одиночный ансамблевый прогноз')
    parser.add_argument('--freq_type', type=str, help='Частота прогноза - суточный days, месячный months',
                        default='months')
    parser.add_argument('--freq', type=str, nargs='?', help='Частота прогноза - число (При days: 1 - ежедневный, '
                                                            '10 - ежедекадный, при months: 1 - ежемесячный',
                        default='1')
    parser.add_argument('--lead_type', type=str, default='months', nargs='?',
                        help='Шаг заблаговременности: days или months')
    parser.add_argument('--lead', type=int, default=1, choices=range(1, 13), nargs='?',
                        help='Величина заблаговременности')
    parser.add_argument('--params', type=str, nargs='?', required=True,
                        help='Полный путь до файла с параметрами расчета')
    parser.add_argument('--log', type=str, default='ecorun.log', help='Файл для записи лога ошибок выполнения скрипта')
    args = parser.parse_args()

    ens_params = read_params(args.params)

    # app_log = logging.getLogger('root')
    # log_handler = RotatingFileHandler(filename=args.log, mode='a', maxBytes=100*1024,
    #                                   backupCount=2, encoding=None, delay=0)
    # app_log.setLevel(logging.ERROR)
    # app_log.addHandler(log_handler)

    if args.single == False:
        # dates = datelist(args.date_start, args.date_end, args.freq_type, args.freq)
        # костыль для проверки бесшовности
        dates = ['2017-05-11', '2017-06-11', '2017-07-11', '2017-08-11', '2017-09-11', '2017-10-11',
                 '2018-05-11', '2018-06-11', '2018-07-11', '2018-08-11', '2018-09-11', '2018-10-11',
                 '2019-05-11', '2019-06-11', '2019-07-11', '2019-08-11', '2019-09-11', '2019-10-11',
                 '2020-05-11', '2020-06-11', '2020-07-11', '2020-08-11', '2020-09-11', '2020-10-11',
                 '2021-05-11', '2021-06-11', '2021-07-11', '2021-08-11', '2021-09-11', '2021-10-11',
                 '2022-05-11', '2022-06-11', '2022-07-11', '2022-08-11', '2022-09-11', '2022-10-11',
                 '2023-05-11', '2023-06-11', '2023-07-11', '2023-08-11', '2023-09-11', '2023-10-11']
    else:
        dates = [args.date_start]
    # 12.04.2025 дописать установку только одного створа для прогноза в basin.bas
    # ecocycle(dates, {args.lead_type: int(args.lead)}, ens_params)
