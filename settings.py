import os
class Settings:
    def __init__(self):
        #self.ROOT_DIR = "D:/"
        self.ROOT_DIR = "D:\\"
        self.ERA_TIFF_DIR = os.path.join(self.ROOT_DIR,"Data\\ERA5Land\\")
        self.ERA_BAS_DIR = os.path.join(self.ROOT_DIR,"EcoBaikal\\Data\\Meteo\\Eraland\\")
        self.GFS_TIFF_DIR = os.path.join(self.ROOT_DIR,"Data\\GFS\\")
        self.GFS_BAS_DIR = os.path.join(self.ROOT_DIR,"EcoBaikal\\Data\\Meteo\\")
        self.EMG_HYDRO_DIR = os.path.join(self.ROOT_DIR,"EcoBaikal\\Data\\Hydro\\Baikal\\")
        self.EMAIL_XLS_DIR = os.path.join(self.ROOT_DIR,"Data\\HYDRO")
        self.SHORT_CT = os.path.join(self.ROOT_DIR,"EcoBaikal\\Archive\\002\\CT\\")
        self.SHORT_RES = os.path.join(self.ROOT_DIR, "EcoBaikal\\Archive\\002\\RES\\")
        self.LONG_CT = os.path.join(self.ROOT_DIR, "EcoBaikal\\Archive\\003\\CT\\")
        self.LONG_RES = os.path.join(self.ROOT_DIR, "EcoBaikal\\Archive\\003\\ENS\\")
        self.MODEL_DIR = os.path.join(self.ROOT_DIR, "EcoBaikal\\model\\")
        self.MODEL_BAS_DIR = os.path.join(self.ROOT_DIR,'EcoBaikal\\Basin\\Baik\\Bas\\')
        self.HYDRO_FACT_DIR = os.path.join(self.ROOT_DIR, "Data\\HYDRO\\")
        self.SOURCE_NAME = "QCURVBaikal                        .txt"
        self.rivers = {'Anga': 'angara', 'Barg': 'barguzin', 'Sele': 'selenga'}
        self.emails_d = ['gonchukovlv@yandex.ru', 'gonchukov-lv@ferhri.ru', 'moreido@mail.ru'] # debug
        self.emails_p = ['gonchukovlv@yandex.ru', 'moreido@mail.ru', 'envision@enplus.ru', 
			'kalugin-andrei@mail.ru', 'karmazinenkoEI@enplus-generation.ru'		, 
			'dl@irmeteo.ru', 'voda@irmeteo.ru', 'gidro.81@mail.ru', 
				'gmo-bcgms@mail.ru'] # production
        if not os.path.isdir(self.ROOT_DIR):
            self.mkdirs()


    def mkdirs(self):
        if not os.path.isdir(self.ROOT_DIR):
            os.makedirs(self.ROOT_DIR)

        if not os.path.isdir(self.ERA_TIFF_DIR):
            os.makedirs(self.ERA_TIFF_DIR)

        if not os.path.isdir(self.ERA_BAS_DIR):
            os.makedirs(self.ERA_BAS_DIR)

        if not os.path.isdir(self.GFS_TIFF_DIR):
            os.makedirs(self.GFS_TIFF_DIR)

        if not os.path.isdir(self.GFS_BAS_DIR):
            os.makedirs(self.GFS_BAS_DIR)

        if not os.path.isdir(self.EMG_HYDRO_DIR):
            os.makedirs(self.EMG_HYDRO_DIR)

        if not os.path.isdir(self.EMAIL_XLS_DIR):
            os.makedirs(self.EMAIL_XLS_DIR)

'''
def gfsProc(today):
    wd = 'd:/Data/GFS/'
    outDir = 'd:/EcoBaikal/Data/Meteo/'
    
def eraProc():
    # all files in wd
    fromDir = 'D:/Data/ERA5Land/'
    toDir = 'D:/EcoBaikal/Data/Meteo/Eraland/'
    '''



