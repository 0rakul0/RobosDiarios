# -*- coding: utf-8 -*-

import http.client as httplib
import json
import traceback
from datetime import datetime, timedelta, date

import requests

from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
from util.FileManager import DiarioNaoDisponivel
from bs4 import BeautifulSoup
import re
import os
from util.StringUtil import remove_acentos, remove_varios_espacos
from util.FileManager import MaxTentativasExcedidas
import traceback
import multiprocessing


class RoboDiarioSP(RoboDiarioBase):
    def __init__(self, robo="DJSP", log="log_robo_sp.txt", erro="erro_robo_sp.txt"):
        self.__url = "https://www.dje.tjsp.jus.br/cdje/index.do"
        self.urlantigosbase = 'https://www.imprensaoficial.com.br'
        self.urlantigos = "https://www.imprensaoficial.com.br/DO/BuscaDO2001Resultado_11_3.aspx?" \
                         "filtrotipopalavraschavesalvar=FE&filtrodatafimsalvar={datajunto}&" \
                         "filtrodatainiciosalvar={datajunto}&"\
                         "filtroperiodo={data}+a+{data}&filtropalavraschave=+&" \
                         "filtrocadernossalvar={cad}&" \
                         "xhitlist_vpc={pag}"


        super(RoboDiarioSP, self).__init__(robo, log, erro)

    def juntar_pdfs(self, prefixo, data, cad, qtd_paginas, por_cad=True):
        if qtd_paginas:
            pdfs = []
            for pagina in range(1, qtd_paginas + 1):
                name = "{prefixo}_{data}_{cad}_{page:04d}.pdf".format(prefixo=prefixo,
                                                                data=data.strftime("%Y_%m_%d"), cad=cad, page=pagina)
                pdf = os.path.join(self.filemanager.caminho(name, data, True), name)

                if self.filemanager.verificar_pdf(pdf):
                    pdfs.append(pdf)

            if por_cad:
                name = "{prefixo}_{data}_{cad}.pdf".format(prefixo=prefixo, data=data.strftime("%Y_%m_%d"), cad=cad)
            else:
                name = "{prefixo}_{data}.pdf".format(prefixo=prefixo, data=data.strftime("%Y_%m_%d"))

            saida = os.path.join(self.filemanager.caminho(name, data, True), name)
            self.filemanager.juntar_pdfs(saida=saida, pdfs=pdfs, apagar_arquivos=True)
            statinfo = os.stat(saida)
            if statinfo.st_size == 0:
                os.remove(saida)


    def download_sp_antigos(self, mes=None, prefixo="DJSP", cadernos=None, fim=None, inicio=None):

        if fim:
            ultimo = fim
        else:
            ultimo = date(1970, 1, 1)

        if inicio:
            data = inicio
        else:
            data = date(1960, 1, 1)

        try:
            while ultimo >= data and self.tentativas < self.max_tentativas:
                if mes and data.month != mes:
                    data += timedelta(1)
                else:
                    conseguiu = False
                    self.tentativas = 0

                    while not conseguiu:
                        try:
                            ConfigManager().escreve_log("Acessando diário de {data}".format(data=data.strftime("%d/%m/%Y")),
                                                        self.robo, self.log)

                            if not cadernos:
                                #cadernos =  {'Judiciario_I_parte_I': 'jc0',
                                 #   'Judiciario_I_parte_II': 'jc1',
                                 #   'Judiciario_II': 'jc2',
                                 #   'Judiciario_III': 'jc3',
                                 #   #'Junta_Comercial': 'juc',
                                 #   'Suplemento': 'sup',
                                 #   'Judiciario_Editais_e_Leiloes' :'edl',
                                 #   'Empresarial :'emp' ,
                                 #   'Empresarial2' :'em2',
                                #    'Executivo :'ex0',
                                #    'Ineditoriais': 'ine',
                                #    'Suplementos': 'Sup' }
                                cadernos = {'Suplementos': 'Sup'}
                            for cad in cadernos.keys():
                                pag_busca = 1
                                s = requests.Session()

                                acabou = False

                                name = "{prefixo}_{data}_{cad}.pdf".format(prefixo=prefixo, data=data.strftime("%Y_%m_%d"), cad=cad,
                                                                           pg='')

                                html_page = s.get(self.urlantigos.format(data=data.strftime('%d/%m/%Y'),
                                                                         datajunto=data.strftime('%Y%m%d'),
                                                                         cad=cadernos[cad], pag=pag_busca),
                                                  verify=False, timeout=100)
                                soup = BeautifulSoup(html_page.text, "html5lib")

                                spn_ocorrencias = soup.find('span', {'id': 'lblDocumentosEncontrados'})

                                if spn_ocorrencias:
                                    pg_diario = int(spn_ocorrencias.get_text())
                                    paginas_busca = int(soup.find('span', {'id': 'lblDocumentosEncontrados'}).get_text()) // 15 + 1

                                    pag = 1

                                    try:
                                        while not acabou and pag_busca <= paginas_busca:
                                            for tr in soup.find_all('tr', {'class': 'tx_cinza_3'}):
                                                a = tr.find('a')

                                                tipo_sup = ''

                                                if cadernos[cad] == 'sup':
                                                    tipo_sup = remove_acentos(tr.get_text().strip().lower())
                                                    if re.match('-\s+judiciario i parte i\s+\-', tipo_sup):
                                                        tipo_sup = 'Suplemento_Judiciario_I_parte_I'
                                                    elif re.match('-\s+judiciario i parte ii\s+\-', tipo_sup):
                                                        tipo_sup = 'Suplemento_Judiciario_I_parte_II'
                                                    elif re.match('-\s+.*?editais e leiloes\s+\-', tipo_sup):
                                                        tipo_sup = 'Suplemento_Editais_e_Leiloes'
                                                    else:
                                                        a = None


                                                if a:
                                                    try:
                                                        link = a['href']
                                                    except:
                                                        pass
                                                    match = re.search('javascript\:pop\(\'(.*?)\'\,.*?\);', link, re.IGNORECASE | re.MULTILINE)

                                                    if match:
                                                        link_pag = self.urlantigosbase + match.group(1)

                                                        name_pg = "{prefixo}_{data}_{cad}_{pg:04d}.pdf".format(prefixo=prefixo, data=data.strftime("%Y_%m_%d"), cad=tipo_sup if cadernos[cad] == 'sup' else cad,
                                                                                                   pg=pag)

                                                        redirpdf = s.get(link_pag, verify=False, timeout=self.filemanager.timeout)

                                                        soup = BeautifulSoup(redirpdf.content, 'html5lib')

                                                        framepdf = soup.find('frame', {'name': 'GatewayPDF'})

                                                        if not framepdf:
                                                            acabou = True
                                                            ConfigManager().escreve_log("{} - não houve diário no dia.".format(name), self.robo,
                                                                                        self.log)
                                                        else:
                                                            linkgateway = framepdf['src']

                                                            link_pdf = self.urlantigosbase + "/DO/" + linkgateway

                                                            ConfigManager().escreve_log("Buscando {} em {}...".format(name_pg, link_pdf),
                                                                                        self.robo, self.log)

                                                            conseguiu = False

                                                            while not conseguiu:
                                                                self.filemanager.download(name_pg, data, link_pdf, False, True, 3)

                                                                arq = os.path.join(self.filemanager.caminho(name_pg, data), name_pg)

                                                                if self.filemanager.verificar_pdf(arq):
                                                                    conseguiu = True
                                                                else:
                                                                    os.remove(arq)
                                                                    self.tentativas += 1

                                                            pag += 1

                                            pag_busca += 1

                                            pag_html = -1

                                            while pag_html != pag_busca:
                                                html_page = s.get(
                                                    self.urlantigos.format(data=data.strftime('%d/%m/%Y'),
                                                                           datajunto=data.strftime('%Y%m%d'),
                                                                           cad=cadernos[cad], pag=pag_busca),
                                                    verify=False, timeout=100)
                                                soup = BeautifulSoup(html_page.text, "html5lib")
                                                spn_pag_num = soup.find('span', {'id': 'lblPagina'})

                                                if spn_pag_num:
                                                    pag_html = int(spn_pag_num.text)

                                                    if pag_busca != pag_html:
                                                        ConfigManager().escreve_log("Timeout na sessão ao buscar a "
                                                                                    "página {pag} dos resultados de "
                                                                                    "busca de "
                                                                                    "{name}".format(pag=pag_busca,
                                                                                                    name=name),
                                                                                    self.robo, self.log)
                                                        self.tentativas += 1
                                    except MaxTentativasExcedidas as mex:
                                        pass

                                    if pag > 1:
                                        if cadernos[cad] == 'sup':
                                            self.juntar_pdfs(prefixo, data, 'Suplemento_Judiciario_I_parte_I', pg_diario)
                                            self.juntar_pdfs(prefixo, data, 'Suplemento_Judiciario_I_parte_II', pg_diario)
                                            self.juntar_pdfs(prefixo, data, 'Suplemento_Editais_e_Leiloes', pg_diario)
                                        else:
                                            self.juntar_pdfs(prefixo, data, cad, pg_diario)

                                        ConfigManager().escreve_log("{} baixado.".format(name),
                                                                self.robo, self.log)
                                    else:
                                        ConfigManager().escreve_log("{} - não houve diário no dia.".format(name), self.robo,
                                                                    self.log)
                                else:
                                    ConfigManager().escreve_log("{} - não houve diário no dia.".format(name), self.robo,
                                            self.log)

                            conseguiu = True
                            data += timedelta(1)
                        except Exception as e:
                            ConfigManager().escreve_log("Erro ao baixar o diário: " + traceback.format_exc(), self.robo, self.erro)
                            self.tentativas += 1

        except MaxTentativasExcedidas as me:
            ConfigManager().escreve_log("Máximo de tentativas de download excedidas. Parando.", self.robo, self.log)

    def download_atualizacao_diaria(self):
        ConfigManager().escreve_log("Acessando {}".format(self.__url), self.robo, self.log)

        atual = datetime.now().date()

        for num_caderno in (11, 12, 13, 14, 15, 18):
            data = self.data_inicial("DJSP_Caderno{}".format(num_caderno))
            while atual >= data:
                conseguiu = False
                self.tentativas = 0

                while not conseguiu:
                    try:
                        name\
                            = "DJSP_Caderno{caderno}_{ano}_{mes:02d}_{dia:02d}.pdf". \
                                format(caderno=num_caderno, ano=data.year, mes=data.month, dia=data.day)

                        pagina_download = "https://www.dje.tjsp.jus.br/cdje/downloadCaderno.do?dtDiario={data}&cdCaderno={caderno}". \
                            format(data=data.strftime("%d/%m/%Y"), caderno=num_caderno)

                        pdf = requests.get(pagina_download, verify=False, timeout=self.filemanager.timeout)

                        if "text/html" in pdf.headers['content-type']:
                            ConfigManager().escreve_log("{} - não houve diário no dia.".format(name), self.robo, self.log)
                        elif "application/octet-stream" in pdf.headers['content-type']:
                            ConfigManager().escreve_log("Buscando {} em {}...".format(name, pagina_download), self.robo, self.log)
                            self.filemanager.download(name, data, pagina_download, False, True, 3)
                        conseguiu = True
                    except (DiarioNaoDisponivel, FileNotFoundError) as e:
                        ConfigManager().escreve_log("Diario não disponível na data {data}".format(
                            data=data.strftime("%d/%m/%Y")), self.robo, self.log)
                        conseguiu = True
                    except Exception as e:
                        ConfigManager().escreve_log("Erro: " + str(e), self.robo, self.erro)
                        self.tentativas += 1

                data += timedelta(1)

    #86 - 107
    def download_edicoes_por_pagina(self, num_inicial, num_final):
        ConfigManager().escreve_log("Acessando {}".format(self.__url), self.robo, self.log)

        atual = num_inicial

        while atual <= num_final:
            for num_caderno in (11, 12, 13, 14, 15, 18):

                conseguiu = False
                self.tentativas = 0

                while not conseguiu:
                    pdf_pags = []

                    pagina_busca = "https://www.dje.tjsp.jus.br/cdje/cabecalho.do?cdVolume=1&nuDiario={num}" \
                                   "&cdCaderno={caderno}&nuSeqpagina=1".format(num=str(atual), caderno=num_caderno)
                    res = requests.get(pagina_busca, verify=False, timeout=self.filemanager.timeout)

                    soup = BeautifulSoup(res.content)

                    data = datetime.strptime(soup.find_all('input', {'class', 'box disabled'})[0].attrs['value'], '%Y-%m-%d')

                    pagina_count = "https://www.dje.tjsp.jus.br/cdje/getListaDeSecoes.do?cdVolume=1&nuDiario={num}" \
                                   "&cdCaderno={caderno}".format(num=str(atual), caderno=num_caderno)
                    json_pags = requests.get(pagina_count, verify=False, timeout=self.filemanager.timeout)
                    num_pags = int(re.search('\[([0-9]+)\,\[', json_pags.content.decode('utf-8').strip()).group(1))

                    nome = "DJSP_Caderno{caderno}_{ano}_{mes:02d}_{dia:02d}.pdf". \
                                    format(caderno=num_caderno, ano=data.year, mes=data.month, dia=data.day)
                    final = os.path.join(self.filemanager.caminho(nome, data, True), nome)

                    if os.path.exists(final):
                        conseguiu = True
                        ConfigManager().escreve_log("{} - já baixado.".format(nome), self.robo, self.log)
                    else:
                        try:
                            for pag in range(1,num_pags+1):
                                name\
                                    = "DJSP_Caderno{caderno}_{ano}_{mes:02d}_{dia:02d}_{pag:06d}.pdf". \
                                        format(caderno=num_caderno, ano=data.year, mes=data.month, dia=data.day, pag=pag)

                                pagina_download = "https://www.dje.tjsp.jus.br/cdje/getPaginaDoDiario.do?cdVolume=1&nuDiario=" \
                                                  "{num}&cdCaderno={caderno}&nuSeqpagina={pag}". \
                                    format(num=str(atual), caderno=str(num_caderno), pag=pag)

                                pdf = requests.get(pagina_download, verify=False, timeout=self.filemanager.timeout)

                                if "text/html" in pdf.headers['content-type']:
                                    ConfigManager().escreve_log("{} - não houve diário no dia.".format(name), self.robo, self.log)
                                elif "application/pdf" in pdf.headers['content-type']:
                                    ConfigManager().escreve_log("Buscando {} em {}...".format(name, pagina_download), self.robo, self.log)
                                    self.filemanager.download(name, data, pagina_download, False, True, 3)
                                    pag_i = os.path.join(self.filemanager.caminho(name, data, True), name)
                                    pdf_pags.append(pag_i)

                            self.filemanager.juntar_pdfs(final, pdf_pags, apagar_arquivos=True)

                            conseguiu = True
                        except (DiarioNaoDisponivel, FileNotFoundError) as e:
                            ConfigManager().escreve_log("Diario {cad} - {num} não disponível.".format(
                                cad=str(num_caderno), num=str(atual)), self.robo, self.log)
                            conseguiu = True
                        except Exception as e:
                            ConfigManager().escreve_log("Erro: " + str(e), self.robo, self.erro)
                            self.tentativas += 1

            atual += 1

    def data_limite(self):
        return date(2023, 7, 20)

def _baixa_antigos_por_mes(mes):
    print("Processo para o mês" + mes)

    robo = RoboDiarioSP()
    robo.download_sp_antigos(int(mes))


if __name__ == '__main__':
    robo = RoboDiarioSP()
    robo.download_atualizacao_diaria()
    #robo.download_sp_antigos(inicio=date(2007,10,1), fim=date(2007,11,6))
    #robo.download_edicoes_por_pagina(86, 107)
    '''
    pool = multiprocessing.Pool(12)

    jobs = []

    partes = ["1","2","3","4","5","6","7","8","9","10","11","12"] #["1","2","3","4","5","6","7","8","9","10","11","12"]

    for parte in partes:
        jobs.append((parte))

    res = pool.map(_baixa_antigos_por_mes,jobs)
    '''

