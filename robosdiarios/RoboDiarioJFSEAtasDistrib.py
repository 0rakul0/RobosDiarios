import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
import os.path
import re


class RoboDiarioJFSEAtasDistrib(RoboDiarioBase):

    def __init__(self):

        self.url_jfse = 'https://consulta2.jfse.jus.br/ConsultaTebas/cons_ata.asp?DifMes='
        super(RoboDiarioJFSEAtasDistrib, self).__init__("TRF05", "TRF5_robodiario.txt", "TRF5_robodiario.err")

    def download_atualizacao_diaria(self):
        self.download_jfse()

    def data_limite(self):
        pass

    def data_inicial(self, filtro, tipo_arquivo="*.ata", por_tipo=True, somente_inicio_mes=False, subfolders=None):
        pass

    def escreve_log(self, txt):
        ConfigManager().escreve_log(txt, self.robo, self.log, verbose=False)


    def download_jfse(self):

        self.escreve_log('########### INICIO JFSE ###########')
        print('########### INICIO JFSE ###########')

        # Define o numero de meses que devem ser verificados pelo robo
        for numero_da_pagina in range(-171, 1, 1):

            get_pagina_inicial = requests.get(self.url_jfse + str(numero_da_pagina), verify=False)

            pagina_inicial = bs(get_pagina_inicial.text, "html5lib")

            for link in pagina_inicial.select("#ConsProc > table > tbody > tr > td > p > table > tbody > tr > td > p > a")[1:]:

                data = datetime.strptime(re.search(r"(\d{2}\/\d{2}\/\d{4})", link.text).group(1), "%d/%m/%Y")

                nome_final_do_arquivo = 'TRF05_ATADISTRIB_JFSE_' + re.sub('[^\d]', '', link.text.strip()) + '_' + data.strftime("%Y_%m_%d") + '.ata'

                full_filename = self.filemanager.caminho(nome_final_do_arquivo, data) + os.path.sep + nome_final_do_arquivo

                if not os.path.isfile(full_filename):

                    retry = 5

                    while retry > 0:
                        try:

                            download_get = requests.get(
                                "https://consulta2.jfse.jus.br/ConsultaTebas" + link.attrs["href"][1:],
                                                        verify=False)
                            if download_get.status_code == 200:
                                print("Baixando", data)

                                soup = bs(download_get.text, "html5lib")

                                with open(full_filename, 'w', encoding="latin-1") as outfile:
                                    outfile.write(soup.text)

                            retry = 0

                        except Exception:
                            retry -= 1
                            if retry == 0:
                                raise Exception
                else:
                    print("Já baixado", data)


if __name__ == '__main__':
    robo = RoboDiarioJFSEAtasDistrib()
    robo.download_atualizacao_diaria()
    print('########### FIM TRF05 ###########')