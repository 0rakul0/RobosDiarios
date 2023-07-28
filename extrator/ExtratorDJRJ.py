import re
from extrator.ExtratorBase import ExtratorBase
from classificadores.ClassificaEdital import ClassificaEdital
from acompanhamento_processual.AcompanhamentoProcessualRJ import AcompanhamentoProcessualRJ
from extrator.ProcessaExtrator import ProcessaExtrator
from util.ConfigManager import ConfigManager

class ExtratorDJRJ(ExtratorBase):
    nome_diario = "DJRJ"

    def __init__(self, arquivo, acompanhamento,arquivo_bd=None):
        super(ExtratorDJRJ, self).__init__("DJRJ", arquivo, acompanhamento, ClassificaEdital(), arquivo_bd)
        self.__log = "log_extrator_rj.txt"
        self.__erro = "erro_extrator_rj.txt"

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
        if len(lista) % 2 == 1:
            lista.append("")
        for count, item in enumerate(lista):
            lista[count] = lista[count] + lista[count+1]
            del lista[count+1]
        return lista

    def cria_lista_de_linhas(self):
        expressao_cabecalho = re.compile(
            'Publicação.{0,200}\s*PODER JUDICI[AÁ]RIO DO\s*ESTADO DO RIO DE JANEIRO\s*Ano.{0,20}\s*Disponibiliza[çc][aã]o.\s*.*\s*(Publica[çc][ãa]o.\s*.*\s*)?DI[ÁA]RIO DA JUSTI[ÇC]A ELETR[ÔO]NICO\s*Caderno.{0,30}\s*TRIBUNAL.{0,50}\s*www.{0,15}\s*.{1,}.\s*PRESIDENTE\s*.{1,}.\s*.{1,}\s*1.{1,}\s*2.{1,}.\s*3.{1,}')

        expressao_data = re.compile(" *\d{1,2} *DE *[A-Za-zÇç]* *DE *20[01]\d")

        expressao_para_o_mes_de_agosto = re.compile('DURANTE\s*O\s*MÊS\s*DE\s*AGOSTO,\s*O\s*DJERJ\s*SERÁ\s*PUBLICADO\s*EM\s*CARÁTER\s*EXPERIMENTAL,\s*SEM\s*VALOR\s*LEGAL\.\s*')

        expressao_nucleos = re.compile('1º\sNúcleo|2º\sNúcleo|3º\sNúcleo|4º\sNúcleo|5º\sNúcleo|6º\sNúcleo|7º\sNúcleo|8º\sNúcleo|9º\sNúcleo|10º\sNúcleo|11º\sNúcleo|12º\sNúcleo|13º\sNúcleo')

        lista_expressoes_ignoradas = []

        lista_expressoes_ignoradas.append(expressao_cabecalho)
        lista_expressoes_ignoradas.append(expressao_para_o_mes_de_agosto)
        lista_expressoes_ignoradas.append(expressao_data)
        lista_expressoes_ignoradas.append(expressao_nucleos)

        #titulo = '\\.\\s*$\\s*.{50}'

        separador_2008_9 = re.compile('(\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})|(\d{4}\.\d{3}\.\d{6}\-\d)')
        separador = re.compile('(\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})')

        lista_de_linhas, data = super(ExtratorDJRJ, self).cria_lista_de_linhas_removendo_separador(lista_expressoes_ignoradas, separador)
        lista_de_linhas = self.concatena_npu_texto(lista_de_linhas)
        return lista_de_linhas, data

    def procura_processos_falencia(self, lista_de_linhas):
        expressao_npu_numero_proc = re.compile('(\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})|(\d{3}\.\d{2}\.\d{4}\.\d{6}(\-\d\/\d{6}\-\d{3})?)|(\d{3}\.\d{2}\.\d{6}\-\d)')
        expressao_processo = re.compile('(((Pedido *de)? *(Auto)? *(fa[\- ]*l[Êê]n[\- ]*c[\- ]*ia))|(Recupera[Çç][Ãã]o *Judicial)) *((-) *'
                                        '| *(de *Empres[Áá]rios *, *So))', re.IGNORECASE)

        expressao_processo_recuperacao_novo = re.compile("Recupera[Çç][Ãã]o judicial", re.IGNORECASE)
        expressao_falencia = re.compile('(AUTO-?|PEDIDO\s+D?E?\s*)?FAL[ÊE]NCIA|INSOLV[ÊE]NCIA\s+REQUERIDA\s+PELO\s+CREDOR', re.IGNORECASE)
        expressao_convolacao = re.compile('Convola[cçCÇ][ãaAÃ]o',re.IGNORECASE)
        expressao_rec_jud = re.compile('rec\.?(upera[cçCÇ][ãaAÃ]o)?\s*(jud\.?(icial)?)', re.IGNORECASE)
        expressao_decl_creditos = re.compile('DECLARA[ÇC][ÃA]O\s+DE\s+CR[ÉE]DITO', re.IGNORECASE)

        processos_encontrados = []
        for item in lista_de_linhas:
            npu_num_proc = expressao_npu_numero_proc.search(item)
            processo_match = expressao_processo.search(item)
            if npu_num_proc:
                if processo_match:
                    processos_encontrados.append(npu_num_proc.group(0))
                    ConfigManager().escreve_log(
                        "{npu} - {match} .".format(npu=str(npu_num_proc.group(0)),
                                                    match=str(processo_match.group(0))),
                        self._acompanhamento.nome, self.log)
                    print(60 * '*')
                else:
                    processo_recuperacao_match = expressao_processo_recuperacao_novo.search(item)
                    if processo_recuperacao_match:
                        processos_encontrados.append(npu_num_proc.group(0))
                        ConfigManager().escreve_log(
                            "{npu} - {match} .".format(npu=str(npu_num_proc.group(0)),
                                                        match=str(processo_recuperacao_match.group(0))),
                            self._acompanhamento.nome, self.log)
                        print(60 * '*')
                    else:
                        falencia_match = expressao_falencia.search(item)
                        if falencia_match:
                            processos_encontrados.append(npu_num_proc.group(0))
                            ConfigManager().escreve_log(
                                "{npu} - {match} .".format(npu=str(npu_num_proc.group(0)),
                                                            match=str(falencia_match.group(0))),
                                self._acompanhamento.nome, self.log)
                            print(60 * '*')
                        else:
                            convolacao_match = expressao_convolacao.search(item)
                            if convolacao_match:
                                processos_encontrados.append(npu_num_proc.group(0))
                                ConfigManager().escreve_log(
                                    "{npu} - {match} .".format(npu=str(npu_num_proc.group(0)),
                                                                match=str(convolacao_match.group(0))),
                                    self._acompanhamento.nome, self.log)
                                print(60 * '*')
                            else:
                                rec_jud_match = expressao_rec_jud.search(item)
                                if rec_jud_match:
                                    processos_encontrados.append(npu_num_proc.group(0))
                                    ConfigManager().escreve_log(
                                        "{npu} - {match} .".format(npu=str(npu_num_proc.group(0)),
                                                                    match=str(rec_jud_match.group(0))),
                                        self._acompanhamento.nome, self.log)
                                    print(60 * '*')
                                else:
                                    decl_creditos_match = expressao_decl_creditos.search(item)
                                    if decl_creditos_match:
                                        processos_encontrados.append(npu_num_proc.group(0))
                                        ConfigManager().escreve_log(
                                            "{npu} - {match} .".format(npu=str(npu_num_proc.group(0)),
                                                                        match=str(decl_creditos_match.group(0))),
                                            self._acompanhamento.nome, self.log)
                                        print(60 * '*')

        print("Foram encontrados "+str(len(processos_encontrados)), 'processos')
        return processos_encontrados, None

if __name__ == '__main__':
    p = ProcessaExtrator("DJRJ", "txt", ExtratorDJRJ, AcompanhamentoProcessualRJ)
    p.extrai_diversos('Judicial_-_1')
