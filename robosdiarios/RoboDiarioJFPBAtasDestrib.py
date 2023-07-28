from bs4 import BeautifulSoup
import os.path
from datetime import datetime, timedelta
from util.FileManager import *
from robosdiarios.RoboDiarioBase import RoboDiarioBase

import os
import re
import requests

from bs4 import BeautifulSoup as bs
from datetime import datetime
from dateutil import relativedelta

from util.ConfigManager import ConfigManager

class RoboDiarioJFPBAtasDestrib(RoboDiarioBase):
    def __init__(self):
        self.__url = 'http://web.jfpb.jus.br/consproc/cons_ata.asp?DifMes={MES}'
        self.__urlata = 'http://web.jfpb.jus.br/consproc/{LISTA_ATA}'

        super(RoboDiarioJFPBAtasDestrib, self).__init__("TRF05", "TRF5_robodiario.txt", "TRF5_robodiario.txt")


    def download_atualizacao_diaria(self):
        #mes = -174
        #mes 174 limite na url
        #testtime = 1 #120000
        for numero_da_pagina in range(-160, 1, 1):
            retrySite = 5
            while retrySite > 0 :
                try:
                    busca_ata= requests.session().get(self.__url.format(MES=str(numero_da_pagina)),timeout = 120000 )
                    soup = BeautifulSoup(busca_ata.text, 'html.parser')
                    a = soup.select('a')
                    link_href = [linha_ata for linha_ata in a if './lista_ata' in str(linha_ata)]
                    print(self.__url.format(MES=str(numero_da_pagina)))
                    for link in link_href:
                        retryAta = 5
                        while retryAta > 0 :
                            try:
                                lista_ata = link.attrs['href'].replace("./","")
                                acessa_ata = requests.session().get(self.__urlata.format(LISTA_ATA = lista_ata), timeout = 60000)
                                soup_ata = BeautifulSoup(acessa_ata.text, 'html.parser')
                                data = datetime.strptime(re.search(r"(\d{2}\/\d{2}\/\d{4})", link.string).group(1), "%d/%m/%Y")
                                #nome = re.search('.*\)',str(link.string).strip())
                                #urlata = self.__urlata.format(LISTA_ATA = lista_ata)
                                nome_final_do_arquivo = 'TRF05_ATADISTRIB_JFSE_' + re.sub('[^\d]', '',link.text.strip()) + '_' + data.strftime("%Y_%m_%d") + '.ata'
                                full_filename = self.filemanager.caminho(nome_final_do_arquivo,data) + os.path.sep + nome_final_do_arquivo
                                if not os.path.isfile(full_filename):
                                    with open(full_filename, 'w', encoding="latin-1") as outfile:
                                        outfile.write(soup_ata.text)
                                    print('Baixando', data)
                                else:
                                    print("Já baixado", data)
                                retryAta = 0
                            except Exception as e:
                                time.sleep(300)
                                retryAta -= 1
                                if retryAta == 0:
                                    ConfigManager().escreve_log("Erro: {e}".format(e=str(e)), self.robo, self.erro)
                    retrySite = 0
                except Exception as e:
                    time.sleep(300)
                    retrySite -= 1
                    if retrySite == 0:
                        ConfigManager().escreve_log("Erro: {e}".format(e=str(e)), self.robo, self.erro)


    def data_limite(self):
        return datetime.date(2004, 1, 2)

if __name__ == '__main__':
    roboJFPB = RoboDiarioJFPBAtasDestrib()
    roboJFPB.download_atualizacao_diaria()