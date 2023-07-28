import os
import re
import requests

from bs4 import BeautifulSoup as bs
from datetime import datetime
from dateutil import relativedelta
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager

class RoboDiarioJFALAtasDistrib(RoboDiarioBase):

    def __init__(self):

        self.url_sjal = 'http://www.jfal.jus.br/servicos/processos/fisicos/atas-de-distribuicao'
        super(RoboDiarioJFALAtasDistrib, self).__init__("TRF05","TRF5_robodiario.txt", "TRF5_robodiario.err")

    def download_atualizacao_diaria(self):
        self.download_sjal()

    def data_limite(self):
        return datetime.date(2004,5,1)

    def data_inicial(self, filtro, tipo_arquivo="*.ata", por_tipo=True, somente_inicio_mes=False, subfolders=None):

        data = super(RoboDiarioJFALAtasDistrib, self).data_inicial(filtro, tipo_arquivo,por_tipo,subfolders)

        if somente_inicio_mes:
            return data.replace(day=1)

        return data

    def escreve_log(self,txt):
        ConfigManager().escreve_log(txt,self.robo,self.log,verbose=False)

    def download_sjal(self):

        self.escreve_log('########### INICIO SJAL ###########')
        print('########### INICIO SJAL ###########')

        primeira_pagina = requests.post(self.url_sjal)

        dataatual = datetime.date(datetime.today())
        datainicial = datetime.date(datetime(2004,5,1))
        diferenca = relativedelta.relativedelta(datainicial,dataatual)
        meses = diferenca.years*12 + diferenca.months

        # As páginas são navegadas relativamente ao mês que estamos, logo o valor negativo na string

        for mes in range(-1,meses-1,-1):

            url_sjal_dif = 'http://tebas.jfal.jus.br/consulta/cons_ata.asp?DifMes={}'.format(str(mes))

            segunda_pagina = requests.get(url_sjal_dif)
            soup_segunda_pagina = bs(segunda_pagina.text, 'html5lib')
            atas = soup_segunda_pagina.select('html body form#ConsProc table tbody tr td p table tbody tr td p a')

            if atas is None:
                atas = 0

            for ata in range(1,len(atas)):

                url_sjal_ata = 'http://tebas.jfal.jus.br/consulta/' + re.sub(r'^\./',r'', atas[ata]['href'])

                data_da_ata = datetime.strptime(re.findall(r'\d{2}/\d{2}/\d{4}', atas[ata].text)[1], '%d/%m/%Y')

                nome_final_do_arquivo = r'TRF05_ATADISTRIB_JFAL_'+ re.sub('[^\d]', '', atas[ata].text.strip()) + \
                                        '_' + data_da_ata.strftime("%Y_%m_%d") + '.ata'

                full_filename = self.filemanager.caminho(nome_final_do_arquivo, data_da_ata) + \
                                os.path.sep + nome_final_do_arquivo

                if not os.path.isfile(full_filename):

                    try:

                        retry = 5

                        while True:

                            ata_pagina = requests.get(url_sjal_ata)
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

    robo = RoboDiarioJFALAtasDistrib()
    robo.download_atualizacao_diaria()
    print('########### FIM SJAL ###########')
    robo.escreve_log('########### FIM SJAL ###########')