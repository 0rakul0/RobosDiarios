# -*- coding: utf-8 -*-

import re

from acompanhamento_processual.AcompanhamentoProcessualDJSP import AcompanhamentoProcessualDJSP
from extrator.ProcessaExtrator import ProcessaExtrator
from extrator.ExtratorBase import ExtratorBase
from classificadores.ClassificaEdital import ClassificaEdital


class ExtratorTRTSP(ExtratorBase):
    nome_diario = "TRTSP"

    def __init__(self, arquivo, acompanhamento,arquivo_bd = None):
        super(ExtratorTRTSP, self).__init__("TRTSP", arquivo, acompanhamento, ClassificaEdital(), arquivo_bd)

    def cria_lista_de_linhas(self):
        expressao_cabecalho = re.compile('(São *Paulo, *)(\d* *de *[A-Za-zçÇ]* *de *\d*)', re.IGNORECASE)
        lista_expressoes_ignoradas = []

        expressao_diario = re.compile('DOeletrônico *\- *Tribunal *Regional *do *Trabalho *\- *\d* *. *Região',re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_diario)

        expressao_edicao = re.compile('E *d *i *ç *ã *o *n *. *\d*')
        lista_expressoes_ignoradas.append(expressao_edicao)


        separador = ''
        return super(ExtratorTRTSP, self).cria_lista_de_linhas_com_separador_igual_a_linha(expressao_cabecalho, lista_expressoes_ignoradas, None, separador)
#ele não é um edital, mas funciona como, pois a busca serve apenas para achar cnpj
    def is_edital(self):
        return True

    def salva_dados(self,processos):
        pass

    def identifica_data_cabecalho(self,expressao_cabecalho,linha_atual):
        pass
    def procura_processos_falencia(self,lista_de_linhas):
        return None

        # regex_cnpj = re.compile('C *N *P *J.*[\D^]\d{2}[\. ]*\d{3}[\. ]*\d{3}[\/ ]*\d{4}[\- ]*\d{2}\D')

    def get_caderno(self):
        return "PAGINAS SEM CADERNO"


if __name__ == '__main__':
    p = ProcessaExtrator("TRTSP", "txt", ExtratorTRTSP, AcompanhamentoProcessualDJSP)
    p.extrai_diversos()
