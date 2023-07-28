__author__ = 'B249025230'

from datetime import datetime, date, timedelta
import os
import traceback
import requests
from bs4 import BeautifulSoup

from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel


class RoboDiarioDOU(RoboDiarioBase):
    def __init__(self):
        self.url_num_pages = "http://pesquisa.in.gov.br/imprensa/jsp/visualiza/index.jsp?jornal={caderno}&pagina=1&data={data}"
        self.url2 = "http://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal={caderno}&pagina={pagina}&data={data}&captchafield=firstAccess"
        # self.url = 'https://pesquisa.in.gov.br/imprensa/jsp/visualiza/index.jsp?jornal={caderno}&pagina={pagina}&data={data}'
        super(RoboDiarioDOU, self).__init__("DOU",  "log_robo_dou.txt",  "erro_robo_dou.txt")
    def download_atualizacao_diaria(self):
        atual = datetime.now().date()

        data = self.data_inicial("DOU")
        # data = date(2017,11,24)

        while atual >= data:
            for caderno in 1,2,3:
                conseguiu = False
                self.tentativas = 0

                while not conseguiu:
                    try:
                        nome = 'DOU_Cad{cad}_{ano}_{mes:02d}_{dia:02d}.pdf'.format(
                            ano=data.year,mes=data.month,dia=data.day,cad=caderno)
                        if not self.filemanager.ja_baixado(nome, data, "*.pdf"):

                            data_str = '/'.join(str(data).replace('-','/').split('/')[::-1])
                            if caderno is 1:
                                caderno = 515
                            elif caderno is 2:
                                caderno = 529
                            elif caderno is 3:
                                caderno = 530
                            dou = requests.get(self.url_num_pages.format(caderno=caderno, data=data_str),verify=False, timeout=self.timeout)
                            ConfigManager ().escreve_log ("Acessando {}".format (self.url_num_pages.format (
                                caderno=caderno, data=data_str)), self.robo,
                                self.log)

                            soup = BeautifulSoup(dou.content, "html5lib")
                            if 'Os seguintes problemas' not in soup.prettify():
                                texto=str(soup.frame)
                                # posicao=texto.find('totalArquivos')+14
                                num_pags = texto.split('=')[-1].replace('\"/>','')
                                nr_pag_int = int(num_pags)
                                pdfs= []
                                urls_download = list (self.url2.format (caderno=caderno, pagina=i, data=data_str) for i in range (1, nr_pag_int + 1))
                                for num_pag_atual in enumerate(urls_download,start=0):
                                    if caderno is 515:
                                        caderno = 1
                                    elif caderno is 529:
                                        caderno = 2
                                    elif caderno is 530:
                                        caderno = 3
                                    arq = 'DOU_Cad{cad}_{ano}_{mes:02d}_{dia:02d}_{pag:04d}.pdf'.format(ano=data.year,mes=data.month,dia=data.day,cad=caderno,pag=num_pag_atual[0])

                                    if not self.filemanager.ja_baixado(arq, data, "*.pdf"):

                                        try:
                                            self.filemanager.download(arq, data, urls_download[num_pag_atual[0]], False, True, 10)

                                        except (DiarioNaoDisponivel, FileNotFoundError) as e:
                                            ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                                                data=data.strftime("%d/%m/%Y")), self.robo, self.log)

                                    elif self.filemanager.ja_baixado(nome, data, '*.pdf'):
                                        ConfigManager ().escreve_log ("Caderno já baixado previamente " + nome,
                                                                      self.robo, self.log)

                                    else:
                                        ConfigManager().escreve_log("Página já baixada previamente " + arq,
                                                                    self.robo, self.log)
                                    pag_i = os.path.join(self.filemanager.caminho(arq, data, True), arq)
                                    pdfs.append(pag_i)
                                final = os.path.join(self.filemanager.caminho(nome, data, True), nome)
                                ConfigManager().escreve_log('Fazendo merge do PDF "' + nome + '"', self.robo, self.log)
                                self.filemanager.juntar_pdfs(final, pdfs)
                                ConfigManager().escreve_log('Merge do PDF "' + nome+ '" feito com sucesso', self.robo, self.log)
                                for pdf in pdfs:
                                    os.remove(pdf)
                                conseguiu =True
                        else:
                            ConfigManager().escreve_log('PDF Final já baixado previamente '+ nome, self.robo, self.log)

                        conseguiu = True
                    except Exception as er:
                        ConfigManager().escreve_log("Erro: " + str(er), self.robo, self.erro)
                        self.tentativas += 1
            data += timedelta(1)



    def data_limite(self):
        return date(2017,11,23)

    def existe_pagina(self, url):
        try:
            requests.get(url, verify=False, timeout=self.timeout)
            return True
        except FileNotFoundError:
            return False

    '''
    def renomeia_arquivo(self, pasta):
        arquivos = os.listdir(pasta)
        for arquivo in arquivos:
            nome = self.novo_nome(arquivo)
            os.rename(os.path.join(pasta, arquivo), os.path.join(pasta, nome))

    def mudar_nomes(self):
        txts_convertidos = os.path.join(self.path,"txt_a_extrair")
        txts_extraidos = os.path.join(self.path,"txt_repositorio")
        pdfs_convertidos = os.path.join(self.path,"pdf_repositorio")
        pdfs_a_converter = os.path.join(self.path,"pdf_a_converter")

        self.renomeia_arquivo(txts_convertidos)
        self.renomeia_arquivo(txts_extraidos)
        self.renomeia_arquivo(pdfs_convertidos)
        self.renomeia_arquivo(pdfs_a_converter)

    def novo_nome(self,nome_antigo):
        novo = nome_antigo
        regex = re.search("(\d{4}_\d{2}_\d{2})_(.*)\.(.*)",nome_antigo)
        data = regex.group(1)
        caderno = regex.group(2)
        extensao = regex.group(3)
        if data and caderno and extensao:
            novo = "DOU_" + caderno + "_" + data + "." + extensao
        return novo
    '''

if __name__ == '__main__':
    robo = RoboDiarioDOU()
    robo.download_atualizacao_diaria()