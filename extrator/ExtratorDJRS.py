# -*- coding: utf-8 -*-

import re
import datetime
from extrator.ExtratorBase import ExtratorBase
from classificadores.ClassificaEdital import ClassificaEdital
from acompanhamento_processual.AcompanhamentoProcessualRS import AcompanhamentoProcessualRS
from extrator.ProcessaExtrator import ProcessaExtrator

class ExtratorDJRS(ExtratorBase):
    nome_diario = "DJRS"

    def __init__(self, arquivo, acompanhamento,arquivo_bd = None):
        super(ExtratorDJRS, self).__init__("DJRS", arquivo, acompanhamento, ClassificaEdital(), arquivo_bd)

    def get_caderno(self):
        arq = self._arquivo.name.upper()

        if 'CAPITAL_1_GRAU' in arq:
            return 'CAPITAL 1o GRAU'
        elif 'CAPITAL_2_GRAU' in arq:
            return "CAPITAL 2o GRAU"
        elif 'INTERIOR_1_GRAU' in arq:
            return "INTERIOR 1o GRAU"
        elif 'EDITAIS_1_e_2' in arq:
            return "EDITAIS 1o E 2o GRAU"
        elif 'EDITAIS' in arq:
            return "EDITAIS"
        elif 'COMARCAS_DO_INTERIOR' in arq:
            return "COMARCAS DO INTERIOR"
        elif "ADMINISTRATIVA_E_JUDICIAL" in arq:
            return "ADMINISTRATIVA E JUDICIAL"
        elif 'EXTRA' in arq:
            return 'EXTRA'
        elif "FORO_CENTRAL_E_REGIONAIS" in arq:
            return "FORO CENTRAL E REGIONAIS"
        elif "TRIBUNAL_DE_JUS" in arq:
            return "TRIBUNAL DE JUSTICA"
        else:
            return None


    def identifica_data_cabecalho(self,expressao_cabecalho,linha_atual):
        cabecalho_match = re.search(expressao_cabecalho,linha_atual)
        return cabecalho_match.group(2) if (cabecalho_match.group(2) is not None) else cabecalho_match.group(4)

    def salva_dados(self,processos):
        pass

    def cria_lista_de_linhas(self):
        if self.is_capital():
            return self.cria_lista_de_linhas_capital()
        elif self.is_interior():
            return self.cria_lista_de_linhas_interior()
        elif self.is_edital():
            return self.cria_lista_de_linhas_edital()
        else:
            return None,None


    # Verificar necessidade de outras expressões
    # Incompleto.
    def cria_lista_de_linhas_edital(self):
        expressao_cabecalho = re.compile(
            '.*(\w*\d* *\/ *.*\w*-feira,? *(\d+ *.* *\w* *\d+))|(\w*-feira,? *(\d+ *.* *\w* *\d+) *\/ *.*\d*)')
        lista_expressoes_ignoradas = []

        expressao_diario = re.compile('DI.RIO  DA  JUSTI.A  ELETR.NICO-RS')
        lista_expressoes_ignoradas.append(expressao_diario)

        separador = ''
        return super(ExtratorDJRS, self).cria_lista_de_linhas_com_separador_igual_a_linha(expressao_cabecalho, lista_expressoes_ignoradas, None, separador)

    def cria_lista_de_linhas_interior(self):
        expressao_cabecalho = re.compile(
            '.*(\w*\d* *\/ *.*\w*-feira,? *(\d+ *.* *\w* *\d+))|(\w*-feira,? *(\d+ *.* *\w* *\d+) *\/ *.*\d*)')
        lista_expressoes_ignoradas = []

        expressao_encarte = re.compile(
            "ENCARTE *COMARCAS *DO *INTERIOR")
        lista_expressoes_ignoradas.append(expressao_encarte)

        expressao_data = re.compile("^.*, *\d{1,2} *DE *.* *DE *20[01]\d")
        lista_expressoes_ignoradas.append(expressao_data)

        expressao_nota_expediente = re.compile(
            "NOTA *DE *EXPEDIENTE *N. *\d*\/\d{4}")
        lista_expressoes_ignoradas.append(expressao_nota_expediente)

        expressao_diario = re.compile("DI.RIO *D. *JUSTI.A")
        lista_expressoes_ignoradas.append(expressao_diario)

        expressao_vara = re.compile(".*VARA.*COMARCA.*")
        lista_expressoes_ignoradas.append(expressao_vara)

        separador = ''
        return super(ExtratorDJRS, self).cria_lista_de_linhas_com_separador_igual_a_linha(expressao_cabecalho, lista_expressoes_ignoradas, None, separador)

    def cria_lista_de_linhas_capital(self):
        expressao_cabecalho = re.compile(
            '.*(\w*\d* *\/ *.*\w*-feira,? *(\d+ *.* *\w* *\d+))|(\w*-feira,? *(\d+ *.* *\w* *\d+) *\/ *.*\d*)')

        lista_expressoes_ignoradas = []

        expressao_nota_expediente = re.compile("NOTA *DE *EXPEDIENTE *N. *\d*\/\d{4}")
        lista_expressoes_ignoradas.append(expressao_nota_expediente)

        busca_vara_especializada = re.compile('(?i)VARA DE FAL.NCIAS E CONCORDATAS.*')

        separador = ''
        return super(ExtratorDJRS, self).cria_lista_de_linhas_com_separador_igual_a_linha(expressao_cabecalho, lista_expressoes_ignoradas, busca_vara_especializada, separador)

    # TODO buscar cnpj de falência
    # Atualmente ele apenas procura qualquer CNPJ independente de ser de falência
    def procura_cnpj_falencia(self,lista_de_linhas):
        expressaoCNPJ = re.compile("(\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2})")
        lista_cnpj = []
        for item in lista_de_linhas:
            if expressaoCNPJ.search(item):
                lista_cnpj.append(expressaoCNPJ.search(item).group(0))
        return lista_cnpj

    def procura_processos_falencia(self, lista_de_linhas):
        if self.is_capital():
            return self.procura_processos_falencia_capital(lista_de_linhas),None
        elif self.is_interior_atual():
                return self.procura_processos_falencia_interior_atual(lista_de_linhas),None
        elif self.is_interior_antigo():
            return self.procura_processos_falencia_interior_antigos(lista_de_linhas),None
        elif self.is_edital():
            return self.procura_processos_falencia_edital(lista_de_linhas)
        return None,None


    def procura_processos_falencia_interior_atual(self,lista_de_linhas):
        expressaoFalencia = re.compile("([ ]*((PEDIDO[ ]*DE[ ]*)|[ ]*AUTO)?FAL.NCIA)|([ ]*CONCORDATA)|([ ]*RECUPERA..O[ ]*JUDIC)|[ ]*(CONCURSO DE CREDORES)|[ ]*(RELAT.RIO[ ]*FALIMENTAR)|([ ]*CONVOLA.{2}O)|[ ]*CLASSIFICA..O[ ]*DE[ ]*CR.DITOS")
        expressaoProcesso = re.compile("^(\d{3}[\/]\d[\.]\d{2}[\.]\d{7}[-]\d).*")
        expressaoMassaFalida = re.compile("(M(ASSA)?\.?([ ]*FALIDA)|MASSA[\.,:-;])")
        expressaoTrava = re.compile("TRAVA[ ]*BANC.RIA")
        expressaoEncerra = re.compile("[E][N][C][E][R][R][A][D].[ ]*[A]?[ ][R][E][C][U][P][E][R][A].{2}[O][ ]*[J][U][D][I][C][I][A][L]")
        expressaoFalDecret = re.compile("[D][E][C][R][E][T].{0,4}[ ]*.{0,4}([F][A][L].[N][C][I][A])(.*)")
        expressaoConvolacao = re.compile("[C][O][N][V][O][L][A]")
        expressaoSindico = re.compile("((S.NDIC[OA]([^TNL]))|(ADMINISTRADOR[A]?[ ]* JUD))")
        expressaoFalimentar = re.compile("FAL(IMENTAR|.NCI.L?|ID)")
        expressaoCredores = re.compile("(QUADRO|ASSEMBL.IA)[ ]*(GERAL)?[ ]*(DE)?[ ]*CREDOR")
        expressaoCred = re.compile("CREDOR((A)|(ES))?[ ]*((PRIVILEGIAD)|(PREFERENCIA))")
        expressaoHabCred = re.compile("HABILITA.{1,2}O[ ]*((DE)|(O))?[ ]*((CR.DITO)|(RETARDAT))")
        expressaoLei = re.compile("11[\.]?101")
        expressaoQuirograf = re.compile("QUIROGRAF")
        processosFalencia = []
        titulo = ''
        for item in lista_de_linhas:
            falenciaMatch = expressaoFalencia.search(item)
            massaMatch = expressaoMassaFalida.search(item)
            encerraMatch = expressaoEncerra.search(item)
            falDecretMatch = expressaoFalDecret.search(item)
            convolacaoMatch = expressaoConvolacao.search(item)
            sindicoMatch = expressaoSindico.search(item)
            falimentarMatch = expressaoFalimentar.search(item)
            credoresMatch = expressaoCredores.search(item)
            habCredMatch = expressaoHabCred.search(item)
            quirografMatch = expressaoQuirograf.search(item)
            credMatch = expressaoCred.search(item)
            travaMatch = expressaoTrava.search(item)
            leiMatch = expressaoLei.search(item)
            if (falenciaMatch or massaMatch or encerraMatch or falDecretMatch or
                    convolacaoMatch or sindicoMatch or falimentarMatch or credoresMatch or habCredMatch or
                    leiMatch or quirografMatch or credMatch or travaMatch):
                processoMatch = expressaoProcesso.search(item)
                if processoMatch:
                    processosFalencia.append(processoMatch.group(1))
        return processosFalencia

    def procura_processos_falencia_interior_antigos(self,lista_de_linhas):
        achou_falencia = False
        #expressão para lista de massas falidas
        # expressao_Massa_Falida = re.compile(
        # ".*(?i)([M][-]?[ ]?[A][-]?[ ]?[S][-]?[ ]?[S][-]?[ ]?[A][-]?[ ]?[ ][-]?[ ]?[F][-]?[ ]?[A][-]?[ ]?[L][-]?[ ]?[I][-]?[ ]?[D][-]?[ ]?[A][-]?[ ]?).*")
        expressao_falencia = re.compile("^([ ]*((PEDIDO[ ]*DE[ ]*)|^[ ]*AUTO)?FAL.NCIA)|^([ ]*CONCORDATA)|^([ ]*RECUPERA..O[ ]*JUDIC)|^[ ]*(CONCURSO DE CREDORES)|^[ ]*(RELAT.RIO[ ]*FALIMENTAR)|^([ ]*CONVOLA.{2}O)|^[ ]*CLASSIFICA..O[ ]*DE[ ]*CR.DITOS")
        expressao_processo = re.compile("^(\d{3}[\/]\d[\.]\d{2}[\.]\d{7}[-]\d).*")
        lista_processos = []
        qtd_encontrada = 0
        titulo = ''

        for item in lista_de_linhas:
            falencia_match = expressao_falencia.search(item)
            if achou_falencia:
                processo_match = expressao_processo.search(item)
                if processo_match:
                    qtd_encontrada+=1
                    lista_processos.append(processo_match.group(1))
                else:
                    achou_falencia = False
            elif falencia_match:
                achou_falencia = True
                titulo = item
            else:
                achou_falencia = False
        #pensar em inserir no log
        # for k,v in map_titulo_processos.items():
        #     qtd_processos_da_classe_k = 0
        #     for processo in v:
        #         qtd_processos_da_classe_k+=1
        #     print str(qtd_processos_da_classe_k) +" processos da classe: "+k+" foram encontrados."
        return lista_processos


    def procura_processos_falencia_capital(self, lista_de_linhas):
        expressao_processos = re.compile("^(\d{3}[\/]\d[\.]\d{2}[\.]\d{7}[-]\d).*")
        expressao_vara = re.compile("(?i)[V][A][R][A].*[F][A][L].[N][C][I][A][S].*[C][O][M][A][R][C][A].*")
        expressao_data = re.compile(".*[,][ ]*\d{1,2}[ ]*[D][E][ ]*\w*[ ]*[D][E][ ]*\d{4}")
        expressao_desconsiderada = re.compile('([D][I].[R][I][O][ ]*[D][A][ ]*[J][U][S][T][I].[A].*)|(.*[(].*)|(.*[)].*)')
        lista_processos = []
        encontrou_vara = False
        titulo = ''
        for item in lista_de_linhas:
            if encontrou_vara:
                processo_match = expressao_processos.search(item)
                if processo_match:
                    lista_processos.append(processo_match.group(1))
                else:
                    data_match = expressao_data.search(item)
                    if data_match:  # este caso ocorre quando acaba a lista de processos da vara
                        encontrou_vara = False
            else:
                vara_match = expressao_vara.search(item)
                if vara_match:
                    encontrou_vara = True
                else:
                    encontrou_vara = False
        return lista_processos

    def procura_processos_falencia_edital(self, lista_de_linhas):
        expressao_falencia = re.compile(".*[Ff][Aa][Ll].[Nn][Cc][Ii][Aa].*")
        expressao_processos = re.compile(".*(\d{3}[\/]\d[\.]\d{2}[\.]\d{7}[-]\d).*")


        lista_processos = []
        map_editais = {}
        encontrou_falencia = False
        titulo = ''
        for item in lista_de_linhas:
            falencia_match = expressao_falencia.search(item)
            if falencia_match:
                processo_match = expressao_processos.search(item)
                if processo_match:
                    processo = processo_match.group(1)
                    lista_processos.append(processo)
                    if processo in list(map_editais.keys()):
                        map_editais[processo].append(item)
                    else:
                        map_editais.update({processo : [item]})

        return lista_processos,map_editais

    def is_capital(self):
        return self.is_capital_primeiro_grau() or self.is_capital_segundo_grau()

    def is_capital_primeiro_grau(self):
        expressao_nome = re.compile('(\d{4}_7\.)|(.*_Capital_1_)')
        return True if expressao_nome.search(self._arquivo.name) else False

    def is_capital_segundo_grau(self):
        expressao_nome = re.compile('(\d{4}_5\.)|(.*_Capital_2_)')
        return True if expressao_nome.search(self._arquivo.name) else False
    #adm _0
    # capital segunda inst_5 e  prim inst _7
    #interior 6
    #editais _8
    #militar 9

    def is_administrativo_e_judicial(self):
        expressao_nome = re.compile('(\d{4}_0\.)|(.*_Administrativa_e_Judicial)')
        return True if expressao_nome.search(self._arquivo.name) else False

    def is_edital(self):
        if self._arquivo.name.endswith('_8.txt'):
            return True
        if re.search('Editais_1_e_2_Grau',self._arquivo.name):
            return True
        return False

    def is_interior(self):
        return self.is_interior_atual() or self.is_interior_antigo()

    def is_interior_atual(self):

        expressao_nome_por_extenso = re.compile('.*_Interior_1_')
        expressao_nome_por_codigo = re.compile('(\d{4})_6\.')
        if expressao_nome_por_extenso.search(self._arquivo.name):
            data_caderno = self.pega_data_caderno_nome_arquivo()

            if data_caderno:
                data_caderno = datetime.datetime.strptime(data_caderno, "%Y_%m_%d")
                if data_caderno.date() >= datetime.date(2011,2,11):
                    return True
                else:
                    return False
        match_nome_por_codigo = expressao_nome_por_codigo.search(self._arquivo.name)
        if match_nome_por_codigo:
            if int(match_nome_por_codigo.group(1)) >= 4517:
                return True
            else:
                return False
        return False

    def is_interior_antigo(self):
        expressao_nome_por_codigo = re.compile('(\d{4})_6\.')
        return True if expressao_nome_por_codigo.search(self._arquivo.name) else False
        #Existe uma ordem de precedência onde o is_interior_atual deve ser chamado antes do is_anterior_antigo

if __name__ == '__main__':
    p = ProcessaExtrator("DJRS", "txt", ExtratorDJRS, AcompanhamentoProcessualRS)
    p.extrai_diversos()