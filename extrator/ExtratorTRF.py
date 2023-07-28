# -*- coding: utf-8 -*-

import re

import os, sys
import datetime
from extrator.ExtratorBase import ExtratorBase
from acompanhamento_processual.AcompanhamentoProcessualTRF1 import  AcompanhamentoProcessualTRF1
from extrator.ProcessaExtrator import ProcessaExtrator
from pdjus.service.CadernoService import CadernoService
from pdjus.service.DiarioService import DiarioService
from pdjus.service.ProcTempService import ProcTempService
from pdjus.service.ProcTempTagService import ProcTempTagService
from util.StringUtil import remove_acentos, remove_varios_espacos
from util.ConfigManager import ConfigManager
from pdjus.modelo.Publicacao import Publicacao
from pdjus.modelo.Distribuicao import Distribuicao
from pdjus.modelo.ProcTemp import ProcTemp
from util.RegexUtil import RegexUtil

class ExtratorTRF(ExtratorBase):

    nome_diario = "TRF05"

    def __init__(self, arquivo, acompanhamento = None,arquivo_bd = None):
        super(ExtratorTRF, self).__init__("TRF", arquivo, acompanhamento, None,arquivo_bd)
        # self.atas_distrib_trf3 = "dados\TRF\html\2005\06{}"
        # self.mongo_client = MongoClient(
        #     'mongodb://projetobpc:pr0j3t0bpc@cluster1-shard-00-00-6jpvu.mongodb.net:27017,cluster1-shard-00-01-6jpvu.mongodb.net:27017,cluster1-shard-00-02-6jpvu.mongodb.net:27017/<DATABASE>?ssl=true&replicaSet=Cluster1-shard-0&authSource=admin')
        # self.current_database = self.mongo_client.bpc

        self.aux_dict_estados = {
            'amazonas': "AM",
            'acre': "AC",
            'bahia': "BA",
            'tocantins': "TO",
            'minas gerais': "MG",
            'distrito federal': "DF",
            'goias': "GO",
            'piaui': "PI",
            'amapa': "AP",
            'roraima': "RR",
            'rondonia': "RO",
            'para': "PA",
            'maranhao': "MA",
            'mato grosso': "MT",
            'mato grosso do sul': "MS"
        }

        self.distribuicoes = []
        self.publicacoes = []

        self.versao = 1

        # self.regex_npu = re.compile('', re.MULTILINE)

        # self.regex_npu = "(\d{7}\-?\d{2}\.?\d{4}\.?4\.?01\.?\d{4}|\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.d{4})|(\d{3}\.\d{2}\.\d{4}\.\d{6}(\-\d\/\d{6}\-\d{3})?)|(\d{3}\.\d{2,4}\.\d{6}\-?\d?)"
        #self.regex_npu = "(\\b\d{1,7}[\-\s]*?\d{2}\.?(19|20)\d{2}\.?[48]\.?\d{2}\.?\d{4}\\b|\\b(19|20)\d{2}\.?\d{2}\.?\d{2}\.?\d{5,6}[\-\s]*?\d\\b)"  # AAAA.RE.OR.NNNNN-D
        self.regex_npu = "(\d{1,7}\-?\d{2}\.?\d{4}\.?4\.?0[1-5]\.?\d{4}|\d{4}\.?\d{2}\.?\d{2}\.?\d{5,6}\-?\d)"
        # alterada a regex de npu para incluir também npus que não contenham pontos ou traços ou zeros na frente

        # self.regex_trf1 = "^(?>\bagravo\b\s++\bde\b\s++\binstrumento\b|\bconflito\b\s++\bde\b\s++\bcompetência\b|\bação\b\s++\brescisória\b)\s++N\.\s++(?P<NUM>[\d\-\.\s]++)\/\w\w.*$(?P<teste>\s^.*$)\s++(?>RELATORA?\s++)(.*$\s)+?E\s++M\s++E\s++N\s++T\s++A\s++(?P<EMENTA>(.*$\s)+?)A\s++C\s++Ó\s++R\s++D\s++Ã\s++O\s++(?P<ACORDAO>(.*$\s)+?)\s"
        # self.regex_trf1_teste = "^(?>\bagravo\b\s++\bde\b\s++\binstrumento\b|\bconflito\b\s++\bde\b\s++\bcompetência\b|\bação\b\s++\brescisória\b)\s++N\.\s++(?P<NUM>[\d\-\.\s]++)\/\w\w.*$(?P<teste>\s^.*$)\s++(?>RELATORA?\s++)(.*$\s)+?(?>DECISÃO\s++|E\s++M\s++E\s++N\s++T\s++A\s++|D\s++E\s++C\s++I\s++S\s++Ã\s++O\s++)"
        # self.regex_distribuicao_old = "^(?P<NUM>[\d\-\.]++)\s++\d++\s++\-\s++[A-Za-z\s\/íéóúáàêôãõ]++^.\s(?P<VARA>\s^.*$)+?\s\s"

        # partes = "\s*?(?>"
        # itens_parte = "AUTOR|SUSCITANTE|REPTE|ARGTE|ORDNTE|OPOENTE|EXQTE|RECTE|REQTE|DEPCTE|EXPTE|LITISAT|ASSISTA|PROCUR|IMPDO|EXPTE|IMPTE|EMBTE|INDCDO|EXCDO|REQDO|PACIENTE|PERITO|EXEQTE|REAQDO|AUTDE\.?\s*+POL\.?|RECDO\/RECTE|P\.\s*+AUTORA|RELATOR(?:\(A\))?"
        # partes += itens_parte+"|"
        # for p in itens_parte.split('|')[:-4]:
        #     partes += '\s*+'.join(list(p)) + "|"
        # partes = partes[:-1] + ")\.?"

        #self.regex_distribuicao2 = "^(?P<NUM>[\d\-\.]++)\s++(?P<NUM_CLASSE>\d++)\s++\-\s++(?P<CLASSE>[A-Za-z\s\/íéóúáàêôãõ]+?)"+partes+"\s*(?P<VARA>^.*\s)+?(\s\*|\s\s)"
        # funciona para alguns casos em TRF01_JUD_SJAC_2017_06_02

        # self.regex_distribuicao3 = "^PROCESSO\s++:\s++(?P<NUM>[\d\-\.]++)\s++.*$\sCLASSE\s++:\s++(?P<NUM_CLASSE>\d++)-(?P<CLASSE>[A-Za-z\s\/íéóúáàêôãõ]+?)(?:AUTOR|EXQTE|REQTE|DEPCTE|LITISAT|AUTDE.POL|ASSISTA|PROCUR|IMPDO|EXPTE|IMPTE|EMBTE|INDCDO|EXCDO|REQDO)\s*(?P<VARA>\s^.*$)+?\s\s"
        #self.regex_distribuicao3 = "^PROCESSO\s*?:\s*?(?P<NUM>[\d\-\.]++)\s++.*$\sCLASSE\s*?:\s*?(?P<NUM_CLASSE>\d++)-(?P<CLASSE>[A-Za-z\s\/íéóúáàç\(\)êôãõ]+?)"+partes+"\s*(?P<VARA>\s^.*$)+?(\s\*|\s\s)"
        # funciona para alguns casos em TRF01_JUD_SJAC_2017_06_02

        self.regex_skip_bad_conversion = "PROCESSO:\s*PROCESSO:"
        self.regex_partes = "(?P<PARTE>^.*\s:.*\s)"

        # self.regex_publicacao = "^\s*?(?:PROCESSO\b\s*+N?.?\s*+|Numera[çc][aã]o\s*+[úu]nica\s*+):\s*?(?P<NUM>.*+)$[\s^]*+[\d\s\-\.]+(?P<TIPO>(?>.*$\s){1,7}?)(?:(?P<PARTES>"+partes+"(?>.*$\s)+?)(?:(?P<TEXTO>(?:O|A)?\s*+EXM(.*$\s){1,}?)\s|EDITAL\sDE\sCITAÇÃO))"
        # self.regex_cabecalho = "^(?:\d++\s*+)?Di[aá]rio\s*+da\s*+Justi[çc]a\s*+Federal\s*+da\s*+\d++.\s*+Regi[ãa]o\s*+(?:\/\s*+[\w\d]++)?\s*+\-\s*+(?:Ano\s*+\w++\s++N\.\s*+\d++\s*+\-\s*+)?Caderno\s*+(Judicial|Administrativo)\s*+\-\s*+Disponibilizado\s*+em\s*+\d++\/\d++\/\d++\s*+(?:PODER\s*+JUDICIÁRIO\s*+.*$(\s.*){1,}?)?"
        #
        # self.regex_split_publicacao = "EXPEDIENTE\sDO\sDIA\s(\d\d)DE"
        # self.regex_split_distribuicao = "ATA\s+DE\s+DISTRIBUI[CÇ][ÃA].*?:\s*(?P<DATA_DISTRIBUICAO>\d+\/\d+\/\d+)"

        self.flags=re.I|re.M|re.U|re.X

        ### Regexes para pré 2015/03

        # self.regex_distribuicao_pre20153 = "^(?P<NUM>[\d\-\.]++)\s++(?P<NUM_CLASSE>\d++)\s++\-\s++(?P<CLASSE>[A-Za-z\s\/íéóúáàêôãõç]+?)\s*?"+partes+"\s*(?:^.*\s)+?(?:V\s*+a\s*+r\s*+a\s*+:\s*+(?P<VARA>.*$))"
        # self.regex_distribuicao2_pre20153 = "^PROCESSO\s*?:\s*?(?P<NUM>[\d\-\.]++)\s*+CLASSE\s*+:\s*+(?P<NUM_CLASSE>\d++)?\-?(?P<CLASSE>[A-Za-z\s\/íéóúáàç\(\)êôãõ]+?)\s*?(?P<parte>(AUTOR|SUSCITANTE|REPTE|ARGTE|ORDNTE|OPOENTE|EXQTE|RECTE|REQTE|DEPCTE|EXPTE|LITISAT|ASSISTA|PROCUR|IMPDO|EXPTE|IMPTE|EMBTE|INDCDO|EXCDO|REQDO|PACIENTE|PERITO|EXEQTE|REAQDO|AUTDE\.?\s*+POL\.?|RECDO\/RECTE|P\.\s*+AUTORA|RELATOR(?:\(A\))?)\s*(?:^.\s)+?)(?:V\s+a\s*+r\s*+a\s*+:\s*+(?P<VARA>.*$))"
        #
        # #self.regex_distribuicao = "^(PROCESSO\s*?:\s*?)?(?P<NUM>[\d\-\.]++)\s*+)(CLASSE\s*+:\s*+)?(?P<NUM_CLASSE>\d++)?\-?(?P<CLASSE>[A-Za-z\s\/íéóúáàç\(\)êôãõ]+?)\s*?"+partes+"\s*(?:^.*\s)+?(?:V\s*+a\s*+r\s*+a\s*+:\s*+(?P<VARA>.*$))"
        # self.regex_split_secoes = "^Se[cç][aã]o\s*+Judici[aá]ria\s*+do\s*+(?:(?:estado\s*+d[aoe]\s*+)*?(amazonas|acre|bahia|tocantins|minas\s*+gerais|distrito\s*+federal|goi[aá]s|piau[ií]|amap[aá]|roraima|rond[ôo]nia|par[aá]|maranh[ãa]o|mato\s*+grosso|mato\s*+grosso\s*+do\s*+sul))$"
        # # self.regex_publicacao_pre201503 = "^\s*?[\s^]*+(?P<NUM>[\d\s\-\.])+(?P<TIPO>(?>.*$\s){1,7}?)(?:(?P<PARTES>"+partes+"(?>.*$\s)+?)(?:(?P<TEXTO>(?:O|A)?\s*+EXM(.*$\s){1,}?)Numera[çc][ãa]o))"
        # self.regex_publicacao_pre201503 = "[\s^]++(?P<NUM>[\d\s\-\.]+)(?P<TIPO>(?>.*$\s){1,3}?)(?:(?P<PARTES>" + partes + "(?>.*$\s)+?)(?:(?P<TEXTO>(?:O|A)?\s*+EXM(.*$\s){1,}?)Numera[çc][ãa]o))"
        # self.regex_cabecalho_pre201503 = "\s*+Este\s*+documento\s*+pode\s*+ser\s*+verificado(?:.*$\s)+?ISSN.*$"



    # def extrai_trf1(self, texto_arquivo):
    #     for m in re.finditer(self.regex_trf1_teste, texto_arquivo, flags=re.I|re.M|re.U|re.X):
    #         self.count3 += 1
    #         self.ultimos.add(m.group("ultima").trim())

    # def get_insert(self, tabela, dados):
    #
    #     c = dados[0].keys()
    #     c = sorted(c)
    #
    #     c = ",".join(c)
    #
    #     valores = ""
    #     for d in dados:
    #         v = "("
    #         for campo in c.split(','):
    #             v += "'{}',".format(d[campo].replace("'",'"'))
    #         v = v[:-1] + "),"
    #         valores += v
    #
    #     valores = valores[:-1]
    #
    #     sql = "INSERT INTO desenv_bpc.{TABELA}({CAMPOS}) VALUES {VALORES};".format(TABELA=tabela, CAMPOS=c, VALORES=valores)
    #
    #     return sql

    # def extraiUnico(self):
    #     return True

    # @profile
    # def extraiAtuais(self):
    #
    #     arquivo = self.pular_arquivo_mal_convertido(self.regex_cabecalho)
    #
    #     # print(datetime.datetime.now(), self._arquivo.name)
    #
    #     if arquivo:
    #
    #         if "TRF1" in self._arquivo.name:
    #             # self.extrai_trf1(arquivo)
    #             # print(self.count3)
    #             # print(self.ultimos)
    #             return True
    #         else:
    #
    #             estado = re.search("TRF01_JUD_SJ(..)",
    #                              self._arquivo.name.split('\\')[-1]).group(1)
    #
    #             data = re.search("TRF01_JUD_SJ.._(\d\d\d\d_\d\d_\d\d)",
    #                              self._arquivo.name.split('\\')[-1]).group(1)
    #
    #             self.extrai_distribuicoes(arquivo,  self.regex_distribuicao2, data, estado)
    #             self.extrai_distribuicoes(arquivo,  self.regex_distribuicao3, data, estado)
    #
    #             # self.extrai_publicacoes(arquivo, pubDao, self.regex_publicacao)
    #             # extração de publicações suspensa.
    #
    #             return True
    #
    #     else:
    #         print("Encontrado erro de conversão no arquivo", self._arquivo.name)
    #         return False

    # @profile
    def extrai(self,tag=None):

        # with open(self._arquivo.name, encoding='latin-1', mode='r', errors="ignore") as file:
        #     texto_arquivo = file.read()
        texto_arquivo = self._arquivo.read()

        if texto_arquivo:

            proc_temp_service = ProcTempService()
            proc_temp_tag_service = ProcTempTagService()

            if tag:
                currTag = tag
            else:
                currTag = proc_temp_tag_service.dao.get_por_tag(os.path.basename(self._arquivo.name).split('_')[0] + '_pre')

            k = 0

            for m in re.finditer(self.regex_npu, texto_arquivo, flags=self.flags):

                k += 1

                p = ProcTemp()
                p.numero = m.group(0).replace(' ', '')
                print(p.numero)

                if re.search(RegexUtil.npu_trfs, m.group(0), self.flags):
                    p.is_npu = True
                    p.numero = p.numero.zfill(20)
                    p.ano = int(re.search('(\d{4})\d{7}$', p.numero).group(1))
                else:
                    p.is_npu = False
                    p.ano = int(re.search('^(\d{4})', p.numero).group(1))


                p.tag = currTag
                p.versao = self.versao
                p.arquivo_origem = self._arquivo_bd

                # p.tag = re.search('([\w\d\_]+)\.', self._arquivo.name).group(1).split('_')[0]+'_pre'
                # os.path.basename(self._arquivo.name).split('_')[2]
                # p.dado_entrada = os.path.basename(self._arquivo.name)

                proc_temp_service.salvar(p, commit=False)

                if k == 300:
                    k = 0
                    proc_temp_service.dao.commit()

            proc_temp_service.dao.commit()

            return True
        else:
            return False


    # def extrai2009_2015(self):
    #
    #     arquivo = self.limpa_cabecalhos(self.regex_cabecalho_pre201503)
    #
    #
    #     # pubDao = PublicacaoDao()
    #
    #     # print(datetime.datetime.now(), self._arquivo.name)
    #
    #     if arquivo:
    #
    #         if "TRF1" in self._arquivo.name:
    #             # self.extrai_trf1(arquivo)
    #             # print(self.count3)
    #             # print(self.ultimos)
    #             return True
    #         else:
    #
    #             secoes = []
    #
    #             curr = 0
    #
    #             for m in re.finditer(self.regex_split_secoes, arquivo, self.flags):
    #                 secoes.append(arquivo[curr:m.start()])
    #                 curr = m.start()
    #
    #             secoes.append(arquivo[curr:])
    #
    #             secoes = secoes[1:]
    #
    #             for secao in secoes:
    #                 estado = re.search(self.regex_split_secoes, secao, self.flags).group(1)
    #                 estado = self.aux_dict_estados[remove_varios_espacos(remove_acentos(estado.lower()))]
    #                 data = re.search("TRF01_COMPLETO_(\d\d\d\d_\d\d_\d\d)",
    #                                     self._arquivo.name.split('\\')[-1]).group(1)
    #                 self.extrai_distribuicoes(secao, self.regex_distribuicao_pre20153, data, estado)
    #                 self.extrai_distribuicoes(secao, self.regex_distribuicao3, data, estado)
    #                 # self.extrai_publicacoes(secao, pubDao, self.regex_publicacao_pre201503, data, estado)
    #                 # não vamos extrair publicações.
    #
    #             return True
    #
    #     else:
    #         print("Encontrado erro de conversão no arquivo", self._arquivo.name)
    #         return False

    def trata_classe(self, classe):
        return re.sub("\s\s", " ", classe.strip().upper().replace("AUTOR","").strip())

    # # @profile
    # def extrai_distribuicoes(self, texto_arquivo, regex, datastr, uf):
    #
    #     count = 0
    #     for m in re.finditer(regex, texto_arquivo, flags=self.flags):
    #
    #         d = Distribuicao()
    #
    #         data_diario = datetime.datetime.strptime(datastr, "%Y_%m_%d")
    #         data_publicacao = data_diario
    #
    #         # print(self._arquivo.name.split('\\')[-1],self.trata_classe(m.group("CLASSE")))
    #
    #         try:
    #             self.preenche_dicionario_distribuicao(d, self.trata_classe(m.group("CLASSE")), 'TRF01', data_diario,
    #                                        self.get_nome_caderno(), '-', uf,
    #                                        data_publicacao,
    #                                        m.group("NUM"), # NPU !!!!!
    #                                        # num_antigo.group(0).strip() if num_antigo else None,
    #                                        None,
    #                                        "OUTRAS", "-", "BPC", False)
    #
    #             # count += 1
    #             #
    #             # if count > 10:
    #             #     distDao.flush()
    #             #     count = 0
    #
    #         except Exception as e:
    #             print(e)
    #
    #     # print("Inseridos:", count)

    # def extrai_npu(self, regex):
    #
    #     # texto_arquivo = self.pular_arquivo_mal_convertido(self.regex_cabecalho) #nao limpa cabeçalho na vdd verifica se a conversao foi feita corretamente


    # # @profile
    # def extrai_publicacoes(self, texto_arquivo, pubDao, regex, datastr, uf):
    #
    #     for m in re.finditer(regex, texto_arquivo, flags=self.flags):
    #
    #         p = Publicacao()
    #         data_diario = datetime.datetime.strptime(datastr, "%Y_%m_%d")
    #         data_publicacao = data_diario
    #
    #         print(self._arquivo.name.split('\\')[-1], self.trata_classe(m.group("TIPO")))
    #
    #
    #         self.preenche_publicacao(p, self.trata_classe(m.group("TIPO")), "", 'TRF01', data_diario, self.get_nome_caderno(),
    #                                  '-', uf, data_publicacao, m.group("NUM").strip(), "", "-", "BPC", None)
    #
    #         p.texto = m.group("TEXTO")
    #
    #         pubDao.salvar(p, caderno=p.caderno, tag="BPC", commit=False)
    #
    #     pubDao.commit()




    def pular_arquivo_mal_convertido(self, regex):

        with open(self._arquivo.name, encoding='utf-8', mode='r', errors="ignore") as file:

            try:
                f = file.read()

                # f, num = re.subn(regex, " \n", f, flags=self.flags)

                # if num == 0:
                #     f, num = re.subn(self.regex_cabecalho_pre201503, " ", f, flags=re.I|re.M|re.U|re.X)

                if re.search(self.regex_skip_bad_conversion, f, flags=self.flags):
                    return None

                # não lembro pq pus isso aqui
                # if re.search("Autos\scom\sOrdinatório:\sAUDIÊNCIAS\sDE\sCONCILIAÇÃO\sDESIGNADAS", f, flags=re.I|re.M|re.U|re.X):
                #     f = f.split("Autos com Ordinatório: AUDIÊNCIAS DE CONCILIAÇÃO DESIGNADAS")[0]

                return f

            except Exception as e:
                print("Erro ao limpar cabeçalhos")
                return None

    def cria_lista_de_linhas(self):
        pass
    def identifica_data_cabecalho(self):
        pass
    def is_edital(self):
        pass
    def procura_processos_falencia(self):
        pass
    def salva_dados(self):
        pass

    def get_caderno(self):
        diario = os.path.basename(self._arquivo.name)

        try:
            data = datetime.datetime.strptime(re.search("(\d{4}_\d{2}_\d{2}).*?\.txt", diario).group(1),
                                              "%Y_%m_%d")
        except:
            data = None
            ConfigManager().escreve_log('Data invalida para ' + diario + '. Pulando...',
                                        self._acompanhamento.nome, self.__erro)

        diario = DiarioService().preenche_diario('TRF01', data)

        caderno = CadernoService().preenche_caderno(self.get_nome_caderno(),diario)

        return caderno

    def get_nome_caderno(self):

        return '_'.join(self._arquivo.name.split('_')[1:3])

if __name__ == '__main__':

    try:
        param = sys.argv[1]
    except:
        param = "processar"

    p = ProcessaExtrator("TRF05", "ata", ExtratorTRF, None)

    if param == "listar":
        # listar todos os arquivos do TRF1 que não foram processados ainda
        p.extrai_diversos(tag=sys.argv[2])
    else:
        p.extrai_arquivo(param, [param.split("_")[0]], extrai_extraido=False)

        # for ano in range(2017, 2018):
        # # for ano in range(2014, 2015):
        #     for mes in range(12, 13):
        #         print("Processando {}/{}".format(ano, mes))
        #         p.extrai_diversos_diretorio('C:\\Users\\e279274021\\Desktop\\TRF\\TRF5\\{ANO}\\{MES}'.format(ANO=str(ano), MES="{:02d}".format(mes)), 'TRF05_')
        #         # p.extrai_diversos_diretorio(
        #         #   'Z:\\TRF\\TRF01\\txt\\{ANO}\\{MES}'.format(ANO=str(ano), MES="{:02d}".format(mes)), 'TRF01_COMPLETO_2014_01_15')
        #         # p.extrai_diversos_diretorio(
        #             #     '..\\..\\dados',
        #             #     'TRF01_COMPLETO_2014_02_06')