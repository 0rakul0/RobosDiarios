import re
import datetime
from extrator.ExtratorBase import ExtratorBase
from classificadores.ClassificaEdital import ClassificaEdital
from acompanhamento_processual.AcompanhamentoProcessualDJBA import AcompanhamentoProcessualDJBA
from extrator.ProcessaExtrator import ProcessaExtrator
from util.ConfigManager import ConfigManager


class ExtratorDJBA(ExtratorBase):
    nome_diario = "DJBA"


    def __init__(self, arquivo, acompanhamento,arquivo_bd = None):
        super(ExtratorDJBA, self).__init__("DJBA", arquivo, acompanhamento, ClassificaEdital(), arquivo_bd)
        self.log = "log_extratorDJBA.txt"

    def get_nome_caderno(self):
        return "JUDICIAL"

    def salva_dados(self,processos):
        return

    def is_edital(self):
        pass

    def identifica_data_cabecalho(self,expressao_cabecalho,linha_atual):
        pass

    def concatena_npu_texto(self, lista):
        del lista[0]
        if (len(lista)%2 == 1):
            lista.append("")
        for count, item in enumerate(lista):
            lista[count] = lista[count] + lista[count+1]
            del lista[count+1]
        return lista

    def cria_lista_de_linhas(self):
        #todo colocar expressao cabeçalho nas expressoes ignoradas
        expressao_cabecalho = re.compile(
            'Cad\s*\d{1,3}\s*[\\\/-––]\s*P.gina\s*\d{1,5}\s*TJBA\s*[\\\/-––]\s*DI.RIO\sDA\sJUSTI.A\sELETR.NICO\s[\\\/-––]\sN.\s\d{1,4}\.\d{1,5}\s[--––]\sDisponibiliza..o.{0,9}?-feira, *\d{1,2} *de *.{4,9} *de *\d{4}')
        lista_expressoes_ignoradas = []

        expressao_data = re.compile(" *\d{1,2} *DE *[A-Za-zÇç]* *DE *20[01]\d")
        lista_expressoes_ignoradas.append(expressao_data)
        #lista_expressoes_ignoradas.append(expressao_cabecalho)

        separador = '(\d{7}\-\d{2}\.\d{4}\.\d\.?\d{2}\.\d{4})|(\d{3}\.\d{2}\.\d{4}\.\d{6}(\-\d\/\d{6}\-\d{3})?)|(\d{3}\.\d{2}\.\d{6}\-\d)'
        lista_de_linhas , data = super(ExtratorDJBA, self).cria_lista_de_linhas_removendo_separador(lista_expressoes_ignoradas, separador)
        lista_de_linhas = self.concatena_npu_texto(lista_de_linhas)
        return lista_de_linhas,data
        # return super(ExtratorDJBA, self).cria_lista_de_linhas_sem_remover_separador(expressao_cabecalho,
        #                                                                                   lista_expressoes_ignoradas,
        #                                                                                   False, separador)



    def procura_processos_falencia(self, lista_de_linhas):
        #expressao_processo_novo = re.compile('(\d{7} *\-\d{2} *\.\d{4} *\.\d *\.\d{2} *\.\d{4}) *((\(\d{3} *\.\d{2} *\.\d{4} *\.\d{6}\))|(\(p *r *o *c *e *s *s *o *p *r *i *n *c *i *p *a *l.*)) *\- *(F *a *l *[Êê] *n *c *i *a) *d *e *E *m *p *r *e *s *[Áá] *r *i *o *s *, *S *o *c',re.IGNORECASE)
        expressao_npu_numero_proc = re.compile('(\d{7}\-\d{2}\.\d{4}\.\d\.?\d{2}\.\d{4})|(\d{3}\.\d{2}\.\d{4}\.\d{6}(\-\d\/\d{6}\-\d{3})?)|(\d{3}\.\d{2}\.\d{6}\-\d)')
        expressao_processo = re.compile('(((Pedido *de)? *(Auto)? *(fa[\- ]*l[Êê]n[\- ]*c[\- ]*ia))|(Recupera[Çç][Ãã]o *Judicial)) *((-) *| *(de *Empres[Áá]rios *, *So))',re.IGNORECASE)
        expressao_processo_recuperacao_novo = re.compile("Recupera[Çç][Ãã]o judicial",re.IGNORECASE)
        expressao_falencia = re.compile('(AUTO-?|PEDIDO\s+D?E?\s*)?FAL[ÊE]NCIA|INSOLV[ÊE]NCIA\s+REQUERIDA\s+PELO\s+CREDOR',re.IGNORECASE)
        expressao_convolacao = re.compile('Convola[cçCÇ][ãaAÃ]o',re.IGNORECASE)
        expressao_rec_jud = re.compile('rec\.?(upera[cçCÇ][ãaAÃ]o)?\s*(jud\.?(icial)?)',re.IGNORECASE)
        expressao_decl_creditos = re.compile('DECLARA[ÇC][ÃA]O\s+DE\s+CR[ÉE]DITO',re.IGNORECASE)

        # expressao_processo = re.compile(
        #     '........................................................................................................................',
        #     re.IGNORECASE)
        # expressao_processo_recuperacao_novo = re.compile(".........", re.IGNORECASE)
        # #expressao_falencia = re.compile(    '.', re.IGNORECASE)
        # expressao_convolacao = re.compile('.........', re.IGNORECASE)
        # expressao_rec_jud = re.compile('.........', re.IGNORECASE)
        # expressao_decl_creditos = re.compile('.........', re.IGNORECASE)

        processos_encontrados = []
        for item in lista_de_linhas:
            npu_num_proc = expressao_npu_numero_proc.search(item)
            processo_match = expressao_processo.search(item)
            if npu_num_proc:
                if processo_match:
                    processos_encontrados.append(npu_num_proc.group(0))
                    print(npu_num_proc.group(0) + " - " + processo_match.group(0))
                    ConfigManager().escreve_log(
                        "{npu} - {match} .".format(npu=str(npu_num_proc.group(0)),
                                                   match=str(processo_match.group(0))),
                        self._acompanhamento.nome, self.log)
                    print(60 * '*')
                    print(60*'*')
                else:
                    processo_recuperacao_match = expressao_processo_recuperacao_novo.search(item)
                    if processo_recuperacao_match:
                        processos_encontrados.append(npu_num_proc.group(0))
                        print((npu_num_proc.group(0) + " - " + processo_recuperacao_match.group(0)))
                        ConfigManager().escreve_log(
                            "{npu} - {match} .".format(npu=str(npu_num_proc.group(0)),
                                                       match=str(processo_recuperacao_match.group(0))),
                            self._acompanhamento.nome, self.log)
                        print(60 * '*')
                        print(60*'*')
                    else:
                        falencia_match = expressao_falencia.search(item)
                        if falencia_match:
                            processos_encontrados.append(npu_num_proc.group(0))
                            print((npu_num_proc.group(0) + " - " + falencia_match.group(0)))
                            ConfigManager().escreve_log(
                                "{npu} - {match} .".format(npu=str(npu_num_proc.group(0)),
                                                           match=str(falencia_match.group(0))),
                                self._acompanhamento.nome, self.log)
                            print(60*'*')
                        else:
                            convolacao_match = expressao_convolacao.search(item)
                            if convolacao_match:
                                processos_encontrados.append(npu_num_proc.group(0))
                                print((npu_num_proc.group(0) + " - " + convolacao_match.group(0)))
                                ConfigManager().escreve_log(
                                    "{npu} - {match} .".format(npu=str(npu_num_proc.group(0)),
                                                               match=str(convolacao_match.group(0))),
                                    self._acompanhamento.nome, self.log)
                                print(60*'*')
                            else:
                                rec_jud_match = expressao_rec_jud.search(item)
                                if rec_jud_match:
                                    processos_encontrados.append(npu_num_proc.group(0))
                                    print((npu_num_proc.group(0) + " - " + rec_jud_match.group(0)))
                                    ConfigManager().escreve_log(
                                        "{npu} - {match} .".format(npu=str(npu_num_proc.group(0)),
                                                                   match=str(rec_jud_match.group(0))),
                                        self._acompanhamento.nome, self.log)
                                    print(60*'*')
                                else:
                                    decl_creditos_match = expressao_decl_creditos.search(item)
                                    if decl_creditos_match:
                                        processos_encontrados.append(npu_num_proc.group(0))
                                        print((npu_num_proc.group(0) + " - " + decl_creditos_match.group(0)))
                                        ConfigManager().escreve_log("{npu} - {match} .".format(npu = str(npu_num_proc.group(0)), match = str(decl_creditos_match.group(0))), self._acompanhamento.nome, self.log)
                                        print(60*'*')

        ConfigManager().escreve_log("Foram encontrados {} processos do nosso interesse.".format(str(len(processos_encontrados))), self._acompanhamento.nome, self.log)
        print(("Foram encontrados "+str(len(processos_encontrados)) + " processos do nosso interesse."))
        return processos_encontrados , None

if __name__ == '__main__':
    p = ProcessaExtrator("DJBA", "txt", ExtratorDJBA, AcompanhamentoProcessualDJBA)
    p.extrai_diversos()