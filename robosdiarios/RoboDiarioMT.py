# -*- coding: utf-8 -*-
from util.StringUtil import remove_acentos, remove_varios_espacos, remove_quebras_linha_de_linha
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.DateUtil import parse_mes_para_num
from bs4 import BeautifulSoup as bs
import requests
import json
import re


class RoboDiarioMT(RoboDiarioBase):

    def __init__(self):
        self.url_base = 'https://dje-api.tjmt.jus.br/api/diarioOficial/documentohdf/'
        # self.url = "https://dje-api.tjmt.jus.br/api/diarioOficial/edicoes?periodoDataDe={ano_inicio}-{mes_inicio:02d}-{dia_inicio:02d}T03:00:00.000Z&periodoDataAte={ano_fim}-{mes_fim:02d}-{dia_fim:02d}T03:00:00.000Z&indicePagina=0&quantidadePagina=100"
        self.url_download_todo_acervo = 'https://dje-api.tjmt.jus.br/api/diarioOficial/edicoes?periodoDataDe=2000-01-01T02:00:00.000Z&periodoDataAte={data_atual}T03:00:00.000Z&indicePagina={pagina}&quantidadePagina=100'
        self.url_download_diario = 'https://dje-api.tjmt.jus.br/api/diarioOficial/edicoes?periodoDataDe={data_atual}T02:00:00.000Z&periodoDataAte={data_atual}T03:00:00.000Z&indicePagina={pagina}&quantidadePagina=100'
        super(RoboDiarioMT, self).__init__("DJMT", "log_robo_mt.txt", "erro_robo_mt.txt")

    def atualiza_acervo(self):
        # data = datetime.now().date()
        data = date(2021,1,12)
        atual = data.strftime('%Y-%m-%d')
        s = requests.Session()

        for pag in range(0,100000):
            html = s.get(self.url_download_todo_acervo.format(pagina=pag, data_atual=atual)).text

            if re.search('\{\"items\":\[\],\"numFound\":\d*,\"start\":\d+}', html):
                self.escreve_log('Não existem mais diários a serem baixados')
                break

            soup_qtd_pags = bs(html, 'html5lib')
            cadernos = json.loads(soup_qtd_pags.text)['items']

            for caderno in cadernos:
                for cad in caderno['documentos']:
                    nome_caderno = remove_acentos(cad['nomeCaderno'].upper().replace(' ', '_'))
                    data_caderno = caderno['dataPublicacao'].split('T')[0].replace('-', '_')
                    lista_data = data_caderno.split('_')
                    data = date(int(lista_data[0]), int(lista_data[1]), int(lista_data[2]))
                    name = 'DJMT_{}_{}.pdf'.format(nome_caderno, data_caderno)
                    try:
                        url_caderno = self.url_base+cad['enderecoPublicacao']
                    except TypeError as e:
                        continue
                    self.escreve_log('Baixando o diário {}'.format (name))
                    self.filemanager.download(name, data=data, url=url_caderno)


    def download_atualizacao_diaria(self):

        data = self.data_inicial('DJMT')
        atual = datetime.now().date()
        s = requests.Session()

        while data <= atual+timedelta(days=1): # a data de busca no site retorna a data do caderno do último dia útil

            dataSemana = data.weekday()

            if dataSemana != 5 and dataSemana != 6: # final de semana

                data_atual = data.strftime ('%Y-%m-%d')
                html = s.get(self.url_download_diario.format (pagina=0, data_atual=data_atual)).text

                soup_qtd_pags = bs (html, 'html5lib')
                cadernos = json.loads (soup_qtd_pags.text)['items']

                if len(cadernos) == 0:
                    data += timedelta(days=1)
                    continue

                for caderno in cadernos:
                    for cad in caderno['documentos']:
                        nome_caderno = remove_acentos(cad['nomeCaderno'].upper().replace(' ', '_'))
                        data_caderno = caderno['dataPublicacao'].split('T')[0].replace('-', '_')
                        lista_data = data_caderno.split('_')
                        data_real_caderno = date(int(lista_data[0]), int(lista_data[1]), int(lista_data[2]))
                        name = 'DJMT_{}_{}.pdf'.format(nome_caderno, data_caderno)
                        try:
                            url_caderno = self.url_base + cad['enderecoPublicacao']
                        except TypeError as e:
                            continue
                        if endereco_caderno is None:
                            continue

                        url_caderno = self.url_base + endereco_caderno

                        self.escreve_log ('Baixando o diário {}'.format (name))
                        self.filemanager.download (name, data=data_real_caderno, url=url_caderno)

            data += timedelta(days=1)


    def data_limite(self):
        return date(2002, 3, 2)

    def escreve_log(self, txt):
        ConfigManager().escreve_log('[' + datetime.now().strftime("%Y-%m-%d %H:%M") + '] ## ' + txt, self.robo,self.log)

if __name__ == '__main__':
    robo = RoboDiarioMT()

    robo.escreve_log('########### INÍCIO ROBÔ DJMT ###########')
    #robo.atualiza_acervo()
    robo.download_atualizacao_diaria()
    robo.escreve_log('############ FIM ROBÔ DJMT #############')
