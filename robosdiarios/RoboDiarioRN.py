from datetime import timedelta, datetime, date
import requests
import time
from bs4 import BeautifulSoup as bs
from util.ConfigManager import ConfigManager
from dateutil.relativedelta import relativedelta
from util import DateUtil as d
from robosdiarios.RoboDiarioBase import RoboDiarioBase


class RoboDiarioRN(RoboDiarioBase):
    def __init__(self):

        self.url_inicial = 'https://diario.tjrn.jus.br/djonline/inicial.jsf'
        self.url_goto = 'https://diario.tjrn.jus.br/djonline/goto.jsf'
        self.url_jud = 'https://diario.tjrn.jus.br/djonline/pages/repositoriopdfs/{ano}/{trimestre}tri/{data}/{data}_JUD.pdf' # trimestre ex: 3, 2... / data ex: 20200713
        self.url_adm = 'https://diario.tjrn.jus.br/djonline/pages/repositoriopdfs/{ano}/{trimestre}tri/{data}/{data}_ADM.pdf'
        super(RoboDiarioRN, self).__init__("DJRN", "log_robo_rn.txt", "erro_robo_rn.txt")


    def atualiza_acervo(self, data_inicial=None):
        s = requests.Session()
        headers_inicial = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                            'Accept-Encoding':'gzip, deflate, br',
                            'Accept-Language':'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                            'Connection':'keep-alive',
                            'Host':'diario.tjrn.jus.br',
                            'Sec-Fetch-Dest':'document',
                            'Sec-Fetch-Mode':'navigate',
                            'Sec-Fetch-Site':'none',
                            'Sec-Fetch-User':'?1',
                            'Upgrade-Insecure-Requests':'1',
                            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

        html = s.get(self.url_inicial, headers=headers_inicial, verify=False)

        try:
            jsessionid = html.request.headers._store['cookie'][1]
        except:
            jsessionid = 'JSESSIONID='+html.cookies._cookies['diario.tjrn.jus.br']['/djonline']['JSESSIONID'].value


        for caderno in [self.url_jud,self.url_adm]:

            if data_inicial is None:
                data_inicial = date (2007, 10, 30) # data do primeiro caderno no acervo do site

            data_atual = datetime.now ().date ()

            while data_atual >= data_inicial:

                if int(data_inicial.month) in [1,2,3]:
                    trimestre = 1
                elif int(data_inicial.month) in [4,5,6]:
                    trimestre = 2
                elif int(data_inicial.month) in [7,8,9]:
                    trimestre = 3
                else:
                    trimestre = 4

                ano = data_inicial.year

                data = str(data_inicial).replace('-','')

                headers_caderno = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                                    'Accept-Encoding':'gzip, deflate, br',
                                    'Accept-Language':'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                                    'Cache-Control':'max-age=0',
                                    'Connection':'keep-alive',
                                    'Cookie':jsessionid,
                                    'Host':'diario.tjrn.jus.br',
                                    'If-Modified-Since':'Mon, 06 Jul 2020 22:38:58 GMT',
                                    'If-None-Match':'W/"4131139-1594075138129"',
                                    'Sec-Fetch-Dest':'document',
                                    'Sec-Fetch-Mode':'navigate',
                                    'Sec-Fetch-Site':'none',
                                    'Sec-Fetch-User':'?1',
                                    'Upgrade-Insecure-Requests':'1',
                                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

                html_cad = s.get (caderno.format (ano=ano, trimestre=trimestre, data=data), headers=headers_caderno, verify=False)

                if html_cad.status_code != 200:
                    self.escreve_log ('Não houve caderno {} no dia {}'.format ('Judicial' if 'JUD' in caderno else 'Administrativo',data_inicial))
                    data_inicial += relativedelta (days=+1)
                    continue

                name = 'DJRN_{}_{}.pdf'.format('JUD' if 'JUD' in caderno else 'ADM', data_inicial.strftime ('%Y_%m_%d'))

                self.escreve_log('Baixando o diário {}'.format (name))
                self.filemanager.download(name=name, data=data_inicial, url=caderno.format(ano=ano,trimestre=trimestre,data=data), headers=headers_caderno, session=s)
                data_inicial += relativedelta(days=+1)

    def download_atualizacao_diaria(self):
        data_inicial = self.data_inicial ('DJRN')
        self.atualiza_acervo(data_inicial)

    def escreve_log(self, txt):
        ConfigManager ().escreve_log ('[' + datetime.now ().strftime ("%Y-%m-%d %H:%M") + '] ## ' + txt, self.robo, self.log)

    def data_limite(self):
        return date(2023, 7, 20)


if __name__ == '__main__':
    robo = RoboDiarioRN()
    robo.escreve_log('########### INÍCIO ROBÔ DJRN ###########')
    robo.download_atualizacao_diaria()
    # robo.atualiza_acervo()
    robo.escreve_log('########### FIM ROBÔ DJRN ###########')



