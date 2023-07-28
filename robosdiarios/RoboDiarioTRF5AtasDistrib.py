import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
import os.path
from util.DateUtil import daterange
from  datetime import date

class RoboDiarioTRF5AtasDistrib(RoboDiarioBase):

    def __init__(self):

        self.url_trf5 = 'http://www4.trf5.jus.br/archive/atas/{ANO}/{MES}/{DATA}.html'
        super(RoboDiarioTRF5AtasDistrib, self).__init__("TRF05", "TRF5_robodiario.txt", "TRF5_robodiario.err")


    def download_atualizacao_diaria(self):
        self.download_trf5()

    def data_limite(self):
        return datetime.date(2009,1,1)

    def data_inicial(self, filtro, tipo_arquivo="*.ata", por_tipo=True,somente_inicio_mes=False, subfolders=None):

        data = super(RoboDiarioTRF5AtasDistrib, self).data_inicial(filtro, tipo_arquivo, por_tipo, subfolders)

        if somente_inicio_mes:
            return data.replace(day=1)

        return data

    def escreve_log(self, txt):
        ConfigManager ().escreve_log (txt, self.robo, self.log, verbose=False)

    def download_trf5(self):

        self.escreve_log('########### INICIO TRF05 ###########')
        print('########### INICIO TRF05 ###########')

        # start_date = self.data_inicial()
        start_date = date(2007, 8, 1)

        for data in daterange(start_date, datetime.now().date()):

            nome_final_do_arquivo = 'TRF05_ATADISTRIB_TRF5_' + data.strftime("%Y_%m_%d") + '.ata'

            full_filename = self.filemanager.caminho(nome_final_do_arquivo, data) + os.path.sep + nome_final_do_arquivo

            if not os.path.isfile(full_filename):

                url_final = self.url_trf5.format(ANO=data.strftime("%Y"), MES=data.strftime("%m"),
                                                 DATA=data.strftime("%d%m%Y"))

                retry = 5

                while retry > 0:

                    try:

                        pagina = requests.get(url_final, verify=False, timeout=300)

                        if pagina.status_code == 200:
                            print("Baixando", data, end=' ')

                            soup = bs(pagina.text, "html5lib")

                            with open(full_filename, 'w') as outfile:
                                outfile.write(soup.text)

                            print("... Baixou")

                        retry = 0

                    except Exception:
                        retry -= 1
                        if retry == 0:
                            raise Exception

            else:
                print("Já baixado", data)


if __name__ == '__main__':

    robo = RoboDiarioTRF5AtasDistrib()
    robo.download_atualizacao_diaria()
    print('########### FIM TRF05 ###########')
