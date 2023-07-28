import os
import re
import requests

from bs4 import BeautifulSoup as bs
from datetime import datetime
from dateutil import relativedelta
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager

class RoboDiarioJFCEAtasDistrib(RoboDiarioBase):

    def __init__(self):

        self.url_sjce = 'https://www.jfce.jus.br'
        super(RoboDiarioJFCEAtasDistrib, self).__init__("TRF05", "TRF5_robodiario.txt", "TRF5_robodiario.err")

    def download_atualizacao_diaria(self):
        self.download_sjce()

    def data_limite(self):
        return datetime.date(2004,10,1)

    def data_inicial(self, filtro, tipo_arquivo="*.ata", por_tipo=True, somente_inicio_mes=False, subfolders=None):

        data = super(RoboDiarioJFCEAtasDistrib, self).data_inicial(filtro, tipo_arquivo,por_tipo,subfolders)

        if somente_inicio_mes:
            return data.replace(day=1)

        return data

    def escreve_log(self,txt):
        ConfigManager().escreve_log(txt,self.robo,self.log,verbose=False)

    def download_sjce(self):

        self.escreve_log('########### INICIO SJCE ###########')
        print('########### INICIO SJCE ###########')

        dataatual = datetime.date(datetime.today())
        datainicial = datetime.date(datetime(2004,10,1))
        diferenca = relativedelta.relativedelta(datainicial,dataatual)
        meses = diferenca.years*12 + diferenca.months

        for mes in range(0, meses-1, -1):
            url_sjce_meses = self.url_sjce + '/component/distribuicao/?view=distribuicao&diferenca={}'.format(str(mes))
            primeira_pagina = requests.get(url_sjce_meses)
            soup_primeira_pagina = bs(primeira_pagina.text, 'html5lib')
            atas = soup_primeira_pagina.select('html body div#Container div.main div#component-content '
                                               'div.row div div.artigo div#content div#page div.container '
                                               'ul.list-group li.list-group-item')
            if len(atas[0].select('a')) == 0:
                atas = []

            for ata in atas:
                data_da_ata = datetime.strptime(re.findall(r'\d{2}/\d{2}/\d{4}', ata.text)[1], '%d/%m/%Y')
                hora_da_ata = datetime.strptime(re.findall(r'\d{2}:\d{2}', ata.text)[1], '%H:%M')
                nome_final_do_arquivo = r'TRF05_ATADISTRIB_JFCE_' + re.sub('[^\d]', '', ata.text.strip()) + '_' \
                                        + data_da_ata.strftime("%Y_%m_%d") + '.ata'
                full_filename = self.filemanager.caminho(nome_final_do_arquivo, data_da_ata) + \
                                os.path.sep + nome_final_do_arquivo
                if not os.path.isfile(full_filename):
                    try:
                       retry = 5
                       while True:
                            url_sjce_ata = self.url_sjce + ata.select('a')[0]['href']
                            ata_pagina = requests.get(url_sjce_ata)
                            soup_ata_pagina = bs(ata_pagina.text, 'html5lib')
                            if ata_pagina.status_code == 200:
                                with open(full_filename, 'w', encoding='utf8') as outfile:
                                    outfile.write(soup_ata_pagina.text)
                                    print('Baixou o arquivo: ' + nome_final_do_arquivo)
                                    self.escreve_log('Baixou o arquivo: ' + nome_final_do_arquivo)
                                break

                            else:
                                retry -= 1
                                if retry == 0:
                                    raise Exception

                    except Exception:
                        print('Problemas ao baixar o arquivo: ' + nome_final_do_arquivo)
                        self.escreve_log('Problemas ao baixar o arquivo: ' + nome_final_do_arquivo)

if __name__ == '__main__':

    robo = RoboDiarioJFCEAtasDistrib()
    robo.download_atualizacao_diaria()
    print('########### FIM SJCE ###########')
    robo.escreve_log('########### FIM SJCE ###########')
