# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from util.StringUtil import remove_acentos, remove_varios_espacos, remove_quebras_linha_de_linha
from dateutil.relativedelta import relativedelta
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.DateUtil import parse_mes_para_num
from bs4 import BeautifulSoup as bs
import re
import requests


class RoboDiarioGO(RoboDiarioBase):

    def __init__(self):
        self.url_base = 'http://tjdocs.tjgo.jus.br'
        self.url = "http://tjdocs.tjgo.jus.br/pastas/333"
        self.url_download = "http://tjdocs.tjgo.jus.br{edicao}/download"
        super(RoboDiarioGO, self).__init__("DJGO", "log_robo_go.txt", "erro_robo_go.txt")

    def atualiza_acervo(self):
        s = requests.Session()

        html = s.get(self.url)
        soup_anos = bs(html.text, 'html5lib')


        dict_anos_links = self.get_anos(soup_anos)

        for ano, link_ano in dict_anos_links.items():
            html_ano = s.get(link_ano)
            soup_meses = bs(html_ano.text, 'html5lib')
            dict_meses_link = self.get_meses(soup_meses)

            for mes, link_mes in dict_meses_link.items():
                html_mes = s.get(link_mes)
                soup_paginas = bs(html_mes.text, 'html5lib')
                try:
                    qtd_pags = soup_paginas.find('ul',{'class':'pagination'}).find_all('li')[1:-1]
                except AttributeError as e:
                    qtd_pags = [1]
                    self.get_cadernos(qtd_pags, s, link_mes)
                    continue

                self.get_cadernos(qtd_pags,s,link_mes)


    def get_cadernos(self,qtd_pags,s,link_mes):

        for pags in range (1, len (qtd_pags) + 1):
            html_pags = s.get (link_mes + '?page={}'.format (pags))
            soup_cadernos = bs (html_pags.text, 'html5lib')
            cadernos = soup_cadernos.find_all ('span', {'id': 'nome-arquivo'})
            for caderno in cadernos:
                cad = caderno.find ('a')
                if 'pastas' in cad.attrs['href']:
                    continue

                self.download_cadernos(cad)


    def download_cadernos(self,cad):

        edicao_caderno = cad.text.split ('_')[2]
        cad_link_download = self.url_download.format (edicao=cad.attrs['href'])
        procura_data = [data for data in cad.text.split ('_') if re.search('\d{8}',data)][0].replace ('.pdf', '')
        # cad_data_lista = list(cad.text.split ('_')[-1].replace ('.pdf', ''))
        dia = int (''.join (procura_data[0:2]))
        mes = int (''.join (procura_data[2:4]))
        ano = int (''.join (procura_data[4:]))
        data_caderno = date (ano, mes, dia)
        name = 'DJGO_CADERNO_{}_{}.pdf'.format (edicao_caderno, data_caderno.strftime ('%Y_%m_%d'))
        self.escreve_log ('Baixando o diário {}'.format (name))
        self.filemanager.download (name, data=data_caderno, url=cad_link_download)


    def get_anos(self, soup):
        anos = soup.find_all ('tbody')[1].find_all ('tr')

        dict_ano_link = {}

        for ano in anos:
            dict_ano_link[ano.find_all ('a')[-1].text] = self.url_base + ano.find_all ('a')[-1].attrs['href']

        return dict_ano_link


    def get_meses(self, soup):
        meses = soup.find_all ('tbody')[1].find_all ('tr')

        dict_mes_link = {}

        for mes in meses:
            dict_mes_link[mes.find_all ('a')[-1].text.split('-')[0].strip()] = self.url_base + mes.find_all ('a')[-1].attrs['href']

        return dict_mes_link


    def download_atualizacao_diaria(self):
        atual = datetime.now ().date ()

        data = self.data_inicial('DJGO')
        # data = date(2020,9,1)

        s = requests.Session ()

        while data <= atual:

            html = s.get (self.url)

            soup_anos = bs (html.text, 'html5lib')

            dict_anos_links = self.get_anos (soup_anos)

            link_ano = dict_anos_links[str(data.year)]

            html_ano = s.get(link_ano)
            soup_meses = bs(html_ano.text, 'html5lib')
            dict_meses_links = self.get_meses (soup_meses)

            link_mes = dict_meses_links[str(data.month) if len(str(data.month)) == 2 else '0'+str(data.month)]

            html_mes = s.get (link_mes)
            soup_paginas = bs (html_mes.text, 'html5lib')
            qtd_pags = soup_paginas.find ('ul', {'class': 'pagination'}).find_all ('li')[1:-1]
            self.get_cadernos (qtd_pags, s, link_mes)

            data += relativedelta(months=+1)



    def data_limite(self):
        return date(2002, 3, 2)

    def escreve_log(self, txt):
        ConfigManager().escreve_log('[' + datetime.now().strftime("%Y-%m-%d %H:%M") + '] ## ' + txt, self.robo,self.log)

if __name__ == '__main__':
    robo = RoboDiarioGO()

    robo.escreve_log('########### INÍCIO ROBÔ DJGO ###########')
    robo.atualiza_acervo()
    #robo.download_atualizacao_diaria()
    robo.escreve_log('############ FIM ROBÔ DJGO #############')
