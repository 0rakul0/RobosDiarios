# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
import time
import traceback
import re
import os
import requests
from pathlib import Path
import shutil
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from util.StringUtil import remove_acentos
from pdjus.service.ArquivoService import ArquivoService
from pdjus.service.CadernoService import CadernoService
from pdjus.service.DiarioService import DiarioService
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from pdjus.modelo.Diario import Diario
from pdjus.modelo.Caderno import Caderno


class RoboDiarioJusBrasil(RoboDiarioBase):

    def __init__(self):
        # self.__url = "http://www.jusbrasil.com.br/diarios/{diario}/{data}"
        self.url_base = 'http://www.jusbrasil.com.br'
        self.url = 'http://www.jusbrasil.com.br/diarios/{diario}/{ano}/{mes:02d}/{dia:02d}'
        self.browser = None
        self.conseguiu = False
        self.diarios = {"TJ-ES": "DJES","DJAL": "DJAL", "DJAM": "DJAM", "DJRO": "DJRO"}
        # self.diarios = {
        #             "DJAC": "DJAC", "DJAL": "DJAL", "DJAM": "DJAM", "DJAP": "DJAP", "DJBA": "DJBA", "DJCE": "DJCE",
        #             "DJDF": "DJDF", "TJ-ES": "DJES", "DJGO": "DJGO", "DJMA": "DJMA", "DJMG": "DJMG", "DJMS": "DJMS",
        #             "DJMT": "DJMT", "DJPA": "DJPA", "DJPB": "DJPB", "DJPE": "DJPE", "DJPI": "DJPI", "DJPR": "DJPR",
        #             "DJRJ": "DJRJ", "DJRN": "DJRN", "DJRO": "DJRO", "DJRR": "DJRR", "DJRS": "DJRS", "DJSC": "DJSC",
        #             "DJSE": "DJSE", "DJSP": "DJSP", "DJTO": "DJTO", "STF": "STF", "STJ": "STJ", "TRF-1": "TRF01",
        #             "TRF-2": "TRF02", "TRF-3": "TRF03", "TRF-4": "TRF04", "TRF-5": "TRF05", "TRT-1": "TRT01",
        #             "TRT-2": "TRT02", "TRT-3": "TRT03", "TRT-4": "TRT04", "TRT-5": "TRT05", "TRT-6": "TRT06",
        #             "TRT-7": "TRT07", "TRT-8": "TRT08", "TRT-9": "TRT09", "TRT-10": "TRT10", "TRT-11": "TRT11",
        #             "TRT-12": "TRT12", "TRT-13": "TRT13", "TRT-14": "TRT14", "TRT-15": "TRT15", "TRT-16": "TRT16",
        #             "TRT-17": "TRT17", "TRT-18": "TRT18", "TRT-19": "TRT19", "TRT-20": "TRT20", "TRT-21": "TRT21",
        #             "TRT-22": "TRT22", "TRT-23": "TRT23", "TRT-24": "TRT24", "TST": "TST",
        #             "TRE-BA": "TRE-BA", "TRE-PB": "TRE-PB", "TRE-AL": "TRE-AL", "TRE-GO": "TRE-GO", "TRE-MG": "TRE-MG",
        #             "TRE-PE": "TRE-PE", "TRE-RO": "TRE-RO", "TRE-RR": "TRE-RR", "TRE-SC": "TRE-SC", "TRE-SP": "TRE-SP",
        #             "TRE-SE": "TRE-SE", "TRE-AC": "TRE-AC", "TRE-AP": "TRE-AP", "TRE-AM": "TRE-AM", "TRE-CE": "TRE-CE",
        #             "TRE-DF": "TRE-DF", "TRE-ES": "TRE-ES", "TRE-MA": "TRE-MA", "TRE-MT": "TRE-MT", "TRE-MS": "TRE-MS",
        #             "TRE-PA": "TRE-PA", "TRE-PR": "TRE-PR", "TRE-PI": "TRE-PI", "TRE-RJ": "TRE-RJ", "TRE-RN": "TRE-RN",
        #             "TRE-RS": "TRE-RS", "TRE-TO": "TRE-TO", "TSE": "TSE"}

        super(RoboDiarioJusBrasil, self).__init__("JusBrasil", "log_robo_jusbrasil.txt", "erro_robo_jusbrasil.txt")


    def organiza_diarios_sem_diretorio(self, caminho): # USADO PARA ORGANIZAR APENAS DIÁRIOS EM Q O PADRÃO DE NOME POSSUA ANO E MES
        pasta = caminho+'/pdf_a_converter'
        lista_de_arquivos = os.listdir(pasta)
        print('Número de arquivos a serem transferidos: '+str(len(lista_de_arquivos)))
        for arq in lista_de_arquivos:

            extensao = os.path.splitext(arq)[1][1:]
            if extensao == 'py':
                continue
            ano = re.search('\d{4}',arq).group(0)
            mes = re.search('\_(\d{2}|\d)\_',arq).group(0).replace('_','')
            path = caminho+'/'+extensao+'/'+ano+'/'+mes
            path_with_arq = path+'/'+arq

            if os.path.exists(path):
                shutil.move(pasta+'/'+arq, caminho+'/'+extensao+'/'+ano+'/'+mes+'/'+arq)
                print("Arquivo {} transferido!!!".format (arq))

            elif not os.path.exists(path_with_arq):
                print("Criando diretório e transferindo arquivo {} para o caminho {}".format (arq, path))
                os.makedirs (path)
                shutil.move(pasta+'/'+arq, caminho+'/'+extensao+'/'+ano+'/'+mes+'/'+arq)

            else:
                print ("Transferindo arquivo {} para o caminho {}".format (arq, path))
                shutil.move (pasta + '/' + arq, caminho + '/' + extensao + '/' + ano + '/' + mes + '/' + arq)

        print('Foi juregue!!!')


    def juntar_paginas_jusbrasil(self,texto, caminho, nome_caderno):
        join_paginas = ' '.join(texto[0:]).replace('[\'', '').replace('\']', '')
        arquivo = open(caminho + '/' + nome_caderno, 'w+', encoding="utf-8")
        arquivo.writelines (join_paginas)
        arquivo.close ()
        ConfigManager().escreve_log('Merge do caderno {} feito com sucesso!!!\n\n'.format(nome_caderno),self.robo,self.log)

    def nome_do_caderno(self, secao, data, nome_diario):

        if 'PÁGINAS SEM CADERNO' in secao.contents[1].find('a').text.upper():
            nome_caderno = remove_acentos(nome_diario+'_'+data.strftime('%Y_%m_%d')+'.txt')
        else:
            nome_caderno = remove_acentos(nome_diario+'_'+secao.contents[1].find ('a').text \
                               .replace (' - ', '_').replace ('(', '') \
                               .replace (')', '').replace (' ', '_') \
                            + '_' + data.strftime ('%Y_%m_%d') + '.txt')
        return nome_caderno

    def open_selenium(self):
        chrome_options = webdriver.ChromeOptions ()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option ("prefs", prefs)
        self.browser = webdriver.Chrome (executable_path='//mnt//dmlocal//projetos//IPEAJUS-PRODUCAO//chromedriver.exe', chrome_options=chrome_options)
        self.browser.delete_all_cookies()
        self.browser.minimize_window ()

    def selenium_para_bs(self, url_formatada=None, class_name=None, nome_caderno=None, data=None):

        if self.browser is None:
            self.open_selenium()

        if url_formatada is None:
            soup = bs (self.browser.find_element(by=By.CLASS_NAME, value=class_name).get_attribute ("outerHTML"), "html5lib")
            return soup
        else:
            tentativas = 0
            while tentativas <= 3:
                self.browser.get (url_formatada)
                try:
                    soup = bs (self.browser.find_element(by=By.CLASS_NAME, value=class_name).get_attribute ("outerHTML"), "html5lib")
                    return soup
                except Exception as e:
                    erro = self.browser.find_element(by=By.XPATH, value='/html/body/a/img').get_attribute('outerHTML')
                    if '404.png' in erro:
                        ConfigManager ().escreve_log ("Diário {diario} não encontrado no dia {data}!!!".format (diario=nome_caderno, data=data), self.robo, self.log)
                        self.conseguiu = True
                        break
                    elif '410.png' in erro: # PÁGINAS FALTANDO NO SITE DO JUSBRASIL :(
                        tentativas += 1
                        self.browser.close()
                        self.browser = None
                        ConfigManager ().escreve_log ("Tentando baixar o diário {diario} novamente (erro 410: páginas retiradas do site): {url}!!!"
                                                      .format (diario=nome_caderno, url=url_formatada), self.robo, self.log)
                    else:
                        tentativas += 1
                        self.browser.close ()
                        self.browser = None
                    ConfigManager ().escreve_log ("Diário {diario} não baixado: {url}!!!"
                                                  .format (diario=nome_caderno, url=url_formatada), self.robo, self.log)


    def download_antigos(self):
        nome_diario = input ("Nome do diário (DJAL, DJAM, DJRO, TJ-ES): ")  # DJAL, DJAM, DJRO, TJ-ES
        self.download(nome_diario)

    def download_atualizacao_diaria(self):
        # arquivo_service = ArquivoService()
        # diario_service = DiarioService()
        # caderno_service = CadernoService()
        # dict_meses = {'January':'Janeiro','February':'Fevereiro','March':'Março','April':'Abril','May':'Maio','June':'Junho','July':'Julho','August':'Agosto','September':'Setembro','October':'Outubro','November':'Novembro','December':'Dezembro'}
        for nome_diario in self.diarios:
            self.download(nome_diario)


    def verifica_caminho_arquivo(self, data, nome_diario,nome_caderno, link):

        caminho = self.filemanager.caminho (nome_diario, data=None, por_tipo=True)
        extensao = os.path.splitext (nome_caderno)[1][1:]
        path = ''.join (list (caminho)[:-8])+extensao+'/'+ data.strftime ('%Y') + '/' + data.strftime ('%m')

        if os.path.exists (path + '/' + nome_caderno):
            ConfigManager ().escreve_log ("Caderno {} já baixado!!!".format (nome_caderno), self.robo, self.log)
            return None
        else:
            ConfigManager ().escreve_log ("Acessando seções do diário {diario} na url: {url}".format (diario=nome_caderno, url=self.url_base + link), self.robo, self.log)

            if not os.path.exists (path):
                os.makedirs (path)

            return path

    def busca_secoes(self, nome_caderno, link, path):

        try:
            pagina = self.selenium_para_bs (url_formatada=self.url_base + link, class_name='diario-pages', nome_caderno=nome_caderno).find_all ('a')[0].attrs['href']
            prox_pag = self.selenium_para_bs (url_formatada=self.url_base + pagina, class_name='JournalPaginator', nome_caderno=nome_caderno)
            qtd_pags = int (self.selenium_para_bs (class_name='JournalPaginator-pages-amount', nome_caderno=nome_caderno).text.replace ('/', ''))
            total_pags = qtd_pags

            print ('PÁGINA ATUAL DO CADERNO {}: {} / {}'.format (nome_caderno, 1, total_pags))

            if 'PRÓXIMA PÁGINA' in prox_pag.text.upper ():

                linhas = self.selenium_para_bs (class_name='DocumentView-content-text', nome_caderno=nome_caderno)
                texto = []

                while qtd_pags:
                    texto, qtd_pags, linhas = self.append_paginas(total_pags=total_pags, linhas=linhas,qtd_pags=qtd_pags,nome_caderno=nome_caderno, texto=texto)

                self.juntar_paginas_jusbrasil (texto=texto, caminho=path, nome_caderno=nome_caderno)

            else:
                linhas = self.selenium_para_bs (class_name='DocumentView-content-text', nome_caderno=nome_caderno)
                texto = []

                try:
                    texto.append (linhas.text)
                    self.juntar_paginas_jusbrasil (texto=texto, caminho=path, nome_caderno=nome_caderno)
                except Exception as e:
                    print (e)

        except Exception as e:
            ConfigManager ().escreve_log ("Impossível acessar o caderno {}!!!".format (nome_caderno), self.robo, self.log)

    def append_paginas(self,total_pags, linhas,qtd_pags, nome_caderno, texto):

        texto.append (linhas.text)

        if ((total_pags - qtd_pags) + 1) % 25 == 0:  # DE 25 EM 25 PAGS O CÓDIGO IMITA O SER HUMANO ESPERANDO UM SEG, ROLANDO A PAG PRA BAIXO E ESPERANDO MAIS UM SEG
            time.sleep (1)
            self.browser.execute_script ("window.scrollTo(0, 100000)")
            time.sleep (1)

        prox_pag = self.selenium_para_bs (class_name='JournalPaginator', nome_caderno=nome_caderno).find_all ('a')[-1].attrs['href']

        linhas = self.selenium_para_bs (url_formatada=prox_pag, class_name='DocumentView-content-text', nome_caderno=nome_caderno)

        print ('PÁGINA ATUAL DO CADERNO {}: {} / {}'.format (nome_caderno, total_pags - qtd_pags + 2, total_pags))

        qtd_pags -= 1

        return texto, qtd_pags, linhas

    def download(self, nome_diario):

        atual = datetime.now ().date ()
        data = self.data_inicial("JUSBRASIL")  # data do último diário baixado
        # data = self.data_limite() # usado para baixar apartir da data limite
        print ('########## ' + datetime.now ().strftime ('%Y/%m/%d - ( %H:%m:%S )') + ' ##########\n\n')

        while atual >= data:

            self.conseguiu = False
            self.tentativas = 0

            while not self.conseguiu:
                try:
                    secoes = self.selenium_para_bs (url_formatada=self.url.format (diario=nome_diario, ano=data.year, mes=data.month, dia=data.day), class_name='sections', nome_caderno=nome_diario, data=data).find_all ("li")

                    if secoes:
                        for secao in secoes:
                            link = secao.find_all ('a')[1].attrs['href']
                            nome_caderno = self.nome_do_caderno (secao=secao, data=data, nome_diario=nome_diario)
                            path = self.verifica_caminho_arquivo (data, nome_diario, nome_caderno, link)
                            if path is not None:
                                self.busca_secoes (nome_caderno, link, path)
                            else:
                                continue
                        self.conseguiu = True

                except Exception as e:
                    break
            data += timedelta (1)
            time.sleep (2)

    def data_limite(self):
        return date(2013, 1, 1)


if __name__ == '__main__':
    robo = RoboDiarioJusBrasil()
    robo.download_antigos()
    # robo.download_atualizacao_diaria()
    # robo.organiza_diarios_sem_diretorio ('/mnt/dmlocal/dados/RO/DJRO')
