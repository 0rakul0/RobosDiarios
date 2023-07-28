# -*- coding: utf-8 -*-

from extrator.ExtratorBase import ExtratorBase
from classificadores.ClassificaEdital import ClassificaEdital
from acompanhamento_processual.AcompanhamentoProcessualMG import AcompanhamentoProcessualMG
from extrator.ProcessaExtrator import ProcessaExtrator
from bs4 import BeautifulSoup
import re

from pdjus.service.CadernoService import CadernoService

class ExtratorDJMG(ExtratorBase):
    nome_diario = "DJMG"
    def __init__(self, arquivo, acompanhamento,arquivo_bd = None):
        super(ExtratorDJMG, self).__init__("DJMG", arquivo, acompanhamento, ClassificaEdital(), arquivo_bd)

    def cria_lista_de_linhas_html(self):
        soup = BeautifulSoup(self._arquivo,"html5lib")
        linhas_tageadas = soup.find_all('p')
        linhas = []
        for p in linhas_tageadas:
            linhas.append(p.get_text())
        return iter(linhas)

    def cria_lista_de_linhas_txt(self):
        lista_expressoes_ignoradas = []

        expressao_unrtf = re.compile("###(.|\n|\t)*?-+")
        lista_expressoes_ignoradas.append(expressao_unrtf)

        separador = ''
        lista,data_caderno = self.cria_lista_de_linhas_com_separador_igual_a_linha(None, lista_expressoes_ignoradas, None, separador)
        return iter(lista), data_caderno

    def cria_lista_de_linhas(self):
        if self._arquivo.name.endswith('html'):
            return self.cria_lista_de_linhas_html(), self.pega_data_caderno_nome_arquivo()
        elif self._arquivo.name.endswith('txt'):
            return self.cria_lista_de_linhas_txt()

    def procura_processos_falencia(self,lista_de_linhas):
        expressao_numero_tjmg = re.compile('(\d{12}\-\d)',re.IGNORECASE)
        expressao_numeracao_unica = re.compile('(\d{7}\.\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})', re.IGNORECASE)
        encontrou_falencia = False
        num_processos = []
        for element in lista_de_linhas:
            if not ':' in element and not any(x.isdigit() for x in element):
                if 'FALÊNCIA' in element or 'CONVOLAÇÃO' in element or \
                                'RECUPERAÇÃO' in element or \
                                'HABILITAÇÃO DE CRÉDITO' in element or \
                                'CONCORDATA' in element or \
                                'CLASSIFICAÇÃO DE CRÉDITOS' in element or \
                                'FALIMENTAR' in element or \
                                'CONCURSO DE CREDORES' in element or \
                                'FAL?NCIA' in element or 'CONVOLA??O' in element or \
                                'RECUPERA??O' in element or \
                                'HABILITA??O DE CR?DITO' in element or \
                                'CLASSIFICA??O DE CR?DITOS' in element:
                    encontrou_falencia = True
                else:
                    encontrou_falencia = False
            elif encontrou_falencia:
                match_num_tjmg = expressao_numero_tjmg.search(element)
                if match_num_tjmg:
                    num_processos.append(match_num_tjmg.group(1))
                    next(lista_de_linhas,None)
                else:
                    match_num_unica = expressao_numeracao_unica.search(element)
                    if match_num_unica:
                        num_processos.append(match_num_unica.group(1))
        return num_processos,None

    def salva_dados(self,processos):
        pass

    def identifica_data_cabecalho(self,expressao_cabecalho,linha_atual):
        pass

    def is_edital(self):
        return 'edital' in self._arquivo.name.lower()

    def get_nome_caderno(self):
        cad = None

        res = re.search('DJMG_(.*)_[0-9]{4}_[0-9]{2}_[0-9]{2}', self._arquivo.name.upper())

        if res:
            cad = res.group(1).strip().upper()

        return cad


if __name__ == '__main__':
    p = ProcessaExtrator("DJMG", "txt", ExtratorDJMG, AcompanhamentoProcessualMG)
    p.extrai_diversos()
    # Para testar, pode ser arquivo .txt ou .html:
    # with open('C:\\Users\\b249025230\\PycharmProjects\\diario_mining\\Falencias\\dados\\MG\\DJMG\\html\\2015\\04\\DJMG_capital-j1_2015_04_08.html', mode='r') as arq:
    #     e = ExtratorDJMG(arq, None)
    #     lista_de_linhas,data = e.cria_lista_de_linhas()
    #     lista_processos,editais = e.procura_processos_falencia(lista_de_linhas)
    #     for processo in lista_processos:
    #         print(processo)