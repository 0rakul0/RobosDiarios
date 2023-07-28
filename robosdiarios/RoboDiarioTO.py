# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from util.StringUtil import remove_acentos, remove_varios_espacos, remove_quebras_linha_de_linha
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.DateUtil import parse_mes_para_num
from bs4 import BeautifulSoup as bs
import re
import requests


class RoboDiarioTO(RoboDiarioBase):

    def __init__(self):
        self.url = "https://wwa.tjto.jus.br/diario/pesquisa/arquivos/{ano}"
        self.url_download = "https://wwa.tjto.jus.br/diario/diariopublicado/{edicao}.pdf"
        super(RoboDiarioTO, self).__init__("DJTO", "log_robo_to.txt", "erro_robo_to.txt")

    def atualiza_acervo(self):
        atual = datetime.now ().date ()

        # data = self.data_inicial('DJTO')
        data = date(2005, 9, 1)
        s = requests.Session ()
        conseguiu = False

        while atual >= data and conseguiu is False:


            html_get = s.get(self.url.format(ano=data.year))
            self.escreve_log ('Acessando a url: {} para o ano de {}'.format(self.url.format(ano=data.year), data.year))
            soup = bs (html_get.text, 'html5lib')
            tabela = soup.find('section', {'class': 'row-fluid'})
            itens_tabela = tabela.find_all('a')

            dict_edicoes_datas = {}

            dict_edicoes_datas = self.encontra_edicoes(itens_tabela, dict_edicoes_datas)

            self.baixa_diarios(dict_edicoes_datas)

            if data.year != atual.year:
                data += relativedelta (years=1)
            else:
                conseguiu = True


    def download_atualizacao_diaria(self):
        atual = datetime.now ().date ()

        data = self.data_inicial('DJTO')
        # data = date (2005, 1, 1)
        s = requests.Session ()
        conseguiu = False

        while conseguiu is False:

            html_get = s.get (self.url.format (ano=atual.year))
            self.escreve_log ('Acessando a url: {} para o ano de {}'.format (self.url.format (ano=data.year), data.year))
            soup = bs (html_get.text, 'html5lib')
            tabela = soup.find ('section', {'class': 'row-fluid'})
            itens_tabela = tabela.find_all ('a')

            dict_edicoes_datas = {}

            dict_edicoes_datas = self.encontra_edicoes (itens_tabela, dict_edicoes_datas)

            self.baixa_diarios (dict_edicoes_datas)

            # if data.year != atual.year:
            #     data += relativedelta (years=1)
            # else:
            conseguiu = True


    def baixa_diarios(self, dict_edicoes_datas):

        for edicao, data in dict_edicoes_datas.items():
            name = 'DJTO_{}.pdf'.format(str(data).replace('-','_'))
            self.escreve_log('Baixando o diário {}'.format(name))
            self.filemanager.download(name, data=data, url=self.url_download.format(edicao=edicao))


    def encontra_edicoes(self, itens_tabela, dict_edicoes_datas):
        self.escreve_log('Coletando as edições dos diários disponíveis')
        for item in itens_tabela:
            try:
                itens = item.text.strip().split('\n')
                edicao = re.search('\d+',item.attrs['href']).group(0)
                data = itens[1].strip()
                data = self.trata_data (data)
                dict_edicoes_datas[edicao] = data
            except:
                continue

        return dict_edicoes_datas


    def trata_data(self, data):
        data = data.split('/')
        data_final = date(int(data[2]),int(data[1]),int(data[0]))
        return data_final

    def data_limite(self):
        return date(2023, 7, 20)

    def escreve_log(self, txt):
        ConfigManager().escreve_log('[' + datetime.now().strftime("%Y-%m-%d %H:%M") + '] ## ' + txt, self.robo,self.log)

if __name__ == '__main__':
    robo = RoboDiarioTO()

    robo.escreve_log('########### INÍCIO ROBÔ DJTO ###########')
    robo.download_atualizacao_diaria()
    robo.escreve_log('############ FIM ROBÔ DJTO #############')
