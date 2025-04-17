import datetime
import os

import oper_tools
from ecobaikal_longterm import ens_stat, ecocycle as ec_lt
from ecobaikal_shortterm import read_params, ecocycle as ec_st

from settings import Settings
from sender import sendmail

sets = Settings()

if __name__ == '__main__':
    # today =  datetime.date.today()
    today = datetime.date(2025, 4, 17)
    print(today)

    os.chdir(sets.MODEL_DIR)
    params = read_params(os.path.join(sets.MODEL_DIR,'baikal_x+10.txt'))
    for k in params:
        params[k] = params[k].replace("d:",sets.ROOT_DIR)
    ec_st([today], 10, params)

    oper_tools.graphShort(os.path.join(sets.SHORT_RES, (today + datetime.timedelta(days=10)).strftime('%Y%m%d'), sets.SOURCE_NAME))
    files_to_send = []
    fname = os.path.join(sets.SHORT_RES, f'{(today+datetime.timedelta(days=10)).strftime("%Y%m%d")}/x+10.png')
    files_to_send.append(fname)

    #sendmail(f'Прогноз от {today.strftime("%Y-%m-%d")}', f'Прогноз от {today.strftime("%Y-%m-%d")}', [fname])

    if today.day == 1:

        # долгосрочный прогноз
        params = read_params(os.path.join(sets.ROOT_DIR, sets.MODEL_DIR, 'baikal_x+60.txt'))
        for k in params:
            params[k] = params[k].replace("d:",sets.ROOT_DIR)
        ec_lt([today + datetime.timedelta(days=10)], 2, params)
        ens = sets.LONG_RES + '/' + str(datetime.date(today.year, today.month + 2, 1).strftime('%Y%m%d')) + '/' + \
               str(datetime.date(today.year, today.month + 2, 1).strftime('%Y%m%d')) + '_ens.txt'

        ens_stat(ens)
        #"C:\EcoBaikal\Archive\003\ENS\20250601\graph_2025-04-26.png"
        lfname = sets.LONG_RES + '/' + str(datetime.date(today.year, today.month + 2, 1).strftime('%Y%m%d')) + '/' + \
              'graph_' + (today + datetime.timedelta(days=10)).strftime('%Y-%m-%d') + '.png'
        files_to_send.append(lfname)

    sendmail(f'Прогноз от {today.strftime("%Y-%m-%d")}', f'Прогноз от {today.strftime("%Y-%m-%d")}', files_to_send)