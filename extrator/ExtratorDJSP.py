# -*- coding: utf-8 -*-
import datetime
import sys

from classificadores.ClassificaQuadroCredores import ClassificaQuadroCredores
from functools import reduce

from pdjus.modelo.Distribuicao import Distribuicao
from pdjus.service.ArquivoService import ArquivoService
from pdjus.service.DistribuicaoService import DistribuicaoService
from pdjus.service.ProcessoService import ProcessoService
import re
import json
import sys
import requests
from pdjus.service.TipoParteService import TipoParteService
from acompanhamento_processual.AcompanhamentoProcessualDJSPselenium import AcompanhamentoProcessualDJSPselenium
from extrator.ProcessaExtrator import ProcessaExtrator
from extrator.ExtratorBase import ExtratorBase
from classificadores.ClassificaEdital import ClassificaEdital
from util.FalenciaUtil import verifica_texto_decretacao_falencia
from util.StringUtil import remove_acentos, remove_caracteres_csv, remove_varios_espacos, remove_quebras_linha_de_linha
import os
from pdjus.service.DiarioService import DiarioService
from pdjus.service.CadernoService import CadernoService
from util.ConfigManager import ConfigManager

class ExtratorDJSP(ExtratorBase):
    nome_diario = "DJSP"

    def __init__(self, arquivo, acompanhamento,arquivo_bd = None):
        super(ExtratorDJSP, self).__init__("DJSP", arquivo, acompanhamento,
                                           ClassificaEdital(), arquivo_bd)
        self.arquivo_service = ArquivoService()
        self.acompanhamentoDJSPSelenium = AcompanhamentoProcessualDJSPselenium()
        self.distribuicao_service = DistribuicaoService()
        self.tipo_parte_service = TipoParteService()

        self.regex_npu = re.compile('\d{7}\-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4}', re.MULTILINE)
        self.regex_n_antigo = re.compile('(\d{6,7}\-?\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})|'
                                         '(\d{3}\.\d{2}\.\d{4}\.\d{6}(\-\d\/\d{6}\-\d{3})?)|'
                                         '(\d{3}\.\d{2,4}\.\d{6}\-?\d?)', re.MULTILINE)

        self.regex_cabecalho_pag = re.compile('((\s+PUBLICA[CÇ][AÃ]O\s+.{1,20}\s+TRIBUNAL\s+DE\s+JUSTI[CÇ]A\s+DO\s+ESTADO\s+DE.*?\s+DISPONIBILIZA[CÇ][AÃ]O\:.*?\s+)|(.*((\-FEIRA)|(SAB.DO)|(DOMINGO)).*\s*.*S.O\sPAULO.*\s*[0-9]*\s*))?DI[AÁ]RIO\s+((DA\s+JUSTI[CÇ]A\s+ELETR[ÔO]NICO.*\s+S[AÃ]O\s+PAULO.*\s+EDI[CÇ][AÃ]O\s+[0-9]*\s+[0-9]*\s+)|(OFI[ ]?CIAL\s+PODER.*\n.*.*\s+)((EDI[CÇ][AÃ]O\s+[0-9]*\s+[0-9]*\s+)|([0-9]*\s*.*S.O\sPAULO.*\))?))')

        tipo_partes_regex = reduce(lambda x, y: x+ '|' + y ,[x.nome for x in self.tipo_parte_service.dao.listar()])
        tipo_partes_regex = tipo_partes_regex.replace("\\","\\\\").replace(".","\\.").replace("/","\\/").replace("-","\\-").replace("(","\\(").replace(")","\\)")
        self.partes_regex = '(' + tipo_partes_regex + '|AUTOR|SUSCITANTE|REPTE|EMBARGTE|ORDNTE|OPOENTE|EXQTE|RECTE|REQTE|DEPCTE|EXPTE|LITISAT|ASSISTA|PROCUR|IMPDO|EXPTE|IMPTE|EMBTE|INDCDO|EXCDO|REQDO|PACIENTE|PERITO|EXEQTE|REQDO|RELATOR(?:\(A\))?)$'

        self.jTR = '826'
        self.__erro_indice = "erro_extrator_indices.txt"



    def cria_lista_de_linhas(self):
        if self.is_antigo():
            return self.cria_lista_de_linhas_diarios_antigos()
        elif self.is_primeira_instancia():
            return self.cria_lista_de_linhas_primeira_instancia()
        elif self.is_edital():
            return self.cria_lista_de_linhas_editais()
        else:
            return None,None


    def procura_processos_falencia(self, lista_de_linhas):
        if self.is_antigo():
            return self.procura_processos_falencia_antigos(lista_de_linhas),None
        if self.is_primeira_instancia():
            return self.procura_processos_falencia_primeira_instancia(lista_de_linhas),None
        if self.is_edital() or self.is_edital_antigo():
            return self.procura_processos_falencia_edital(lista_de_linhas)

    def procura_processos_falencia_edital(self, lista_de_linhas):
        processo_service = ProcessoService()
        validaQuadro = ClassificaQuadroCredores(tag="FALENCIAS")

        #Aconselho a colocar algum marcador antes do texto e aí modificar o group no match_num. Marcador sugerido: Proc. nº|Processo nº...
        #COLOCADO, regex sem marcador comentado!
        # regex_num_proc = re.compile('(\d{7} *\-? *\d{2} *\. *\d{4} *\. *\d *\. *\d{2} *\. *\d{4})|(\d{3} *\. *\d{2} *\. *\d{4} *\. *\d{3} *\.? *\d{3}( *\- *\d *\/ *\d{6} *\- *\d{3}| *\- *\d)?)|(\d{3} *\. *\d{2} *\. *\d{3} *\.? *\d{3} *\- *\d)|(\d{2} *\. *\d{3} *\.? *\d{3} *\- *\d)|(\d{3} *\. *\d{3} *\. *\d{3} *\- *\d{2})')
        regex_num_proc = re.compile('PROC(\.|ESSO)?\s*.{0,50}?(N.?)?\s*((\d{7} *\-? *\d{2} *\. *\d{4} *\. *\d *\. *\d{2} *\. *\d{4})|(\d{3} *\. *\d{2} *\. *\d{4} *\. *\d{3} *\.? *\d{3}( *\- *\d *\/ *\d{6} *\- *\d{3}| *\- *\d)?)|(\d{3} *\. *\d{2} *\. *\d{3} *\.? *\d{3} *\- *\d)|(\d{2} *\. *\d{3} *\.? *\d{3} *\- *\d)|(\d{3} *\. *\d{3} *\. *\d{3} *\- *\d{2}))|(\\b\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\\b)')

        processos = []
        map_editais = {}

        for item in lista_de_linhas:
            item = item.upper()
            encontrou,processo = verifica_texto_decretacao_falencia(item)
            if encontrou:
                if processo:
                    processos.append(processo)
                    if processo in list(map_editais.keys()):
                        map_editais[processo].append(item)
                    else:
                        map_editais.update({processo: [item]})

            match_num = list(regex_num_proc.finditer(item))
            if len(match_num) > 0 and validaQuadro.verifica_possibilidade_de_quadro(item):
                npus = []
                #list((set([p.group(3) for p in match_num])))
                for num in match_num:
                    if num.group(3) and num.group(3) not in npus:
                        npus.append(num.group(3))
                    elif num.group(10) and num.group(10) not in npus:
                        npus.append(num.group(10))
                # indice_npus = 0

                processos_objs = self.acompanhamentoDJSPSelenium.bate_lista_processos(npus=npus, tag="FALENCIAS", usuario='01105013731',
                                                                      senha='Ruthemi123!', baixa_arvore=True, retorna_processos=True,
                                                                      verifica_minio=True, salva_arvore_por_arvore=True,
                                                                      bucket='extrator-djsp')

                # while npus and indice_npus < len(npus):
                    # num_proc = npus[indice_npus]
                    # num_proc = match.group(3)
                    # processo = processo_service.preenche_processo(npu=num_proc)

                    # if not processo:
                    #     print(num_proc)
                    #     processo = self._acompanhamento.gera_arvore_processos(num_proc, 'FALENCIAS', True, self.get_caderno())

                for processo in processos_objs:
                    if processo and processo.is_processo_falencia_recuperacao_convolacao():
                        validaQuadro.verifica_quadro_credores_no_diario(item, self.data_caderno, processo,caderno=self.get_caderno(), fonte_dado='DJSP')
                        break
                    else:
                        if not processo:
                            print('Processo não encontrado')
                        else:
                            if processo.npu_ou_num_processo and processo.classe_processual:
                                print('Processo {} da classe {} não é de Falência, então o quadro não é dele.'.format(processo.npu_ou_num_processo,processo.classe_processual.nome))
                            else:
                                print('Processo buscado possui erro.')
                #     indice_npus+=1
                # if indice_npus >= len(npus):
                #     print('Não foi possível identificar o processo ao qual o quadro pertence.')


        return processos,map_editais

    def procura_processos_falencia_primeira_instancia(self, lista_de_linhas):
        expressao_npu_numero_proc = re.compile('(\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})|(\d{3}\.\d{2}\.\d{4}\.\d{6}(\-\d\/\d{6}\-\d{3})?)|(\d{3}\.\d{2}\.\d{6}\-\d)')
        expressao_processo = re.compile('(((Pedido *de)? *(Auto)? *(fa[\- ]*l[Êê]n[\- ]*c[\- ]*ia))|(Recupera[Çç][Ãã]o *Judicial)) *((-) *| *(de *Empres[Áá]rios *, *So))',re.IGNORECASE)
        # expressao_processo_novo = re.compile('(\d{7} *\-\d{2} *\.\d{4} *\.\d *\.\d{2} *\.\d{4}) *((\(\d{3} *\.\d{2} *\.\d{4} *\.\d{6}\))|(\(p *r *o *c *e *s *s *o *p *r *i *n *c *i *p *a *l.*)) *\- *(F *a *l *[Êê] *n *c *i *a) *d *e *E *m *p *r *e *s *[Áá] *r *i *o *s *, *S *o *c',re.IGNORECASE)
        expressao_processo_recuperacao_novo = re.compile("Recupera[Çç][Ãã]o judicial",re.IGNORECASE)
        expressao_falencia = re.compile('(AUTO-?|PEDIDO\s+D?E?\s*)?FAL[ÊE]NCIA|INSOLV[ÊE]NCIA\s+REQUERIDA\s+PELO\s+CREDOR',re.IGNORECASE)
        expressao_convolacao = re.compile('Convola[cçCÇ][ãaAÃ]o',re.IGNORECASE)
        expressao_rec_jud = re.compile('rec\.?(upera[cçCÇ][ãaAÃ]o)?\s*(jud\.?(icial)?)',re.IGNORECASE)
        expressao_decl_creditos = re.compile('DECLARA[ÇC][ÃA]O\s+DE\s+CR[ÉE]DITO',re.IGNORECASE)
        processos_encontrados = []
        for item in lista_de_linhas:
            npu_num_proc = expressao_npu_numero_proc.search(item)
            processo_match = expressao_processo.search(item)
            if npu_num_proc:
                if processo_match:
                    processos_encontrados.append(npu_num_proc.group(0))
                    print(npu_num_proc.group(0) + " - " + processo_match.group(0))
                    print(60*'*')
                else:
                    processo_recuperacao_match = expressao_processo_recuperacao_novo.search(item)
                    if processo_recuperacao_match:
                        processos_encontrados.append(npu_num_proc.group(0))
                        print((npu_num_proc.group(0) + " - " + processo_recuperacao_match.group(0)))
                        print(60*'*')
                    else:
                        falencia_match = expressao_falencia.search(item)
                        if falencia_match:
                            processos_encontrados.append(npu_num_proc.group(0))
                            print((npu_num_proc.group(0) + " - " + falencia_match.group(0)))
                            print(60*'*')
                        else:
                            convolacao_match = expressao_convolacao.search(item)
                            if convolacao_match:
                                processos_encontrados.append(npu_num_proc.group(0))
                                print((npu_num_proc.group(0) + " - " + convolacao_match.group(0)))
                                print(60*'*')
                            else:
                                rec_jud_match = expressao_rec_jud.search(item)
                                if rec_jud_match:
                                    processos_encontrados.append(npu_num_proc.group(0))
                                    print((npu_num_proc.group(0) + " - " + rec_jud_match.group(0)))
                                    print(60*'*')
                                else:
                                    decl_creditos_match = expressao_decl_creditos.search(item)
                                    if decl_creditos_match:
                                        processos_encontrados.append(npu_num_proc.group(0))
                                        print((npu_num_proc.group(0) + " - " + decl_creditos_match.group(0)))
                                        print(60*'*')


        print(("Foram encontrados "+str(len(processos_encontrados)) + " processos do nosso interesse."))
        return processos_encontrados

    def procura_processos_falencia_antigos(self, lista_de_linhas):
        if self.pega_data_caderno_nome_arquivo() and int(self.pega_data_caderno_nome_arquivo()[:4]) >= 2006:
            expressao_processo = re.compile('(^|\D)(\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{3}\.\d{2}\.\d{4}\.\d{6}\-\d(\/?\d{6}\-?\d{3})?|(\d{3}\.)?\d{2}\.\d{5,6}\-\d)($|\D|\\b)')
        else:
            expressao_processo = re.compile('(^|\D)(\d{7}\-\d{2}\.\d{4}\.?\d\.\d{2}\.\d{4}|\d{3}\.\d{2}\.\d{4}\.\d{6}\-\d(\/?\d{6}\-?\d{3})?|(\d{3}\.)?\d{2}\.\d{5,6}\-\d|\d{3,4}\/\d{2,4})($|\D|\\b)')


        expressao_falencia = re.compile('(AUTO-?|PEDIDO\s+D?E?\s*)?FAL[ÊE]NCIA|INSOLV[ÊE]NCIA\s+REQUERIDA\s+PELO\s+CREDOR',re.IGNORECASE)
        expressao_convolacao = re.compile('Convola[cçCÇ][ãaAÃ]o',re.IGNORECASE)
        expressao_rec_jud = re.compile('rec\.?(upera[cçCÇ][ãaAÃ]o)?\s*(jud\.?(icial)?)',re.IGNORECASE)
        expressao_decl_creditos = re.compile('DECLARA[ÇC][ÃA]O\s+DE\s+CR[ÉE]DITO',re.IGNORECASE)
        cont_fal = 0
        cont_conv = 0
        cont_recjud = 0
        cont_creditos = 0
        cont_texto_corrido = 0

        processos_encontrados = []
        for item in lista_de_linhas:
            processo_match = expressao_processo.search(item)
            if processo_match:
                falencia_match = expressao_falencia.search(item)
                if falencia_match:
                    processos_encontrados.append(processo_match.group(2))
                    cont_fal +=1
                else:
                    convolacao_match = expressao_convolacao.search(item)
                    if convolacao_match:
                        processos_encontrados.append(processo_match.group(2))
                        cont_conv +=1
                    else:
                        rec_jud_match = expressao_rec_jud.search(item)
                        if rec_jud_match:
                            processos_encontrados.append(processo_match.group(2))
                            cont_recjud +=1
                            print (item)
                        else:
                            decl_creditos_match = expressao_decl_creditos.search(item)
                            if decl_creditos_match:
                                cont_creditos+=1
                                processos_encontrados.append(processo_match.group(2))
                            elif 'concordata' in item.lower() or 'credor' in item.lower()  or 'falido' in item.lower() or 'falimentar' in item.lower()  or 'falencia' in remove_acentos(item.lower()):
                                processos_encontrados.append(processo_match.group(2))
                                cont_texto_corrido+=1

        return processos_encontrados

    def cria_lista_de_linhas_editais(self):
        # expressao_cabecalho = re.compile('(Disponibilização: *\w{0,8}-feira, *)(\d{1,2} *de *.{4,9} *de *\d{4})',re.IGNORECASE)
        lista_expressoes_ignoradas = []

        expressao_diario = re.compile('Diário.{0,100}- *Caderno *Judicial *- *1\W *',re.IGNORECASE)

        lista_expressoes_ignoradas.append(expressao_diario)

        expressao_caderno = re.compile('caderno *\d{1,2}', re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_caderno)

        expressao_site = re.compile('www.dje.tjsp.jus.br', re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_site)

        expressao_edicao = re.compile('S[Ãã]o *Paulo, *Ano \w* *- *Edi[Çç][Ãã]o \d*', re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_edicao)

        expressao_rodape = re.compile('F *e *d *e *r *a *l.{0,100}1 *1 *\. *4 *1 *9 *\/0 *6 *, *a *r *t *\. *4',re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_rodape)

        lista_expressoes_ignoradas.append(re.compile('PUBLICA[ÇC][AÃ]O\s*OFICIAL\s*DO\s*TRIBUNAL\s*DE\s*JUSTI[ÇC]A.{0,50}LEI\s*FEDERAL[\s\,]*(N[Oº].{0,30})?ART\.\s*[0-9]+.?', re.IGNORECASE))
        lista_expressoes_ignoradas.append(re.compile('DI[ÁA]RIO\sD[AE]\sJUSTICA\sELETR[ÔO]NICO\s\-\sCADERNO\sEDITAIS\sE\sLEIL[ÕO]ES', re.IGNORECASE))
        lista_expressoes_ignoradas.append(re.compile('CADERNO(\sDE)?\s+EDITAIS\s+E\s+LEILOES', re.IGNORECASE))
        lista_expressoes_ignoradas.append(re.compile('ANO.{0,}.EDICAO\s[0-9][0-9][0-9][0-9]\s..{0,15}\s?[,]\s?([0-9][0-9])\s?DE\s?.{0,10}\sDE\s[0-9][0-9][0-9][0-9]', re.IGNORECASE))
        lista_expressoes_ignoradas.append(re.compile('DIARIO\sOFICIAL\sPODER\sJUDICIARIO\s.\sCADERNO\sDE\sED\w*', re.IGNORECASE))
        lista_expressoes_ignoradas.append(
            re.compile('\s*DI[AÁ]RIO OFICIAL PODER JUDICI[AÁ]RIO – CADERNO DE EDITAIS E LEIL[OÕ]ES\s*'))
        lista_expressoes_ignoradas.append(re.compile(
            '\s*(JU[ÍI]ZA? DE DIREITO DA )?\d+. VARA CÍVEL D[OAE](STA)? (FORO|COMARCA)?( DE )? ?.+?(,|SP|\.|;)'))
        lista_expressoes_ignoradas.append(re.compile('VALORES\s*EXPRESSOS\s*EM\s*CR\$', re.IGNORECASE))
        lista_expressoes_ignoradas.append(re.compile('\\b\w{5} *\. *\d{3}\\b\s*\n', re.IGNORECASE))

        separador = '(?:SER[ÁáA]? *)?(?:PUBLICADO *(?:[Ee] *)?|AFI ?XADO *(?:[Ee] *)?){1,2}\s*.{0,27}?\s*(?:NA\s+FORMA\s+DA\s+LEI|(NO|EM) *(?:LOCAL|LUGAR) *(PUBLICO E )?DE *COSTUME)\.? *|(?:AFIXADO *E *PUBLICADO)|S[ãÃaA]O *PAULO *, *\d{1,2}\s*DE\s[A-ZÇç]+\s*DE\s*\d{4}\.?|(?:S[ãÃAa]O\s*PAULO|S[\.\s]?P[\.\s]?|SANTOS)[,\s]+\d{1,2}\s*DE\s*[A-Za-zçÇ]+\s*(DE\s*)?\d{4}.|(?:S[ãÃAa]O\s*PAULO|S[\.\s]?P[\.\s]?|SANTOS)[,\s]+\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\.|PRAZO\sDE.{0,20}DIAS,?\s*(NA\s+FORMA\s+DA\s+LEI|NO *(LOCAL|LUGAR) *DE *COSTUME)|\\b[0-9][A-Z]{4}\.[0-9]{3}\\b|\\b(PRIC|PRI)\\b'
        return super(ExtratorDJSP, self).cria_lista_de_linhas_removendo_separador(lista_expressoes_ignoradas, separador)
        # separador = '(?:SER[ÁáA]? *)?(?:PUBLICADO *(?:[Ee] *)?|AFI ?XADO *(?:[Ee] *)?){1,2}\s*.{0,27}?\s*(?:NA\s+FORMA\s+DA\s+LEI|(NO|EM) *(?:LOCAL|LUGAR) *(PUBLICO E )?DE *COSTUME)\.? *|(?:AFIXADO *E *PUBLICADO)|S[ãÃaA]O *PAULO *, *\d{1,2}\s*DE\s[A-ZÇç]+\s*DE\s*\d{4}\.?|(?:S[ãÃAa]O\s*PAULO|S[\.\s]?P[\.\s]?|SANTOS)[,\s]+\d{1,2}\s*DE\s*[A-Za-zçÇ]+\s*(DE\s*)?\d{4}.|(?:S[ãÃAa]O\s*PAULO|S[\.\s]?P[\.\s]?|SANTOS)[,\s]+\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\.|PRAZO\sDE.{0,20}DIAS,?\s*(NA\s+FORMA\s+DA\s+LEI|NO *(LOCAL|LUGAR) *DE *COSTUME)|\\b[0-9][A-Z]{4}\.[0-9]{3}\\b|\\b(P\.?R\.?I\.?C\.?|P\.?R\.?I\.?)\\b'


    def cria_lista_de_linhas_primeira_instancia(self):

        expressao_cabecalho = re.compile('(Disponibilização: .{0,9}?-feira, *)(\d{1,2} *de *.{4,9} *de *\d{4})',re.IGNORECASE)
        lista_expressoes_ignoradas = []

        expressao_diario = re.compile('Diário.{0,100}- *Caderno *Judicial *- *1. *',re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_diario)

        expressao_caderno = re.compile('caderno *\d{1,2}\n')
        lista_expressoes_ignoradas.append(expressao_caderno)

        expressao_site = re.compile('www.dje.tjsp.jus.br')
        lista_expressoes_ignoradas.append(expressao_site)

        expressao_edicao = re.compile('São *Paulo, *Ano \w*? *- *Edição \d*', re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_edicao)

        expressao_rodape = re.compile('F *e *d *e *r *a *l.{0,100}?1 *1 *\. *4 *1 *9 *\/0 *6 *, *a *r *t *\. *4',re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_rodape)

        separador = '(PROC\.?(ESSO)?)?[ \:\-]*(\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})|(\d{3}\.\d{2}\.\d{6}\-\d)'
        return super(ExtratorDJSP, self).cria_lista_de_linhas_mantendo_npu_no_final(expressao_cabecalho, lista_expressoes_ignoradas, None, separador)

    def cria_lista_de_linhas_diarios_antigos(self):

        expressao_cabecalho = re.compile('(\w*-feira, *)(\d{1,2} *de *{4, *de *\d{4,9})',re.IGNORECASE)
        lista_expressoes_ignoradas = []

        expressao_diario = re.compile('Diário Oficial.{0,50}Caderno\s*\d\s*',re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_diario)


        expressao_edicao = re.compile('São *Paulo, *\d*\s*\(\d*\)\s*.?\s*\d', re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_edicao)
        if self.pega_data_caderno_nome_arquivo() and int(self.pega_data_caderno_nome_arquivo()[:4]) >= 2006:
            separador = '(PROC\.?(ESSO)?)?(^|\D{2}|\s)(\d{3}\.\d{2}\.\d{4}\.\d{6}\-\d(\/?\d{6}\-?\d{3})?|(\d{3}\.)?\d{2}\.\d{5,6}\-\d)'
        else:
            separador = '\.\s*\n(PROC\.?(ESSO)?)?\s*((\d{3})?\.?\d{2}\.?\d{5,6}\-?\d|\d{3,4}\/\d{2,4})\s*'

        return super(ExtratorDJSP, self).cria_lista_de_linhas_mantendo_npu_no_final(expressao_cabecalho, lista_expressoes_ignoradas, None, separador)

    def is_antigo(self):
        # Judiciario_II engloba II e III
        return True if 'Judiciario_II' in (self._arquivo.name) else False

    def is_edital_antigo(self):
        return True if 'Editais_e_Leiloes' in (self._arquivo.name) else False

    def is_primeira_instancia(self):
        return self.is_capital() or self.is_interior() or self.is_antigo()

    def is_capital(self):
        return True if 'Caderno12' in (self._arquivo.name) else False

    def is_interior(self):
        if (('Caderno13' in (self._arquivo.name)) or ('Caderno15' in (self._arquivo.name)) or ('Caderno18' in (self._arquivo.name))):
            return True
        else:
            return False

    def get_nome_caderno(self):
        if 'Caderno12' in self._arquivo.name:
            return "JUDICIAL - 1a INSTANCIA - CAPITAL"
        elif 'Caderno18' in self._arquivo.name:
            return "JUDICIAL - 1a INSTANCIA - INTERIOR - PARTE I"
        elif 'Caderno13' in self._arquivo.name:
            return "JUDICIAL - 1a INSTANCIA - INTERIOR - PARTE II"
        elif 'Caderno15' in self._arquivo.name:
            return "JUDICIAL - 1a INSTANCIA - INTERIOR - PARTE III"
        elif 'Judiciario_III' in self._arquivo.name:
            return "JUDICIARIO III - 1a INSTANCIA - INTERIOR"
        elif 'Judiciario_II' in self._arquivo.name:
            return "JUDICIARIO II - 1a INSTANCIA - CAPITAL"
        elif 'Edita' in self._arquivo.name or 'Caderno14' in self._arquivo.name:
            return "EDITAL - 1a INSTANCIA"


    def get_cod_caderno(self, caderno):
        if caderno.startswith("JUDICIAL") and caderno.endswith("CAPITAL"):
            return 12
        elif caderno.endswith("PARTE I"):
            return 18
        elif caderno.endswith("PARTE II"):
            return 13
        elif caderno.endswith("PARTE III"):
            return 15
        elif caderno.startswith("JUDICIARIO III"):
            return 3
        elif caderno.startswith("JUDICIARIO II"):
            return 2
        elif caderno.startswith("EDITAL"):
            return 14

    def is_edital(self):
        return True if 'Caderno14' in (self._arquivo.name) or 'Editais_e_Leiloes' in (self._arquivo.name) else False

    def salva_dados(self,processos):
        pass

    def identifica_data_cabecalho(self,expressao_cabecalho,linha_atual):
        pass

    def __remove_separadores_de_pagina(self, texto):
        return self.regex_cabecalho_pag.sub('\n', texto.replace("ﬁ","FI").upper())


    def __identifica_tipo_data_secao(self, secao):
        nome_comarca = re.search("DIS\-?\n?TRIBU.DOS?\\b(.*\\n?.*)EM",secao).group(1)
        nome_comarca = re.sub("(A|À|Á)(S)?[ ]*VARA(S)?[ ]*((CIVEIS)|(CRIMINAIS))?[ ]*?D[O|A]","",nome_comarca).strip()

        data_str = re.search('[0-9]{1,2} ?\/ ?[0-9]{1,2} ?\/ ?[0-9]{4}',secao).group(0).strip().replace(' ', '')
        data = datetime.datetime.strptime(data_str, '%d/%m/%Y')

        secao_regex = re.search('RELA..O[ *]DO[S]?[ *]FEITO[S]?(.*)DISTRIBU.DOS?', secao.replace('\n', ' ').strip())
        if secao_regex:
            secao = secao_regex.group(1)
            secao = secao.strip()
        else:
            secao = "OUTRAS"

        return remove_acentos(remove_caracteres_csv(secao.strip().replace(' ', '').upper())), data,nome_comarca

    def __identifica_secao(self, match, secoes,start_ref=None,end_ref = None):
        try:
            achou = False
            i = 1
            start = start_ref if start_ref else match.start()
            end = end_ref if end_ref else match.end()


            if len(secoes) == 0:
                return None, None, None
            elif start < secoes[0].start():
                return None, None, None
            elif start > secoes[-1].start():
                secao = secoes[-1].group(0)
                return self.__identifica_tipo_data_secao(secao)
            else:
                while not achou and i < len(secoes):
                    if  start > secoes[i-1].start() and start < secoes[i].start():
                        achou = True
                    else:
                        i += 1

            if achou:
                secao = secoes[i-1].group(0)
                return self.__identifica_tipo_data_secao(secao)
            else:
                return None, None, None
        except:
            return None, None, None

    def preenche_quadro_na_marra(self,path):
        diario_service = DiarioService()
        caderno_service = CadernoService()
        arquivo_service = ArquivoService()
        regex_num_proc = re.compile('PROC(\.|ESSO)?\s*.{0,50}?(N.?)?\s*((\d{7} *\-? *\d{2} *\. *\d{4} *\. *\d *\. *\d{2} *\. *\d{4})|(\d{3} *\. *\d{2} *\. *\d{4} *\. *\d{3} *\.? *\d{3}( *\- *\d *\/ *\d{6} *\- *\d{3}| *\- *\d)?)|(\d{3} *\. *\d{2} *\. *\d{3} *\.? *\d{3} *\- *\d)|(\d{2} *\. *\d{3} *\.? *\d{3} *\- *\d)|(\d{3} *\. *\d{3} *\. *\d{3} *\- *\d{2}))|(\\b\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\\b)')
        processo_service = ProcessoService()
        validaQuadro = ClassificaQuadroCredores(tag="FALENCIAS")
        lista_expressoes_ignoradas = []

        expressao_diario = re.compile('Diário.{0,100}- *Caderno *Judicial *- *1\W *', re.IGNORECASE)

        lista_expressoes_ignoradas.append(expressao_diario)

        expressao_caderno = re.compile('caderno *\d{1,2}', re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_caderno)

        expressao_site = re.compile('www.dje.tjsp.jus.br', re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_site)

        expressao_edicao = re.compile('S[Ãã]o *Paulo, *Ano \w* *- *Edi[Çç][Ãã]o \d*', re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_edicao)

        expressao_rodape = re.compile('F *e *d *e *r *a *l.{0,100}1 *1 *\. *4 *1 *9 *\/0 *6 *, *a *r *t *\. *4',
                                      re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_rodape)

        lista_expressoes_ignoradas.append(re.compile(
            'PUBLICA[ÇC][AÃ]O\s*OFICIAL\s*DO\s*TRIBUNAL\s*DE\s*JUSTI[ÇC]A.{0,50}LEI\s*FEDERAL[\s\,]*(N[Oº].{0,30})?ART\.\s*[0-9]+.?',
            re.IGNORECASE))
        lista_expressoes_ignoradas.append(
            re.compile('DI[ÁA]RIO\sD[AE]\sJUSTICA\sELETR[ÔO]NICO\s\-\sCADERNO\sEDITAIS\sE\sLEIL[ÕO]ES', re.IGNORECASE))
        lista_expressoes_ignoradas.append(re.compile('CADERNO(\sDE)?\s+EDITAIS\s+E\s+LEILOES', re.IGNORECASE))
        lista_expressoes_ignoradas.append(re.compile(
            'ANO.{0,}.EDICAO\s[0-9][0-9][0-9][0-9]\s..{0,15}\s?[,]\s?([0-9][0-9])\s?DE\s?.{0,10}\sDE\s[0-9][0-9][0-9][0-9]',
            re.IGNORECASE))
        lista_expressoes_ignoradas.append(
            re.compile('DIARIO\sOFICIAL\sPODER\sJUDICIARIO\s.\sCADERNO\sDE\sED\w*', re.IGNORECASE))
        lista_expressoes_ignoradas.append(
            re.compile('\s*DI[AÁ]RIO OFICIAL PODER JUDICI[AÁ]RIO – CADERNO DE EDITAIS E LEIL[OÕ]ES\s*'))
        lista_expressoes_ignoradas.append(re.compile(
            '\s*(JU[ÍI]ZA? DE DIREITO DA )?\d+. VARA CÍVEL D[OAE](STA)? (FORO|COMARCA)?( DE )? ?.+?(,|SP|\.|;)'))
        lista_expressoes_ignoradas.append(re.compile('VALORES\s*EXPRESSOS\s*EM\s*CR\$', re.IGNORECASE))
        lista_expressoes_ignoradas.append(re.compile('\\b\w{5} *\. *\d{3}\\b\s*\n', re.IGNORECASE))

        # separador = '(?:SER[ÁáA]? *)?(?:PUBLICADO *(?:[Ee] *)?|AFI ?XADO *(?:[Ee] *)?){1,2}\s*.{0,27}?\s*(?:NA\s+FORMA\s+DA\s+LEI|(NO|EM) *(?:LOCAL|LUGAR) *(PUBLICO E )?DE *COSTUME)\.? *|(?:AFIXADO *E *PUBLICADO)|S[ãÃaA]O *PAULO *, *\d{1,2}\s*DE\s[A-ZÇç]+\s*DE\s*\d{4}\.?|(?:S[ãÃAa]O\s*PAULO|S[\.\s]?P[\.\s]?|SANTOS)[,\s]+\d{1,2}\s*DE\s*[A-Za-zçÇ]+\s*(DE\s*)?\d{4}.|(?:S[ãÃAa]O\s*PAULO|S[\.\s]?P[\.\s]?|SANTOS)[,\s]+\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\.|PRAZO\sDE.{0,20}DIAS,?\s*(NA\s+FORMA\s+DA\s+LEI|NO *(LOCAL|LUGAR) *DE *COSTUME)|\\b[0-9][A-Z]{4}\.[0-9]{3}\\b|\\b(PRIC|PRI)\\b'
        separador = '\n'
        for arquivo in os.listdir(path):
            print("{}".format(arquivo))
            data_caderno = re.search('.*(\d{4}_\d{2}_\d{2})', arquivo).group(1)
            with open(os.path.join(path, arquivo), "r", encoding='utf-8') as f:
                linhas = f.readlines()
                if linhas != []:
                    linhas = list(map(lambda x: x.replace('\n', '').upper(), linhas))
                    linhas_concatenadas = ''
                    fatia = 10000
                    for i in range(0, int(len(linhas) / fatia) + 1):
                        if i * fatia < len(linhas):
                            linhas_concatenadas += (
                                reduce(lambda x, y: x + ' ' + y if not x.endswith('-') else x[:-1] + y,
                                       linhas[i * fatia:i * fatia + fatia]))

                    for expressao_ignorada in lista_expressoes_ignoradas:
                        linhas_concatenadas = expressao_ignorada.sub('', linhas_concatenadas)

                    lista_de_linhas = re.split(separador, linhas_concatenadas)
                    lista_de_linhas = list(filter(lambda linha: linha and linha != '', lista_de_linhas))
            for item in lista_de_linhas:
                item = item.upper()
                match_num = list(regex_num_proc.finditer(item))
                if len(match_num) > 0 :
                    npus = []
                    # list((set([p.group(3) for p in match_num])))
                    for num in match_num:
                        if num.group(3) and num.group(3) not in npus :
                            npus.append(num.group(3))
                        elif num.group(10) and num.group(10) not in npus :
                            npus.append(num.group(10))
                    indice_npus = 0
                    while npus and indice_npus < len(npus):
                        num_proc = npus[indice_npus]
                        # num_proc = match.group(3)
                        for processo in processo_service.dao.lista_por_numero_processo_ou_npu(num_proc):
                            if not processo.quadro_credores:
                                print('PEGANDO O PROCESSO {} do ID {}'.format(processo.npu_ou_num_processo,processo.id))
                                #processo = processo_service.preenche_processo(npu=num_proc)

                                if not processo:
                                    print(num_proc)
                                    processo = self._acompanhamento.gera_arvore_processos(num_proc, 'FALENCIAS', True,
                                                                                          self.get_caderno())

                                if processo and processo.is_processo_falencia_recuperacao_convolacao():

                                    diario = os.path.basename(arquivo)

                                    try:
                                        data = re.search("(\d{4}_\d{2}_\d{2}).*?\.txt", diario).group(1)
                                    except:
                                        data = None

                                    diario = diario_service.preenche_diario(diario, data)

                                    caderno = caderno_service.preenche_caderno("EDITAL - 1a INSTANCIA", diario)

                                    if self._arquivo_bd:
                                        self._arquivo_bd = arquivo_service.preenche_arquivo(self._arquivo_bd.nome_arquivo,
                                                                                            diario, caderno)
                                    validaQuadro.verifica_quadro_credores_no_diario(item, data_caderno, processo,
                                                                        caderno=caderno,
                                                                        fonte_dado='DJSP')
                            else:
                                print('Já possui quadro para esse processo {}'.format(processo.npu))
                        indice_npus+=1
                else:
                    print("NPU OU NUMERO DE PROCESSO NAO ENCONTRADO!")

    def extrai(self, tag=None, ):
        diario_service = DiarioService()
        arquivo_service = ArquivoService()

        f = open("lista_processos.txt", mode='a', encoding="utf8")
        try:
            ConfigManager().escreve_log(
                "Extraindo {}".format(self._arquivo.name),
                self._acompanhamento.nome, 'log_extrator_djsp.txt')
            lista, data_caderno = self.cria_lista_de_linhas()
            if not lista:  # se não tiver extrator, ele diz que foi extraído para não ficar tentando extrair toda vez
                return True
            # if self.is_edital(): #Antes só verificava as empresas no edital, agora em qualquer caderno e bate no sistema se não tivermos no banco.
            # self.verifica_empresas_no_caderno(lista,True)
            num_processos, editais = self.procura_processos_falencia(lista)
            if (data_caderno):
                f.write("Data caderno {}\n".format(str(data_caderno)))
            processou_algum_processo = False
            if num_processos:
                diario = diario_service.preenche_diario('DJSP', data_caderno)

                caderno = self.get_caderno()

                if self._arquivo_bd:
                    self._arquivo_bd = arquivo_service.preenche_arquivo(self._arquivo_bd.nome_arquivo, diario,
                                                                        caderno)

                num_processos = list(set(num_processos))  # remove duplicados
                print('Encontrei {} processos'.format(len(num_processos)))
                self.acompanhamentoDJSPSelenium.bate_lista_processos(npus=num_processos, tag="FALENCIAS",
                                                                                       usuario='01105013731',
                                                                                       senha='Ruthemi123!',
                                                                                       baixa_arvore=True,
                                                                                       retorna_processos=True,
                                                                                       verifica_minio=True,
                                                                                       salva_arvore_por_arvore=True,
                                                                                       bucket='extrator-djsp')
        except Exception as e:
            ConfigManager().escreve_log("ERROR: " + str(e), self._acompanhamento.nome, 'log_extrator_DJSP_erro.txt')
            raise e
            return False
        finally:
            f.close()
