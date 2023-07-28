# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from util.StringUtil import remove_acentos, remove_varios_espacos, remove_quebras_linha_de_linha
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel
from bs4 import BeautifulSoup
import requests
import re

class RoboDiarioMA(RoboDiarioBase):

    def __init__(self):
        self.url = 'http://www.tjma.jus.br/portal/diario/{pagina}?data_inicial={data_inicio}&data_final={data_fim}'
        super(RoboDiarioMA, self).__init__("DJMA", "log_robo_ma.txt", "erro_robo_ma.txt")

    def atualiza_acervo(self):
        atual = datetime.now ().date ()

        # data = self.data_inicial('DJMA')
        data = date (2001, 1, 1)
        # data = date (2020, 7, 29)
        s = requests.Session ()
        conseguiu = False

        while atual >= data and not conseguiu:

            self.escreve_log ('Acessando url: {}'.format (self.url.format (pagina=1, data_inicio=data.strftime ('%d/%m/%Y'), data_fim=atual.strftime ('%d/%m/%Y'))))
            html = s.get(self.url.format(pagina=1, data_inicio=data.strftime('%d/%m/%Y'), data_fim=atual.strftime('%d/%m/%Y')))
            soup = BeautifulSoup(html.text, 'html5lib')
            diarios = soup.find('ul',{'class','general-list search-result download'}).find_all('li')

            qtd_pags = round(int(soup.find('ul',{'class','pagination'}).find_all('strong')[-1].text)/10)

            for pag in range(1,qtd_pags):
                if pag is not 1:
                    self.escreve_log('Acessando url: {}'.format(self.url.format(pagina=pag, data_inicio=data.strftime ('%d/%m/%Y'), data_fim=atual.strftime ('%d/%m/%Y'))))
                    html = s.get(self.url.format (pagina=pag, data_inicio=data.strftime ('%d/%m/%Y'), data_fim=atual.strftime ('%d/%m/%Y')))
                    soup = BeautifulSoup (html.text, 'html5lib')
                    diarios = soup.find ('ul', {'class', 'general-list search-result download'}).find_all ('li')

                for diario in diarios:
                    data_caderno = diario.find('span').text.split()[0].split('/')
                    data_caderno = date(int(data_caderno[2]), int(data_caderno[1]), int(data_caderno[0]))
                    link_caderno = diario.find_all('a')[0].attrs['href']
                    name = 'DJMA_{}.pdf'.format(str(data_caderno).replace('-', '_'))
                    self.escreve_log('Baixando o diário {}'.format (name))
                    self.filemanager.download(name, data=data_caderno, url=link_caderno)

            conseguiu = True



    def download_atualizacao_diaria(self):
        atual = datetime.now ().date ()
        data = self.data_inicial('DJMA')
        s = requests.Session ()
        conseguiu = False

        while atual >= data and not conseguiu:
            self.escreve_log ('Acessando url: {}'.format (self.url.format (pagina=1, data_inicio=data.strftime ('%d/%m/%Y'), data_fim=atual.strftime ('%d/%m/%Y'))))
            html = s.get (self.url.format (pagina=1, data_inicio=data.strftime ('%d/%m/%Y'), data_fim=atual.strftime ('%d/%m/%Y')))
            soup = BeautifulSoup (html.text, 'html5lib')
            diarios = soup.find ('ul', {'class', 'general-list search-result download'}).find_all ('li')

            if diarios[0].text.strip() == 'Nenhuma informação encontrada!':
                self.escreve_log('Não existem diários no dia {}'.format(atual.strftime('%d/%m/%Y')))
                conseguiu = True
                break

            for diario in diarios:
                data_caderno = diario.find ('span').text.split ()[0].split ('/')
                data_caderno = date (int (data_caderno[2]), int (data_caderno[1]), int (data_caderno[0]))
                link_caderno = diario.find_all ('a')[0].attrs['href']
                name = 'DJMA_{}.pdf'.format (str (data_caderno).replace ('-', '_'))
                self.escreve_log ('Baixando o diário {}'.format (name))
                self.filemanager.download (name, data=data_caderno, url=link_caderno)

            conseguiu = True


    def data_limite(self):
        return date(2002, 3, 2)

    def escreve_log(self, txt):
        ConfigManager().escreve_log('[' + datetime.now().strftime("%Y-%m-%d %H:%M") + '] ## ' + txt, self.robo,self.log)

if __name__ == '__main__':
    robo = RoboDiarioMA()
    robo.escreve_log('########### INÍCIO ROBÔ DJMA ###########')
    # robo.atualiza_acervo()
    robo.download_atualizacao_diaria()
    robo.escreve_log('############ FIM ROBÔ DJMA #############')

