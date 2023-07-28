import re
from datetime import datetime
from util.ConfigManager import ConfigManager
from util.SeleniumUtil import *
from util.StringUtil import remove_varios_espacos, remove_quebras_linha_de_linha
from bs4 import BeautifulSoup as bs
from robosdiarios.RoboDiarioBase import RoboDiarioBase
import os.path
from datetime import datetime, date, timedelta
import time as t
from selenium import webdriver
from selenium.webdriver.common.by import By
from pathlib import Path
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import shutil


class RoboDiarioTRF2(RoboDiarioBase):

    def __init__(self):
        self.url_trf2_pesquisa_documentos = 'https://dje.trf2.jus.br/DJE/Paginas/Externas/FiltraPesquisaDocumentos.aspx'
        self.browser = None
        super(RoboDiarioTRF2, self).__init__("TRF02", "TRF2_robodiario.txt", "TRF2_robodiario.err")


    def download_atualizacao_diaria(self):

        self.escreve_log('########### INÍCIO ROBÔ TRF02 ###########')
        data = date(2020,1,15)
        # data = self.data_inicial("TRF02")
        # path = self.get_path_download(data)
        path = '/mnt/dmlocal/dados/TRF/TRF02/pdf/organizador'


        while data <= date.today():
            self.escreve_log('+-+-+-+ ' + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' +-+-+-+')
            if not self.verifica_ja_baixado(data, path):
                self.acessa_url(url=self.url_trf2_pesquisa_documentos, path=path)
                try:
                    self.acessa_pag_perigosa()
                except:
                    pass
                data = self.arvore(data, path)
            else:
                data += timedelta(days=1)

            # path = self.get_path_download(data)
            # self.browser.create_options().add_experimental_option('prefs',{"download.default_directory": os.path.abspath(path)})

        self.browser.quit()


    def arvore(self, data, path):

        self.marca_checkbox()
        self.data_params(data=data.strftime('%d%m%Y'))
        self.select_qtd_diarios()
        self.botao_pesquisar()

        try:
            t.sleep(2)
            soup = selenium_for_bs(self.browser,'ctl00_ContentPlaceHolder_ctrListaDiarios_pnlDiarios', 'ID')
        except:
            t.sleep(3)
            self.browser.refresh()
            t.sleep(2)
            find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_btnVoltar"]')
            self.marca_checkbox()
            self.data_params(data=data.strftime('%d%m%Y'))
            self.select_qtd_diarios()
            self.botao_pesquisar()
            soup = selenium_for_bs(self.browser, 'ctl00_ContentPlaceHolder_ctrListaDiarios_pnlDiarios', 'ID')

        self.scraping(soup, data, path)
        self.browser.execute_script("window.history.go(-1)")
        data += timedelta(days=1)
        return data

    def get_path_download(self, data):

        path = self.filemanager.caminho('TRF02_'+str(data).replace('-','_')+'.pdf')
        # options.add_experimental_option("prefs", {"download.default_directory": os.path.abspath(path)})
        # self.browser = webdriver.Chrome(executable_path='C:\\Users\\e7609043\\Desktop\\chromedriver_win32\\chromedriver.exe',chrome_options=options)
        return path

    def verifica_ja_baixado(self,data, path=None):

        lista_nomes_cadernos = ['ADM_TRF2', 'JUD_TRF2', 'ADM_SJRJ', 'JUD_SJRJ', 'ADM_SJES', 'JUD_SJES']
        for caderno in enumerate(lista_nomes_cadernos):
            split_nome_caderno = caderno[1].split('_')
            nome_final_arquivo = 'TRF02_' + split_nome_caderno[0] + '_' + split_nome_caderno[1] + '_' + str (data).replace ('-', '_') + '.pdf'
            nome_arq_na_pasta = 'CADERNO_' + data.strftime('%d%m%Y') + '_' + split_nome_caderno[1] + '_' + split_nome_caderno[0] + '.pdf'
            if self.filemanager.ja_baixado(nome_arq_na_pasta, data, True):
                self.escreve_log('Caderno {} já baixado'.format(nome_arq_na_pasta))
                self.renomeia_arquivos(self.filemanager.caminho(nome_arq_na_pasta, data))
                if len(lista_nomes_cadernos) == caderno[0]+1:
                    return True
                else:
                    continue
            elif self.filemanager.ja_baixado(nome_final_arquivo, data, True):
                self.escreve_log('Caderno {} já baixado'.format(nome_final_arquivo))
                if len (lista_nomes_cadernos) == caderno[0]+1:
                    return True
                else:
                    continue

            elif os.path.exists(path+'/'+nome_arq_na_pasta):
                self.escreve_log('Caderno {} já baixado'.format(nome_arq_na_pasta))
                self.renomeia_arquivos(self.filemanager.caminho(nome_arq_na_pasta, data))
                if len(lista_nomes_cadernos) == caderno[0]+1:
                    return True
                else:
                    continue
            elif os.path.exists(path+'/'+nome_final_arquivo):
                self.escreve_log('Caderno {} já baixado'.format(nome_arq_na_pasta))
                if len(lista_nomes_cadernos) == caderno[0]+1:
                    return True
                else:
                    continue
            else:
                return False

    def acessa_url(self, url=None, path=None):

        if self.browser is None:
            prefs = {"download.default_directory": os.path.abspath(path)}
            self.browser = open_selenium('../chromedriver', options=prefs, path_download_file=path, headless=False)

        if url:
            t.sleep(2)
            self.browser.get(url)
            # self.browser.minimize_window()

    def acessa_pag_perigosa(self):

        self.browser.find_element(By.XPATH, '//*[@id="details-button"]').click()
        t.sleep(1)
        self.browser.find_element(By.XPATH, '//*[@id="proceed-link"]').click()
        t.sleep(1)


    def marca_checkbox(self):

        find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrFiltraPesquisaDocumentos_rblTipoPesquisa_0"]')


    def data_params(self, data):

        try:
            find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrFiltraPesquisaDocumentos_tbxDataInicial"]')
            t.sleep(1)
            ctrl_a(self.browser)
        except:
            t.sleep(3)
            find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrFiltraPesquisaDocumentos_tbxDataInicial"]')
            t.sleep(1)
            ctrl_a(self.browser)

        send_keys_by_xpath(self.browser,'//*[@id="ctl00_ContentPlaceHolder_ctrFiltraPesquisaDocumentos_tbxDataInicial"]', data)
        find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrFiltraPesquisaDocumentos_tbxDataFinal"]')

        try:
            find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrFiltraPesquisaDocumentos_tbxDataFinal"]')
            t.sleep(1)
            ctrl_a(self.browser)
        except:
            t.sleep(3)
            find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrFiltraPesquisaDocumentos_tbxDataFinal"]')
            t.sleep(1)
            ctrl_a(self.browser)

        send_keys_by_xpath(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrFiltraPesquisaDocumentos_tbxDataFinal"]', data)


    def select_qtd_diarios(self):

        find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrFiltraPesquisaDocumentos_ddlRegistrosPaginas"]/option[7]')


    def botao_pesquisar(self):

        t.sleep(1)
        try:
            find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrFiltraPesquisaDocumentos_btnFiltrar"]')
            t.sleep(1)
        except:
            t.sleep(3)
            find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrFiltraPesquisaDocumentos_btnFiltrar"]')

    def selenium_for_bs(self):

        soup = bs(self.browser.find_element(By.ID, 'ctl00_ContentPlaceHolder_ctrListaDiarios_pnlDiarios').get_attribute("outerHTML"), "html5lib")
        return soup

    def scraping(self, soup, data, path):

        cadernos = soup.find_all('div',{'id':'divVCConteudo'})
        if not 'Em PDF*' in cadernos[0].text:
            self.escreve_log('Não houve caderno na data {}'.format(data))
            return None
        else:
            self.baixa_cadernos(data, path)


    def baixa_cadernos(self, data, path):

        lista_nomes_cadernos = ['ADM_TRF2','JUD_TRF2','ADM_SJRJ','JUD_SJRJ','ADM_SJES','JUD_SJES']
        lista_nomes_finais = []
        lista_nomes_download = []

        for caderno in enumerate(lista_nomes_cadernos):
            split_nome_caderno = caderno[1].split('_')
            nome_final_arquivo = 'TRF02_' + split_nome_caderno[0] + '_' + split_nome_caderno[1] + '_' + str(data).replace('-', '_') + '.pdf'
            lista_nomes_finais.append(nome_final_arquivo)
            nome_arq_na_pasta = 'CADERNO_'+data.strftime('%d%m%Y')+'_'+split_nome_caderno[1]+'_'+split_nome_caderno[0]+'.pdf'
            lista_nomes_download.append(nome_arq_na_pasta)
            if self.filemanager.ja_baixado(nome_arq_na_pasta, data, True):
                self.escreve_log('Caderno {} já baixado'.format(nome_final_arquivo))
            elif self.filemanager.ja_baixado(nome_final_arquivo, data, True):
                self.escreve_log('Caderno {} já baixado'.format(nome_final_arquivo))
            else:
                t.sleep(2)
                self.cadernos(caderno[0], lista_nomes_finais, nome_final_arquivo, path)
                self.escreve_log('Baixou o caderno {} no caminho {}'.format(nome_final_arquivo, path))

        self.renomeia_arquivos(path)


    def cadernos(self, posicao_lista_download, lista_nomes_finais, nome_final_arquivo, path):

        if posicao_lista_download is 0:
            cad_adm_trf2 = find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrListaDiarios_udtVisualizaAdmTrf2_grvCadernos_ctl02_lnkData"]')
            # self.renomeia_arquivos(path,lista_nomes_finais,nome_final_arquivo)
            t.sleep (1)
        elif posicao_lista_download is 1:
            cad_jud_trf2 = find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrListaDiarios_udtVisualizaJudTrf2_grvCadernos_ctl02_lnkData"]')
            # self.renomeia_arquivos(path, lista_nomes_finais, nome_final_arquivo)
            t.sleep (1)
        elif posicao_lista_download is 2:
            cad_adm_rj = find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrListaDiarios_udtVisualizaAdmRj_grvCadernos_ctl02_lnkData"]')
            # self.renomeia_arquivos(path, lista_nomes_finais, nome_final_arquivo)
            t.sleep (1)
        elif posicao_lista_download is 3:
            cad_jud_rj = find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrListaDiarios_udtVisualizaJudRj_grvCadernos_ctl02_lnkData"]')
            # self.renomeia_arquivos(path, lista_nomes_finais, nome_final_arquivo)
            t.sleep (1)
        elif posicao_lista_download is 4:
            cad_adm_es = find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrListaDiarios_udtVisualizaAdmEs_grvCadernos_ctl02_lnkData"]')
            # self.renomeia_arquivos(path, lista_nomes_finais, nome_final_arquivo)
            t.sleep (1)
        elif posicao_lista_download is 5:
            cad_jud_rj = find_element_by_xpath_with_click(self.browser, '//*[@id="ctl00_ContentPlaceHolder_ctrListaDiarios_udtVisualizaJudEs_grvCadernos_ctl02_lnkData"]')
            # self.renomeia_arquivos(path, lista_nomes_finais, nome_final_arquivo)
            t.sleep (1)


    def renomeia_arquivos(self, path):

        t.sleep(2)

        if not os.path.exists(path):
            os.makedirs(path)

        arquivos = os.listdir(path)

        for arq in Path(path).rglob('*.pdf.crdownload'):
            try:
                os.remove(str(arq))
            except PermissionError:
                pass

        while len([arq for arq in arquivos if 'pdf.crdownload' in arq]) != 0:
            t.sleep(4)
            arquivos = os.listdir(path)

        for arq in enumerate(arquivos):
            if os.path.exists(path+'/'+arq[1]):

                if 'CADERNO' in arq[1]:

                    if 'crdownload' in arq[1]:
                        continue

                    nome_splited = arq[1].split('_')
                    tipo = nome_splited[3].replace('.pdf','')
                    sigla = nome_splited[2]
                    data = nome_splited[1]
                    nova_data = []

                    for d in enumerate(list(data)):
                        if d[0] is 2 or d[0] is 4:
                            nova_data.append('_'+d[1])
                        else:
                            nova_data.append(d[1])

                    data = ''.join(nova_data)
                    data = '_'.join(list(reversed(data.split('_'))))
                    nome_full = 'TRF02_' + tipo + '_' + sigla + '_' + data + '.pdf'

                    if os.path.exists(path+'/'+nome_full):
                        os.remove(path+'/'+arq[1])
                        continue
                    else:
                        self.escreve_log('Renomeando o arquivo {} para {}'.format(arq[1],nome_full))
                        os.renames(path+'//'+arq[1], path+'//'+nome_full)

        self.organiza_diarios_sem_diretorio(path)


    def organiza_diarios_sem_diretorio(self, path): # USADO PARA ORGANIZAR APENAS DIÁRIOS EM Q O PADRÃO DE NOME POSSUA ANO E MES

        lista_de_arquivos = os.listdir(path)

        pasta = path

        if len(lista_de_arquivos) == 0:
            return

        for arq in lista_de_arquivos:
            try:
                extensao = os.path.splitext(arq)[1][1:]
                ano = re.search('\d{4}',arq).group(0)
                mes = re.search('\_\d{2}\_',arq).group(0).replace('_','')
                path = '/'.join(path.split('/')[0:6])+'/'+extensao+'/'+ano+'/'+mes
                path_with_arq = path+'/'+arq

                if os.path.exists(path):
                    shutil.move(pasta+'/'+arq, path_with_arq)
                    print("Arquivo {} transferido!!!".format (arq))

                elif not os.path.exists(path_with_arq):
                    print("Criando diretório e transferindo arquivo {} para o caminho {}".format (arq, path))
                    os.makedirs(path)
                    shutil.move(pasta + '/' + arq, path_with_arq)

                else:
                    print("Transferindo arquivo {} para o caminho {}".format(arq, path))
                    shutil.move(pasta + '/' + arq, path_with_arq)

            except Exception as e:
                print(e)
                pass


    def escreve_log(self, txt):
        ConfigManager().escreve_log(txt, self.robo, self.log)

    def data_limite(self):
        return datetime.date(datetime(2009,11,1))

if __name__ == '__main__':
    robo = RoboDiarioTRF2()
    robo.download_atualizacao_diaria()
    robo.escreve_log('########### FIM ROBÔ TRF02 ###########')
