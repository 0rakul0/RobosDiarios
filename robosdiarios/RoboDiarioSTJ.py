from datetime import datetime,timedelta, date
import os,PyPDF2
from PyPDF2 import PdfFileMerger
import traceback
import requests
import zipfile
import time
from pathlib import Path
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup as bs
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.StringUtil import remove_acentos, remove_varios_espacos
from util.ConfigManager import ConfigManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import UnexpectedAlertPresentException
from util.FileManager import DiarioNaoDisponivel
import re



class RoboDiarioSTJ(RoboDiarioBase):

    def __init__(self):
        self.__url = "https://ww2.stj.jus.br/processo/dj/init"
        self.__url_download= 'https://ww2.stj.jus.br/docs_internet/processo/dje/zip/stj_dje_{data}.zip'
        super(RoboDiarioSTJ, self).__init__("DJSTJ", "log_robo_stj.txt", "erro_robo_stj.txt")
        self.pdf_atual =  1

    # def atualiza_acervo_stj(self):
    #     conseguiu = False
    #     s = requests.Session()
    #
    #     while not conseguiu:
    #         try:
    #             # url = 'http://diario.tjrr.jus.br/dpj/'
    #             # pagina = s.get(url)
    #             # soup = bs(pagina.text, "html5lib")
    #             driver = webdriver.Chrome(executable_path='C:\\Users\\e279274021\\Desktop\\chromedriver.exe')
    #             driver.get(self.url_consulta_ce + 'cons_proca.asp')
    #             driver.find_element(By.XPATH, '//*[@id="parametro_tela"]').send_keys('1')
    #             driver.find_element(By.XPATH, '//*[@id="id_btn_consultar"]').click()
    #             diarios = 'teste'
    #
    #
    #             for diario in diarios:
    #                 data = self.pega_data(diario)
    #                 nome = "DJSTJ_{data}.zip".format(data=data.strftime("%Y%m%d"))
    #                 link = 'https://ww2.stj.jus.br/docs_internet/processo/dje/zip/stj_dje_{}.zip'.format(diario.text)
    #                 self.escreve_log("Acessando diário em {}".format(link))
    #                 self.filemanager.download(name=nome,data=data,url=link)
    #                 conseguiu = True
    #             conseguiu = True
    #         except Exception as e:
    #             self.escreve_log("Erro: {e}".format(e=str(e)))
    #             self.tentativas += 1

    def download_atualizacao_diaria(self):
        #data = self.data_inicial('DSTJ')
        data = datetime.now ().date ()
        #data = date(2007,10,2)
        s = requests.Session()
        data_final = date(2007,10,1)
        tentativas = 0

        while data_final <= data and tentativas <= 5 :
            try:

                url_base= 'https://ww2.stj.jus.br/'
                driver = webdriver.Chrome(executable_path='./chromedriver')
                driver.get('https://ww2.stj.jus.br/processo/dj/init')
                driver.find_element(By.XPATH, '//*[@id="id_sel_tipo_pesquisa"]').send_keys('inteiro')
                datefield = driver.find_element(By.XPATH, '//*[@id="id_data_pesquisa"]')
                datefield.click()
                datefield.send_keys(Keys.CONTROL,'a')
                datefield.send_keys(Keys.BACKSPACE)
                datefield.send_keys(data.strftime('%d%m%Y'))
                driver.find_element(By.XPATH, '//*[@id="id_btn_consultar"]').click()
                driver.switch_to_default_content()
                self.baixar_diario(driver,data)
                data += timedelta(1)
            except Exception as e:
                self.escreve_log("Erro: {e}".format(e=str(e)))
                self.tentativas += 1

    def baixar_diario(self,driver,data):
        Proxpag = True
        while Proxpag:
            html = driver.page_source
            soup = bs(html)
            if 'Sem ocorrências' in soup.find('div', {'id': 'idDjPaginadoBlcoPrincipal'}).text.strip().split('.')[0]:
                print('Sem diario nesse dia :', data)
                driver.quit()
                return  data
            pdfs = soup.findAll('div', {'class': 'clsDjArvoreCapituloBloco'})
            for link in pdfs[0].find_all('a', onclick=True):
                seq = re.findall('(\d{7,8})', link['onclick'])[0].strip()
                imp = re.findall('\'(\d{2,5})\'', link['onclick'])[0].strip()
                dataarq = re.findall('(\d{2}\/\d{2}\/\d{4})', link['onclick'])[0].strip()
                nome = 'DSTJ_{}_{}.pdf'.format(str(data).replace('-', '_'), seq, pdf=self.pdf_atual)
                urldow = 'https://ww2.stj.jus.br/processo/dj/documento/?seq_documento={}&data_pesquisa={}&seq_publicacao={}&versao=impressao&nu_seguimento=00001'.format(
                    seq, dataarq, imp)
                baixou = self.filemanager.download(name=nome, data=data, url=urldow)
                if baixou is True:
                    tentativas = 0
                else:
                    self.escreve_log(
                        '{}. Tentando baixar o caderno DJSTJ_{} novamente'.format(tentativas, data))
                    tentativas += 1
            if soup.find('span', {'class': 'clsDjPaginacaoBotoesProximaPaginaTexto'}):
                driver.find_element(By.XPATH, '//*[@id="idDjBarraNavegacaoSuperior"]/div/span[2]').click()
            else:
                caminho_arq = os.path.join(self.filemanager.caminho(nome, data, True), nome)
                caminho = caminho_arq.replace(nome, '') + 'FULL_DSTJ_{}.pdf'.format(str(data))
                filenames_merge = caminho_arq.replace('\\' + nome, '')
                self.juntar_pdfs(data,seq,caminho, filenames_merge)
                print('Deu merge')
                Proxpag = False
                driver.quit()





        #driver.quit()



    def juntar_pdfs(self,data,seq,caminho,filenames_merge):
        # prefixo = "STJ"
        # if qtd_pdf:
        #     pdfs = []
        #     for pagina in range(1, qtd_pdf + 1):
        #         nome = "{prefixo}_{data}_{page:04d}.pdf".format(prefixo=prefixo,
        #                                                         data=data.strftime("%Y_%m_%d"), page=pagina)
        #         pdf = os.path.join(self.filemanager.caminho(nome, data, True), nome)
        #         pdfs.append(pdf)
        #
        #     nome = "{prefixo}_{data}.pdf".format(prefixo=prefixo, data=data.strftime("%Y_%m_%d"))
        #     saida = os.path.join(self.filemanager.caminho(nome,data,  True), nome)
        #     self.filemanager.juntar_pdfs(saida=saida, pdfs=pdfs, apagar_arquivos=True)
        #     statinfo = os.stat(saida)
        #     if statinfo.st_size == 0:
        #         os.remove(saida)
        all_filenames = [str(i) for i in Path(filenames_merge).rglob('DSTJ*.pdf')]

        self.filemanager.juntar_pdfs(saida=caminho, pdfs=all_filenames,apagar_arquivos=True,ordenar=False)

    def pega_data(self, diario):
        data = re.search('\d{8}', diario.text).group(0)
        ano = int(''.join(list(data)[:4]))
        mes = int(''.join(list(data)[4:6]))
        dia = int(''.join(list(data)[6:]))
        data = datetime(day=dia, month=mes, year=ano)
        return data

    def escreve_log(self, texto):
        ConfigManager().escreve_log(texto, self.robo, self.log)


    def data_limite(self):
        return date(2007,10,1)

if __name__ == '__main__':
    robo = RoboDiarioSTJ()
    #robo.atualiza_acervo_rr()
    robo.download_atualizacao_diaria()