from datetime import datetime, timedelta, date
import os,re
import requests
from urllib.request import urlopen, urlretrieve
from urllib.error import HTTPError, URLError
# from requests.packages.urllib3.exceptions import ReadTimeoutError
from bs4 import BeautifulSoup
from robosdiarios.RoboDiarioSP import RoboDiarioSP
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util import DateUtil
from util.ConfigManager import ConfigManager
from util.FileManager import MaxTentativasExcedidas
from util.FileManager import DiarioNaoDisponivel
from pathlib import Path
import csv

class RoboDiarioJUCESP(RoboDiarioSP):

    def __init__(self):
        # self.urldiario = "http://diariooficial.imprensaoficial.com.br/doflash/prototipo/{ano}/{mes}/{dia:02d}/jucesp/" \
        #                  "pdf/pg_{page:04d}.pdf"
        self.urldiario = "https://www.imprensaoficial.com.br/DO/BuscaDO2001Resultado_11_3.aspx?filtrotipopalavraschavesalvar=FE&filtrodatafimsalvar={data}&filtroperiodo={dia:02d}%2f{mes:02d}%2f{ano}+a+{dia:02d}%2f{mes:02d}%2f{ano}&filtrocadernos=Junta+Comercial&filtropalavraschave=+&filtrodatainiciosalvar={data}&xhitlist_vpc={pag:01d}&filtrocadernossalvar=juc"
        self.path_inicial = 'http://www.imprensaoficial.com.br/PortalIO/DO/'
        self.pagina_atual = 1
        self.s = requests.session()
        super(RoboDiarioJUCESP, self).__init__("JUCESP", "log_robo_jucesp.txt", "erro_robo_jucesp.txt")


    def get_pagina_2017(self, data, pagina):
        exprLinks = re.compile ("(\/DO\/BuscaDO.*pdf.*)", re.MULTILINE)

        html = self.s.get(self.urldiario.format(ano=data.year,mes=data.month,dia=data.day,data=str(data).replace('-',''),pag=pagina), verify=False, timeout=100)
        soup = BeautifulSoup (html.text, "html5lib")
        href_tags = soup.find_all('a',{'class':'bg-light text-dark'})
        try:
            for tag in href_tags:
                name = "JUCESP_{data}_{pagina:04d}.pdf".format (data=data.strftime("%Y_%m_%d"),pagina=self.pagina_atual)
                match = exprLinks.search(str(tag))
                nome_arquivo_final = 'JUCESP_{data}.pdf'.format(data=data.strftime("%Y_%m_%d"))
                if match:
                    if self.filemanager.ja_baixado (nome_arquivo_final, data, True):
                        print('Arquivo'+ nome_arquivo_final +'já baixado!!!')
                        self.pagina_atual += 1
                        return False
                    else:
                        link = match.group(0)
                        link = "http://www.imprensaoficial.com.br" + link.replace ('amp;','')
                        html_view = self.s.get (link, verify=False, timeout=100)
                        soup_view = BeautifulSoup (html_view.text, "html5lib")
                        frame = soup_view.find ('iframe', {'name': 'GatewayPDF'})
                        src = frame['src']
                        link = self.path_inicial+src
                        self.filemanager.download (name, data, link, tentativas=20)
                        self.pagina_atual += 1
            if not href_tags:
                return False
            return True
        except TypeError as e:
            print("DEU MERDA AQUI JUREGUE!!!!")

    def get_pagina(self, data, pagina):

        try:
            name = "JUCESP_{data}_{page:04d}.pdf".format(data=data.strftime("%Y_%m_%d"), page=pagina)

            self.filemanager.download(name, data, self.urldiario.format(ano=data.year,
                                                                        mes=DateUtil.parse_mes_por_extenso(data.month),
                                                         dia=data.day, page=pagina))
            return True
        except MaxTentativasExcedidas as e:
            if "404" in str(e): # Este diario baixa até não ter mais páginas e dar erro 404
                return False
            raise e
        except (DiarioNaoDisponivel, FileNotFoundError) as e:
            return False

    def lista_nome_tamanho_arquivos_na_pasta(self, caminho):
        pasta = Path('C:\\Users\\e7609043\\PycharmProjects\\IpeaJUS\\dados\\SP\\JUCESP\\pdf')

        with open (caminho+'\\tabela_nome_tamanho_JUCESP.csv', 'w') as csvfile:
            for f in pasta.glob ('**/*'):
                if f.is_file():
                    escrevelinha = csv.writer (csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                    escrevelinha.writerow([f.name, f.stat().st_size])

    def get_todas_paginas(self, data):
        achouPagina = True
        pagina = 1
        while achouPagina:
            achouPagina = self.get_pagina_2017(data, pagina)
            pagina += 1

        return self.pagina_atual -1 # usado para o método get_pagina_2017
        # return pagina-2 if pagina > 2 else 0 # usado para o método get_pagina

    def juntar_pdfs_jucesp(self, data, name, qtd_paginas):
        prefixo = "JUCESP"

        if qtd_paginas:
            pdfs = []
            for pagina in range(1, qtd_paginas + 1):
                name = "{prefixo}_{data}_{page:04d}.pdf".format(prefixo=prefixo,
                                                                data=data.strftime("%Y_%m_%d"), page=pagina)
                pdf = os.path.join(self.filemanager.caminho(name, data, True), name)
                pdfs.append(pdf)

            name = "{prefixo}_{data}.pdf".format(prefixo=prefixo, data=data.strftime("%Y_%m_%d"))
            saida = os.path.join(self.filemanager.caminho(name,data,  True), name)
            self.filemanager.juntar_pdfs(saida=saida, pdfs=pdfs, apagar_arquivos=True)
            statinfo = os.stat(saida)
            if statinfo.st_size == 0:
                os.remove(saida)

    def juntar_pdfs(self, prefixo, data, cad, qtd_paginas, por_cad=True):
        super(RoboDiarioJUCESP, self).juntar_pdfs(prefixo, data, cad, qtd_paginas, por_cad=False)

    def download_atualizacao_diaria(self):
        atual = datetime.now().date()

        data = self.data_inicial("JUCESP") # data do último diário baixado
        tentativas = 3
        # data = self.data_limite() # usado para baixar apartir da data limite
        #data = date(2017,8,1)

        while atual >= data:
            while tentativas > 0:
                try:
                    ConfigManager().escreve_log("Acessando diário de {data}".format(data=data.strftime("%d/%m/%Y")),
                                            self.robo, self.log)
                    name = "JUCESP_{data}.pdf".format(data=data.strftime("%Y_%m_%d"))
                    qtd_paginas = self.get_todas_paginas(data)

                    if qtd_paginas <= 1:
                        self.pagina_atual = 1
                    elif qtd_paginas == 0:
                        ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                            data=data.strftime("%d/%m/%Y")), self.robo, self.log)
                    else:
                        self.juntar_pdfs_jucesp(data, name, qtd_paginas)
                        self.pagina_atual = 1

                    tentativas = 0

                except (DiarioNaoDisponivel, FileNotFoundError) as e:
                    ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                        data=data.strftime("%d/%m/%Y")), self.robo, self.log)

                except Exception:
                    tentativas -= 1

            data += timedelta(1)
            tentativas = 3

    def download_diarios_antigos(self):
        self.download_sp_antigos(prefixo="JUCESP", cadernos={'Junta_Comercial': 'juc', 'Boletim_JUCESP': 'bjc'},
                                 fim=date(2023, 7, 25), inicio=self.data_limite())

    def data_limite(self):
        return date(2023, 7, 20)

if __name__ == '__main__':
    robo = RoboDiarioJUCESP()
    # robo.lista_nome_tamanho_arquivos_na_pasta('C:\\Users\\e7609043\\PycharmProjects\\IpeaJUS\\dados\\SP\\JUCESP')
    robo.download_atualizacao_diaria()
    # robo.download_diarios_antigos()
