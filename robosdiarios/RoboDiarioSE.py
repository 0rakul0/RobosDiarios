# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.StringUtil import remove_acentos, remove_varios_espacos, remove_quebras_linha_de_linha
from util.ConfigManager import ConfigManager
from util.DateUtil import parse_mes_para_num
from bs4 import BeautifulSoup as bs
import requests


class RoboDiarioSE(RoboDiarioBase):

    def __init__(self):
        self.url = "http://www.diario.tjse.jus.br/diario/internet/pesquisar.wsp"
        self.url_download = "http://www.diario.tjse.jus.br/diario/diarios/{edicao}.pdf"
        super(RoboDiarioSE, self).__init__("DJSE", "log_robo_se.txt", "erro_robo_se.txt")

    def atualiza_acervo(self):
        atual = datetime.now ().date ()

        # data = self.data_inicial('DJSE')
        data = date(2008, 1, 1)
        s = requests.Session ()
        conseguiu = False

        while atual >= data and conseguiu is False:
            pags = ['1', '21']

            dict_edicoes_datas = {}

            data_fim = data + timedelta (days=+60)
            while data_fim > atual:
                data_fim -= timedelta (days=1)

            for pag in pags:

                params = {'tmp.diario.dt_inicio': data.strftime('%d/%m/%Y'),
                          'tmp.diario.dt_fim': data_fim.strftime('%d/%m/%Y'),
                          'grid.lista_diarios.next': pag}

                html_post = s.post (self.url, params=params)
                self.escreve_log ('Acessando a página {}: {} para a data {} até {}'.format ('1' if pag == '1' else '2', self.url, data.strftime('%d/%m/%Y'),data_fim.strftime('%d/%m/%Y')))
                soup = bs (html_post.text, 'html5lib')
                tabela = soup.find ('table', {'class': 'grid'})
                itens_tabela = tabela.find_all ('td', {'class', 'grid_center'})

                dict_edicoes_datas = self.encontra_edicoes (itens_tabela, dict_edicoes_datas)

            self.baixa_diarios (dict_edicoes_datas)
            data = data_fim
            if data_fim == atual:
                conseguiu = True
            # data += relativedelta (months=+1)


    def download_atualizacao_diaria(self):
        atual = datetime.now ().date ()

        data = self.data_inicial('DJSE')
        # data = date (2020, 7, 28)
        s = requests.Session ()
        conseguiu = False

        while atual >= data and conseguiu is False:

            dict_edicoes_datas = {}

            data_fim = data

            data = data.replace(day=1)

            while data_fim > atual:
                data_fim -= timedelta(days=1)

            params = {'tmp.diario.dt_inicio': data.strftime('%d/%m/%Y'),
                      'tmp.diario.dt_fim': data_fim.strftime('%d/%m/%Y'),
                      'grid.lista_diarios.next': '1'}

            html_post = s.post (self.url, params=params)
            self.escreve_log('Acessando a página {}: {} para a data {} até {}'.format(1, self.url, data.strftime('%d/%m/%Y'), data_fim.strftime('%d/%m/%Y')))
            soup = bs (html_post.text, 'html5lib')
            tabela = soup.find ('table', {'class': 'grid'})
            itens_tabela = tabela.find_all ('td', {'class', 'grid_center'})

            dict_edicoes_datas = self.encontra_edicoes (itens_tabela, dict_edicoes_datas)

            self.baixa_diarios (dict_edicoes_datas)

            if data_fim == atual:
                conseguiu = True


    def baixa_diarios(self, dict_edicoes_datas):

        for edicao, data in dict_edicoes_datas.items():
            name = 'DJSE_{}.pdf'.format(str(data).replace('-','_'))
            self.escreve_log('Baixando o diário {}'.format(name))
            self.filemanager.download (name, data=data, url=self.url_download.format(edicao=edicao))


    def encontra_edicoes(self, itens_tabela, dict_edicoes_datas):
        self.escreve_log('Coletando as edições dos diários disponíveis')
        for item in itens_tabela[1:]:
            try:
                edicao = item.find ('a').find ('b').text
                data = item.find ('a').find ('i').text.replace ('(', '').replace (')', '')
                data = self.trata_data (data)
                dict_edicoes_datas[edicao] = data
            except:
                continue

        return dict_edicoes_datas


    def trata_data(self, data):
        data = data.split('de')
        mes = parse_mes_para_num(data[1].strip())
        data_final = date(int(data[2]),mes,int(data[0]))
        return data_final


    def data_limite(self):
        return date(2002, 3, 2)

    def escreve_log(self, txt):
        ConfigManager().escreve_log('[' + datetime.now().strftime("%Y-%m-%d %H:%M") + '] ## ' + txt, self.robo,self.log)

if __name__ == '__main__':
    robo = RoboDiarioSE()
    robo.escreve_log('########### INÍCIO ROBÔ DJSE ###########')
    robo.download_atualizacao_diaria()
    #robo.atualiza_acervo()
    robo.escreve_log('############ FIM ROBÔ DJSE #############')
