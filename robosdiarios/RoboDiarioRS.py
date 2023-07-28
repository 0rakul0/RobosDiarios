# -*- coding: utf-8 -*-
from datetime import datetime, date
import time
import traceback
import json
from bs4 import BeautifulSoup
import requests
import re
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel
from dateutil.relativedelta import relativedelta

class RoboDiarioRS(RoboDiarioBase):

    def __init__(self):
        self.url = 'https://wls.tjrs.jus.br/servicodag/?callback=edicoesPeriodo&tipo=periodo&periodo={DATA}&_='+str(int(round(time.time() * 1000)))#1585665590161'
        self.__url_jusbrasil = 'http://www.jusbrasil.com.br/diarios/{}'
        self.url_download = 'https://www.tjrs.jus.br/servicos/diario_justica/'
        self.tentativas = 0
        super(RoboDiarioRS, self).__init__("DJRS", "log_robo_rs.txt", "erro_robo_rs.txt")

    # TODO Implementar download jusbrasil por data
    # Atualmente data fixa!
    def download_jus_brasil(self):
        data = datetime.strptime("20/08/2015",'%d/%m/%Y')
        link = "http://www.jusbrasil.com.br/diarios/DJRS/{}/{:02d}/{:02d}/Editais-1o-e-2o-grau".format(data.year,data.month,data.day)
        page = requests.get(link, verify=False, timeout=self.timeout)
        soup = BeautifulSoup(page.text)
        paginas = soup.find("select",{"name" : "view_page"})
        if paginas:
            qtd_paginas = int(soup.find("select",{"name" : "view_page"}).find_all("option")[-1].get_text())
            if soup.find('li', {"class":"page"}).find('p').find('a')['href']:
                id_inicial = int(soup.find('li',{"class":"page"}).find('p').find('a')['href'].split('/')[2])
                for pagina_atual in range(id_inicial,id_inicial+qtd_paginas):
                    name = "DJRS_Editais_1_e_2_Grau_{}_{}_{}_pg_{}.html".format(data.year, data.month,
                                                                                           data.day,  pagina_atual - id_inicial + 1)
                    url = self.__url_jusbrasil.format(pagina_atual)
                    try:
                        ConfigManager().escreve_log("Acessando {}".format(url), self.robo, self.log)
                        # ConfigManager().escreve_log("Buscando {} em {}...".format(name, url), self.robo, self.log)
                        self.filemanager.download(name, data, url, False)
                    except (DiarioNaoDisponivel, FileNotFoundError) as e:
                        ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                            data=data.strftime("%d/%m/%Y")), self.robo, self.log)
                    except Exception as er:
                        ConfigManager().escreve_log("Erro em "+name+":" + traceback.format_exc(), self.robo, self.erro)

    def download_atualizacao_diaria(self):
        data = self.data_inicial('DJRS') - relativedelta(days=1)
        # data = self.data_limite()-relativedelta(days=1)

        # ConfigManager().escreve_log("Começando em {}...".format(data.strftime("%d/%m/%Y")), self.robo, self.log)
        self.download_antigos(data)

    def download_antigos(self, data):
        prefixo_json = 'edicoesPeriodo'
        while data < date.today():
            html = requests.get(self.url.format(DATA=data.strftime('%m-%Y')),
                                 verify=False, timeout=10).text
            self.download(html, prefixo_json, data)
            data += relativedelta(months=+1)


    def download(self, html, prefixo_json, data):
        js = html.replace("id", "\"id\"") \
            .replace("data", "\"data\"") \
            .replace("cadernos", "\"cadernos\"") \
            .replace("cadernoLabel", "\"cadernoLabel\"") \
            .replace("cadernoUrl", "\"cadernoUrl\"") \
            .replace("" + prefixo_json + "(", "\"" + prefixo_json + "\":") \
            .replace("])", "]")

        js = "{" + js + "}"

        diarios = json.loads(js)
        print('\n{} editais encontrados no mês {}'.format(len(diarios[prefixo_json]), data.strftime('%m-%Y')))

        for diario in diarios[prefixo_json]:
            data = diario['data'].split('-')
            data = date(int(data[0]), int(data[1]), int(data[2]))
            self.tentativas = 0
            for caderno in diario['cadernos']:
                tipo_caderno = caderno['cadernoLabel'].replace(' ','_')

                tipo_caderno = self.teste_nome_caderno(tipo_caderno)

                nome_caderno = 'DJRS_'+tipo_caderno+'_'+str(data).replace('-','_')+'.pdf'

                if self.filemanager.ja_baixado(nome_caderno, data, '*.pdf'):
                    print('# Arquivo {} previamente já baixado!!!'.format(nome_caderno))
                    continue
                else:
                    caderno_url = caderno['cadernoUrl']
                    html_caderno = requests.get(caderno_url, verify=False, timeout=30).text
                    soup_caderno = BeautifulSoup(html_caderno,'html5lib')
                    try:
                        link_download = self.url_download+soup_caderno.find_all('a', {'class':'texto_geral_peq'})[0]['href']
                        conseguiu = False
                    except Exception as e:
                        print('Erro: {}'.format(soup_caderno.text))
                        conseguiu = True
                        self.tentativas = 0

                    while not conseguiu and self.tentativas <= 3 and not 'RESOLUÇÃO' in nome_caderno:   #Nao sei exatamente o que é resolução mas acho que nao é diario e tb nao conseguia baixar nada entao coloquei pra pular elas
                        try:
                            self.filemanager.download(nome_caderno, data, link_download, False, True, 10)
                            conseguiu = True
                            self.tentativas = 0
                        # except (DiarioNaoDisponivel, FileNotFoundError) as e:
                        #     ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                        #         data=date.strftime("%d/%m/%Y")), self.robo, self.log)
                        #     conseguiu = True
                        except Exception as er:
                            ConfigManager().escreve_log("Erro: " + str(er), self.robo, self.erro)
                            self.tentativas += 1


    def teste_nome_caderno(self, tipo_caderno):
        if 'DRH_-_SELAP' in tipo_caderno:
            tipo_caderno = re.sub ('.*', 'Edital_DRH_SELAP', tipo_caderno)

        elif re.search ('\_CECPODNR\_?', tipo_caderno):
            tipo_caderno = re.sub ('.*', 'Edital_CECPODNR', tipo_caderno)

        elif re.search ('.*Lista\_de\_Jurados?', tipo_caderno):
            tipo_caderno = re.search ('.*Lista\_de\_Jurados?', tipo_caderno).group (0)

        elif re.search ('\_CGJ\_?', tipo_caderno):
            tipo_caderno = re.sub ('\_n.*\-_', '_', tipo_caderno)

        elif 'SCICM_E_PRECATÓRIOS' in tipo_caderno:
            tipo_caderno = re.sub ('\_n.*', '_SCICM_E_PRECATÓRIOS', tipo_caderno)

        elif re.search ('\_?SCICM\_?', tipo_caderno):
            tipo_caderno = re.sub ('\_n.*\-_', '_', tipo_caderno)

        elif re.search ('\_?RECSEL\_?', tipo_caderno):
            tipo_caderno = re.sub ('\_n.*\-_', '_', tipo_caderno)

        elif 'Ato_Convocatório' in tipo_caderno:
            tipo_caderno = 'Ato_Convocatorio'

        elif 'Tabela_de_Emolumentos' in tipo_caderno:
            tipo_caderno = 'Tabela_de_Emolumentos'

        elif re.search ('Edita(l|is)(\_|\s+)n\.', tipo_caderno):
            tipo_caderno = re.sub ('Edita(l|is).*', 'Editais', tipo_caderno)

        elif re.search ('\d{4}', tipo_caderno):
            print (tipo_caderno)

        return tipo_caderno

    def data_limite(self):
        # return (date(2020,3,17))
        return date(datetime.now().year,datetime.now().month,datetime.now().day)


if __name__ == '__main__':
    robo = RoboDiarioRS()
    robo.download_atualizacao_diaria()
    #robo.download_antigos(date(day=3, month=9, year=2020))