from datetime import timedelta, datetime, date
import requests
import time
import os
import json
from bs4 import BeautifulSoup as bs
from util.ConfigManager import ConfigManager
from dateutil.relativedelta import relativedelta
from util import DateUtil as d
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.StringUtil import remove_acentos, remove_varios_espacos, remove_quebras_linha_de_linha


class RoboDiarioRO(RoboDiarioBase):
    def __init__(self):
        self.url_acervo = 'https://portal.tjro.jus.br/diario-api/list.php?ano={ano}'
        super(RoboDiarioRO, self).__init__("DJRO", "log_robo_ro.txt", "erro_robo_ro.txt")


    def atualiza_acervo(self, data=None):
        s = requests.Session()
        atual = datetime.now().date()
        if not data:
            data = date(2004,1,1)

        while atual >= data:

            try:
               html = s.get(self.url_acervo.format(ano=data.year)).text
               js = json.loads(html)
               self.escreve_log('Acessando cadernos do ano {}'.format(data.year))

               for cad in js:
                   name = 'DJRO_{}_{}_{}.pdf'.format(cad['year'], cad['month'], cad['day'])
                   self.escreve_log('Baixando caderno {}'.format(name))
                   self.filemanager.download(name,date(int(cad['year']), int(cad['month']), int(cad['day'])),remove_varios_espacos(cad['url']), tentativas=10)

            except Exception as e:
                print(e)

            data += relativedelta(years=+1)


    def download_atualizacao_diaria(self):
        data = self.data_inicial ('DJRO')
        s = requests.Session ()
        atual = datetime.now ().date ()

        while atual >= data:
            data_str = str (data)
            try:
                html = s.get (self.url_acervo.format (ano=data.year)).text
                js = json.loads (html)
                self.escreve_log ('Acessando caderno do dia {}'.format (data))

                link = None
                for cad in js:
                    if cad['year'] == '0'+str(data.year) if len(str(data.year)) == 1 else str(data.year):
                        if cad['month'] == '0'+str(data.month) if len(str(data.year)) == 1 else str(data.year):
                            if cad['day'] == str(data.day):
                                link = remove_varios_espacos(cad['url'])
                                break

                if link:
                    name = 'DJRO_{}.pdf'.format (data_str.replace ('-', '_'))
                    self.escreve_log ('Baixando caderno {}'.format (name))
                    self.filemanager.download (name, data, link, tentativas=10)
                else:
                    self.escreve_log('Não houve caderno no dia {}'.format(data))

            except Exception as e:
                print (e)

            data += relativedelta (days=+1)


    def escreve_log(self, txt):
        ConfigManager ().escreve_log ('[' + datetime.now ().strftime ("%Y-%m-%d %H:%M") + '] ## ' + txt, self.robo, self.log)


    def data_limite(self):
        return date(2009,5,22)


if __name__ == '__main__':
    robo = RoboDiarioRO()
    robo.escreve_log('########### INÍCIO ROBÔ DJRO ###########')
    robo.download_atualizacao_diaria()
    #robo.atualiza_acervo(date(2020,1,1))
    robo.escreve_log('########### FIM ROBÔ DJRO ###########')