if __name__ == '__main__':
    # p = ExtratorDJSP.busca_assuntos(ExtratorDJSP, npu="1003096-50.2018.8.26.0236", tag='CLASSE_DistribDiversos')
    p = ProcessaExtrator("DJSP", "txt", ExtratorDJSP, AcompanhamentoProcessualDJSPselenium)
    if len(sys.argv) > 2:
        p.extrai_diversos_que_nao_foram_extraidos_a_partir_da_data(
            data=datetime.datetime.strptime('2014-12-12', "%Y-%m-%d").date(), fatia=int(sys.argv[1]), rank=int(sys.argv[2]), tag='FALENCIAS')
    else:
        p.extrai_diversos_que_nao_foram_extraidos_a_partir_da_data(data=datetime.datetime.strptime('2020-1-1', "%Y-%m-%d").date(), tag='FALENCIAS')
    # extrator = ExtratorDJSP(None,AcompanhamentoProcessualDJSP)
    # #MANDEI REFAZER TUDO, TENDO PREENCHIDO QUADRO OU NÂO PQ EU PAREI ALGUNS NA METADE E ELE COMMITAVA!
    # extrator.preenche_quadro_na_marra('novos_diarios\\novos')
    # # extrator.preenche_quadro_na_marra('diarios_quadro')