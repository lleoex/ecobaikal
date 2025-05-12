import argparse
import datetime
import os

import oper_tools
from ecobaikal_longterm import ecocycle as ec_lt
from ecobaikal_shortterm import read_params, ecocycle as ec_st

from settings import Settings
from sender import sendmail

sets = Settings()

if __name__ == '__main__':
    # today =  datetime.date.today()

    parser = argparse.ArgumentParser(description='downloader',)
    parser.add_argument('--date_today', type=str, help='Дата начала расчета гггг-мм-дд', required=True)
    #parser.add_argument('--source', choices=['Q', 'GFS', 'ERA'], required=True)

    args, unknown = parser.parse_known_args()


    today = datetime.datetime.strptime(args.date_today, '%Y-%m-%d').date()
    #today = datetime.date(2025, 4, 17)
    print(today)

    os.chdir(sets.MODEL_DIR)
    params = read_params(os.path.join(sets.MODEL_DIR, 'baikal_x+10.txt'))
    for k in params:
        params[k] = params[k].replace("d:", sets.ROOT_DIR)
    ec_st([today], 10, params)

    oper_tools.graphShort(os.path.join(sets.SHORT_RES, (today + datetime.timedelta(days=10)).strftime('%Y%m%d'), sets.SOURCE_NAME))
    files_to_send = []
    fname = os.path.join(sets.SHORT_RES, f'{(today+datetime.timedelta(days=10)).strftime("%Y%m%d")}/x+10.png')
    files_to_send.append(fname)
    fname = os.path.join(sets.SHORT_RES, f'{(today + datetime.timedelta(days=10)).strftime("%Y%m%d")}/x+10.xlsx')
    files_to_send.append(fname)

    # sendmail(f'Прогноз от {today.strftime("%Y-%m-%d")}', f'Прогноз от {today.strftime("%Y-%m-%d")}', [fname])

    if today.day == 1 or today.day == 10:

        # долгосрочный прогноз
        params = read_params(os.path.join(sets.ROOT_DIR, sets.MODEL_DIR, 'baikal_x+60.txt'))
        for k in params:
            params[k] = params[k].replace("d:", sets.ROOT_DIR)
        ec_lt([today + datetime.timedelta(days=10)], 2, params)

        # обработка ансамбля для статистики и картинок
        ens = sets.LONG_RES + '/' + str(datetime.date(today.year, today.month + 2, 1).strftime('%Y%m%d')) + '/' + \
              str(datetime.date(today.year, today.month + 2, 1).strftime('%Y%m%d')) + '_ens.txt'
        oper_tools.ens_stat(ens)

        # добавление файла для отправки
        lfname = sets.LONG_RES + '/' + str(datetime.date(today.year, today.month + 2, 1).strftime('%Y%m%d')) + '/' + \
                 'graph_' + today.strftime('%Y-%m-%d') + '.png'
        files_to_send.append(lfname)

        # отправка почты
        sendmail(f'Прогноз от {today.strftime("%Y-%m-%d")}', f'Прогноз от {today.strftime("%Y-%m-%d")}', files_to_send)