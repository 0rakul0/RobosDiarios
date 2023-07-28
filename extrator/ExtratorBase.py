# -*- coding: utf-8 -*-

from datetime import datetime
import re, abc
from functools import reduce

import os

from pdjus.service.ArquivoService import ArquivoService
from pdjus.service.AssuntoService import AssuntoService
from pdjus.service.CadernoService import CadernoService
from pdjus.service.ClasseProcessualService import ClasseProcessualService
from pdjus.service.ComarcaService import ComarcaService
from pdjus.service.DiarioService import DiarioService
#from pdjus.service.DistribuicaoService import DistribuicaoService
from pdjus.service.EmpresaService import EmpresaService
from pdjus.service.EstadoService import EstadoService
from pdjus.service.ParteDistribuicaoService import ParteDistribuicaoService
from pdjus.service.PublicacaoService import PublicacaoService
from util.ConfigManager import ConfigManager
from util.StringUtil import remove_acentos,remove_quebras_linha_de_linha, remove_varios_espacos,remove_tracos_pontos_barras_espacos
from util.NumeroUtil import calculo_dv_cnpj

class ExtratorBase(metaclass=abc.ABCMeta):
    def __init__(self, robo, arquivo, acompanhamento, validador_edital,arquivo_bd = None):
        self._arquivo = arquivo
        self._arquivo_bd = arquivo_bd
        self.__robo = robo
        self._acompanhamento = acompanhamento
        self._validador_edital = validador_edital
        self.__log = "log_extrator.txt"
        self.__erro = "erro_extrator.txt"


    @abc.abstractmethod
    def cria_lista_de_linhas(self):
        pass

    @abc.abstractmethod
    def is_edital(self):
        pass

    @property
    def nome_diario(self):
        return self.__robo

    @property
    def data_caderno(self):
        data = None
        str_data = self.pega_data_caderno_nome_arquivo()

        if str_data:
            data = datetime.strptime(str_data, '%Y_%m_%d')

        return data

    def verifica_empresas_no_caderno(self,lista_de_linhas,realiza_busca_empresa_banco=False):
        empresa_service = EmpresaService()
        for linha in lista_de_linhas:
            # Se descomentar a parte de baixo sobre apenas o uso do cnpj for fracasso, retirar as linhas entre esse comentário e o próximo
            lista_cnpj = self.procura_empresa_e_cnpj_pelo_edital(linha)
            for cnpj in lista_cnpj:
                cnpj_com_digito = calculo_dv_cnpj(remove_tracos_pontos_barras_espacos(cnpj))
                if realiza_busca_empresa_banco:
                    empresa = empresa_service.dao.get_por_cnpj(cnpj)
                    if empresa:
                        print("Empresa {} com CNPJ {}, já consta em nosso banco".format(empresa.nome, empresa.cnpj))
                if not empresa or not empresa.nome:
                    print("Buscando o cnpj {} no acompanhamento_processual".format(cnpj_com_digito))
                    self._acompanhamento.consulta_pagina_cnpj(cnpj_com_digito,self._arquivo.name)

            #TODO Descomentar se método com apenas CNPJ for fracasso
            ##nome, cnpj
            # map_cnpj_nomes = self.procura_empresa_e_cnpj_pelo_edital(linha)
            # for cnpj, nomes in list(map_cnpj_nomes.items()): #cnpj -> [nome1,nome2]
            #     if cnpj:
            #         cnpj = calculo_dv_cnpj(remove_tracos_pontos_barras_espacos(cnpj))
            #         if cnpj:
                        # for nome in nomes: #aqui tem cnpj,nome
                        # #após verificação de cnpj ter dado certo...
                        #     if nome:
                        #         empresa = empresaDao.get_por_nome_e_cnpj(nome,cnpj)
                        #     else:
                        #         empresa = empresaDao.get_por_cnpj(cnpj)
                        #     if not empresa:
                        #         empresa = Empresa()
                        #         empresa.cnpj = cnpj
                        #         if nome:
                        #             empresa.nome = nome
                        #             print("Empresa {} - CNPJ {}".format(empresa.nome,empresa.cnpj))
                        #         else:
                        #             print("CNPJ {}".format(empresa.cnpj))
                        #         empresaDao.salvar(empresa)
                        #     else:
                        #         if nome and not empresa.nome:
                        #             empresa.nome = nome
                        #             print("Empresa {} - CNPJ {}".format(empresa.nome,empresa.cnpj))
                        #             empresaDao.salvar(empresa)


    def extrai(self,tag=None,):
        diario_service = DiarioService()
        caderno_service = CadernoService()
        arquivo_service = ArquivoService()

        f = open("lista_processos.txt", mode='a',encoding="utf8")
        try:
            #print("Extraindo {}".format(self._arquivo.name))
            ConfigManager().escreve_log(
                "Extraindo {}".format(self._arquivo.name),
                self._acompanhamento.nome, self.__log)
            lista, data_caderno = self.cria_lista_de_linhas()
            if not lista: #se não tiver extrator, ele diz que foi extraído para não ficar tentando extrair toda vez
                return True
            # if self.is_edital(): #Antes só verificava as empresas no edital, agora em qualquer caderno e bate no sistema se não tivermos no banco.
            # self.verifica_empresas_no_caderno(lista,True)
            num_processos,editais = self.procura_processos_falencia(lista)
            if (data_caderno):
                #print("Data caderno {}".format(str(data_caderno)))
                f.write("Data caderno {}\n".format(str(data_caderno)))
            processou_algum_processo = False
            if num_processos:
                diario = diario_service.preenche_diario(self.__robo, data_caderno)

                caderno = self.get_caderno()

                if self._arquivo_bd:
                    self._arquivo_bd = arquivo_service.preenche_arquivo(self._arquivo_bd.nome_arquivo, diario, caderno)


                num_processos = list(set(num_processos))#remove duplicados
                #print('Encontrei {} processos'.format(len(num_processos)))
                for num_processo in num_processos:
                    #print(num_processo)
                    f.write(num_processo + '\n')
                    processo = self._acompanhamento.gera_arvore_processos(num_processo, tag='FALENCIAS', somente_falencias=True, caderno=caderno)
                    if processo:
                        processou_algum_processo = True
                        # ACHO QUE NÃO É MAIS NECESSÁRIO
                        # if editais:
                        #     for processo,edital in list(editais.items()):
                        #         self._validador_edital.valida(processo,edital[0])

            return processou_algum_processo
            # else:
            #     return False
        except Exception as e:
            ConfigManager().escreve_log("ERROR: "+ str(e), self._acompanhamento.nome, self.__erro)
            raise e
            return False
        finally:
            f.close()

    def concatena_linhas(self, linha_atual, lista, ultima_posicao):
        if len(lista) > 1 and lista[ultima_posicao][-1] == '-' and lista[ultima_posicao][-2] != ' ':
            lista[ultima_posicao] = lista[ultima_posicao][:-1]
            lista[ultima_posicao] = lista[ultima_posicao] + linha_atual
        else:
            lista[ultima_posicao] = lista[ultima_posicao] + " " + linha_atual

        return lista

    def ignora_numero_de_pagina(self, linha_anterior, linha_atual):
        if linha_atual.isdigit():
            ignora_linha= True
            linha_atual = linha_anterior
        else:
            ignora_linha = False
        return linha_atual, ignora_linha

    def procura_empresa_e_cnpj_pelo_edital(self,texto):
        frase = remove_varios_espacos(remove_quebras_linha_de_linha(remove_acentos(texto)))
        expressao_cnpj = re.compile('(C\.? *N\.? *P\.? *J).{0,30}?\D(?<![-\d])([0-9]{2}[\. ]*?[0-9]{3}[\. ]*?[0-9]{3}[ \/]*?[0-9]{4}[\- ]*[0-9]{0,2})(\D|$)')
        # Se descomentar a parte de baixo sobre apenas o uso do cnpj for fracasso, retirar as linhas entre esse comentário e o próximo
        lista_cnpjs = []
        cnpj_match = expressao_cnpj.findall(frase)
        for match in cnpj_match:
            if not match[1] in lista_cnpjs:
                lista_cnpjs.append(match[1])
        return lista_cnpjs
        #TODO Descomentar se método com apenas CNPJ for fracasso
        # expressao_faz_saber = re.compile('[Ff][Aa][Zz] *[Ss][Aa][Bb][Ee][Rr] *([AÀaà]?\(?o?\)?s? *(((requerid)|(interessad)|(empresa)|(executad))(o?\(?a?\)?s?))? *(.{0,100}?((E\.? *I\.? *R\.? *E\.? *L\.? *I)|(M\.? *E\.? *I?)|(E\.? *P\.? *P)|(S[]\/\. ]*A)|(L\.? *T\.? *D\.? *A?)|(EBBA)|(EBAB)|(Microempresa)|(Empresa *de *Pequeno *Porte)|(Empresa *Binacional *Brasileiro[- ]*Argentina)|([Ff]irma [Ii]ndividual)))[ ,\.\;-]*?.*?(C\.? *N\.? *P\.? *J).{0,30}?([0-9]{2}[\. ]*[0-9]{3}[\. ]*[0-9]{3}[ \/]*[0-9]{4}[\- ]*[0-9]{0,2}))(\D|$)', re.IGNORECASE)
        # expressao_empresas_cnpj_uppercase = re.compile('((REQUERID[AO]? ?\(?[AO]?\)?S?)? *(FALENCIA)|CITACAO|) *(DE)? *((.*?((E\.? *I\.? *R\.? *E\.? *L\.? *I)|([Mm]\.? *[Ee]\.? *[Ii]?)|([Ee]\.? *[Pp]\.? *[Pp])|([Ss][\/\. ]*? *[Aa])|([Ll]\.? *[tT]\.? *[Dd]?\.? *[Aa]?)|(EBBA)|(EBAB)|([Mm]icroempresa)|(Empresa *de *Pequeno *Porte)|(Empresa *Binacional *Brasileiro[- ]*Argentina)|([Ff]irma [Ii]ndividual)))[ ,\.\;-]+?.{0,30}?(C\.? *N\.? *P\.? *J).{0,30}?([0-9]{2}[\. ]*?[0-9]{3}[\. ]*?[0-9]{3}[ \/]*?[0-9]{4}[\- ]*[0-9]{0,2}))(\D|$)')
        # expressao_falencia_de = re.compile('(((([fF][Aa][Ll][EeÊê][nN][cC][Ii][Aa])|[Ee][Dd][Ii][Tt][Aa][Ll]) *[dD][eEAaOo])|([Ff][Aa][Ll][Ii][Dd][Aa])) *([Cc][Ii][Tt][Aa][Cc][Aa][Oo] * [Dd]?[Ee]?)?(.{0,50}?([A-Z].{0,100}?((E[\. ]*?I[\. ]*?R[\. ]*?E[\. ]*?L[\. ]*?I)|([Mm][\. ]*?[Ee][\. ]*?[Ii]?)|([Ee]\.? *[Pp]\.? *[Pp])|([Ss][\/\. ]*? *[Aa])|([Ll][\. ]*?[tT][\. ]*?[Dd]?[\. ]*?[Aa]?)|(EBBA)|(EBAB)|([Mm]icroempresa)|(Empresa *de *Pequeno *Porte)|(Empresa *Binacional *Brasileiro[- ]*Argentina)|([Ff]irma [Ii]ndividual)))[ ,\.\;-].+?.{0,30}?(C[\. ]*?N[\. ]*?P[\. ]*?J).{0,30}?([0-9]{2}[\. ]*?[0-9]{3}[\. ]*?[0-9]{3}[ \/]*?[0-9]{4}[\- ]*[0-9]{0,2}))(\D|$)')
        # expressao_executados = re.compile('Executad[oa]s? *?\(?[oas]?\)?: +((.*)(\n?Documentos? +d[oa]s? +Executad[oa]s?\(?[oa]?\)?:?)? * +.*C\.?N\.?P\.?J\.?:? *([0-9]{2}\.?[0-9]{3}\.?[0-9]{3}\/?[0-9]{4}\-?[0-9]{0,2}))(\D|$)',re.IGNORECASE)
        # cnpj_match = expressao_cnpj.search(frase)
        #map_cnpj_nomes = {}
        # while(cnpj_match):
        #     nome =None
        #     cnpj = None
        #     nome_final = None
        #     faz_saber_match = expressao_faz_saber.search(frase)
        #     if faz_saber_match:
        #         nome,cnpj = faz_saber_match.group(9),faz_saber_match.group(23)
        #         frase = frase.replace(faz_saber_match.group(1),'')#retira ocorrência
        #     else:
        #         empresas_uppercase_match = expressao_empresas_cnpj_uppercase.search(frase)
        #         if empresas_uppercase_match:
        #             nome,cnpj =empresas_uppercase_match.group(6), empresas_uppercase_match.group(20)
        #             frase = frase.replace(empresas_uppercase_match.group(5),'')
        #
        #         else:
        #             falencia_de_match = expressao_falencia_de.search(frase)
        #             if falencia_de_match:
        #                 nome,cnpj =falencia_de_match.group(8), falencia_de_match.group(22)
        #                 frase = frase.replace(falencia_de_match.group(7),'')
        #
        #             else:
        #                 executados_match = expressao_executados.search(frase)
        #                 if executados_match:
        #                     nome,cnpj =executados_match.group(2), executados_match.group(4)
        #                     frase = frase.replace(executados_match.group(1),'')
        #                 else:
        #                     cnpj = cnpj_match.group(1)
        #                     frase = frase.replace(cnpj_match.group(1),'')
        #     if nome:
        #         for palavra in nome.split(' '):
        #             if palavra[0].isupper(): #nome deve começar com letra maiuscula
        #                 nome_final = nome[nome.index(palavra):].strip()
        #                 break
        #
        #         if nome_final is not None and nome != nome_final and nome_final !='':
        #             nome = nome_final
        #
        #     if cnpj in list(map_cnpj_nomes.keys()):
        #         if not nome in map_cnpj_nomes[cnpj]:
        #             map_cnpj_nomes[cnpj].append(nome)
        #     else:
        #         map_cnpj_nomes.update({cnpj: [nome]})
        #
        #     cnpj_match = expressao_cnpj.search(frase)
        # return map_cnpj_nomes

    def cria_lista_de_linhas_com_separador_igual_a_linha(self, expressao_cabecalho, lista_expressoes_ignoradas, busca_vara_especializada, separador):
        lista = []
        data_caderno = self.pega_data_caderno_nome_arquivo()

        if data_caderno:
            data_caderno = datetime.strptime(data_caderno, "%Y_%m_%d")

        linha_anterior = ''
        linha_atual = ''
        ignora_linha = False
        continua_pagina_anterior = False
        ultima_posicao = -1 #Usamos a ultima posicao da lista sempre
        encontrou_falencia = False if (busca_vara_especializada) else True #usado quando possui vara especializada

        for line in self._arquivo:
            linha_atual = line.strip('\n').strip('\f')

            if linha_atual != '':
                if encontrou_falencia:
                    if linha_anterior == separador:
                        if continua_pagina_anterior:
                            continua_pagina_anterior = False
                            lista = self.concatena_linhas(linha_atual, lista, ultima_posicao)
                        else:
                            linha_atual, ignora_linha = self.ignora_numero_de_pagina(linha_anterior, linha_atual)
                            if not data_caderno:
                                if expressao_cabecalho:
                                    cabecalho_match = re.search(expressao_cabecalho,linha_atual)
                            if linha_anterior:
                                continua_pagina_anterior = True
                            if not data_caderno and cabecalho_match:
                                data_caderno = cabecalho_match.group(2) if (
                                    cabecalho_match.group(2) is not None) else cabecalho_match.group(4)
                            else:
                                for expressao_ignorada in lista_expressoes_ignoradas:
                                    if re.search(expressao_ignorada,linha_atual):
                                        ignora_linha = True
                                        break
                                if not ignora_linha :
                                    ignora_linha = False
                                    lista.append(linha_atual)
                    else:
                        try:
                            lista = self.concatena_linhas(linha_atual, lista, ultima_posicao)
                        except IndexError:
                            if lista:
                                lista[ultima_posicao] = lista[ultima_posicao] + " " + linha_atual
                            else:
                                lista.append(linha_atual)
                else:
                    vara_match = busca_vara_especializada.search(linha_atual)
                    if vara_match:
                        encontrou_falencia = True
                        lista.append(linha_atual)
            linha_anterior = linha_atual

        return lista,data_caderno

#Se o separador for colocado dentro de um grupo(regex) esse metodo mantem o separador sozinho separado do texto
    def cria_lista_de_linhas_removendo_separador(self,lista_expressoes_ignoradas, separador):
        data_caderno = self.pega_data_caderno_nome_arquivo()

        if data_caderno:
            data_caderno = datetime.strptime(data_caderno, "%Y_%m_%d")
        linhas = self._arquivo.readlines()
        if linhas != []:
            linhas = list(map(lambda x:x.replace('\n','').upper(), linhas))
            linhas_concatenadas = ''
            fatia = 10000
            for i in range(0,int(len(linhas) / fatia)+1):
                if i*fatia < len(linhas):
                    linhas_concatenadas +=(reduce(lambda x, y: x + ' ' + y if not x.endswith('-') else x[:-1]+y, linhas[i*fatia:i*fatia+fatia]))

            for expressao_ignorada in lista_expressoes_ignoradas:
                linhas_concatenadas = expressao_ignorada.sub('',linhas_concatenadas)

            lista_de_linhas = re.split(separador, linhas_concatenadas)
            lista_de_linhas = list(filter(lambda linha: linha and linha != '', lista_de_linhas))
            return lista_de_linhas,data_caderno
        return None, data_caderno

    def cria_lista_de_linhas_mantendo_npu_no_final(self, expressao_cabecalho, lista_expressoes_ignoradas, busca_vara_especializada, separador):
        lista = []
        data_caderno = self.pega_data_caderno_nome_arquivo()

        if data_caderno:
            data_caderno = datetime.strptime(data_caderno, "%Y_%m_%d")
        expressao_separador = re.compile(separador,re.IGNORECASE)
        linha_anterior = ''
        linha_atual = ''
        ignora_linha = False
        continua_pagina_anterior = False
        ultima_posicao = -1 #Usamos a ultima posicao da lista sempre
        encontrou_falencia = False if (busca_vara_especializada) else True #usado quando possui vara especializada

        for line in self._arquivo:
            # nao faço ideia por que esse if estava aqui
            # if len(lista)> 200:
            #     return lista,data_caderno
            separador_match = None
            linha_atual = line.strip('\f').replace('\n','')
            if linha_atual != '' and linha_atual != '\n':
                if encontrou_falencia:
                    if lista !=[]:
                        texto = lista[-1].replace('\n','')+' '+linha_atual.replace('\n','')
                        # separador_match = expressao_separador.search(lista[-1].replace('\n','')+' '+linha_atual.replace('\n',''))
                        separador_match = expressao_separador.search(texto[-300:])
                    else:
                        texto = linha_anterior.replace('\n', '') + ' ' + linha_atual.replace('\n', '')
                        # separador_match = expressao_separador.search(linha_anterior.replace('\n','')+' '+linha_atual.replace('\n',''))
                        separador_match = expressao_separador.search(texto[-300:])
                    if separador_match:
                        linha_atual, ignora_linha = self.ignora_numero_de_pagina(linha_anterior, linha_atual.replace('\n',''))
                        if not data_caderno:
                            if expressao_cabecalho:
                                cabecalho_match = re.search(expressao_cabecalho,linha_atual)
                        if not data_caderno and cabecalho_match:
                            data_caderno = cabecalho_match.group(2) if (
                                cabecalho_match.group(2) is not None) else cabecalho_match.group(4)
                        else:
                            for expressao_ignorada in lista_expressoes_ignoradas:
                                if re.search(expressao_ignorada,linha_atual):
                                    ignora_linha = True
                                    break
                            if not ignora_linha :
                                nova_entrada_na_lista = lista[ultima_posicao].strip() + ' '+linha_atual.replace('\n','').strip()
                                match_linha = expressao_separador.search(nova_entrada_na_lista)
                                lista[ultima_posicao] = nova_entrada_na_lista[:match_linha.end()]
                                linha_atual = lista[ultima_posicao][match_linha.end():].strip()
                                lista.append(linha_atual)

                    else:
                        try:
                            lista = self.concatena_linhas(linha_atual.replace('\n',''), lista, ultima_posicao)
                        except IndexError:
                            if lista:
                                lista[ultima_posicao] = lista[ultima_posicao] + " " + linha_atual
                            else:
                                lista.append(linha_atual)

                        #TODO VERIFICAR SE A MUDANÇA ABAIXO MELHORA!
                                # HOJE a expressão não é ignorada se não der match no separador.
                        # for expressao_ignorada in lista_expressoes_ignoradas:
                        #     if re.search(expressao_ignorada,linha_atual):
                        #         ignora_linha = True
                        #         break
                        # if not ignora_linha:
                        #     try:
                        #         lista = self.concatena_linhas(linha_atual.replace('\n',''), lista, ultima_posicao)
                        #     except IndexError:
                        #         if lista:
                        #             lista[ultima_posicao] = lista[ultima_posicao] + " " + linha_atual
                        #         else:
                        #             lista.append(linha_atual)
                        # else:
                        #    ignora_linha = False
                else:
                    vara_match = busca_vara_especializada.search(linha_atual)
                    if vara_match:
                        encontrou_falencia = True
                        lista.append(linha_atual.replace('\n',''))
            if linha_atual == lista[-1]:
                linha_anterior = ''
            else:
                linha_anterior = linha_atual

        return lista,data_caderno

    @abc.abstractmethod
    def procura_processos_falencia(self,lista_de_linhas):
        pass

    @abc.abstractmethod
    def salva_dados(self,processos):
        return

    def gera_csv_processos_falencia(self):
        pass

    @abc.abstractmethod
    def identifica_data_cabecalho(self, expressao_cabecalho, linha_atual):
        return

    @abc.abstractmethod
    def get_nome_caderno(self):
        pass

    def get_caderno(self):
        diario_service = DiarioService ()
        caderno_service = CadernoService ()
        arquivo_service = ArquivoService ()
        diario = os.path.basename (self._arquivo.name)

        try:
            data = re.search ("(\d{4}_\d{2}_\d{2}).*?\.txt", diario).group (1)
        except:
            data = None
            ConfigManager ().escreve_log ('Data invalida para ' + diario + '. Pulando...',
                                          self._acompanhamento.nome, self.__erro_indice)

        diario = diario_service.preenche_diario (diario, data)

        caderno = caderno_service.preenche_caderno (self.get_nome_caderno (), diario)

        if self._arquivo_bd:
            self._arquivo_bd = arquivo_service.preenche_arquivo (self._arquivo_bd.nome_arquivo, diario, caderno)

        return caderno

    def pega_data_caderno_nome_arquivo(self):
        data = re.search('.*(\d{4}_\d{2}_\d{2})', self._arquivo) if isinstance(self._arquivo,str) else re.search('.*(\d{4}_\d{2}_\d{2})', self._arquivo.name)
        return data.group(1) if (data is not None) else data


    #@profile
    def preenche_dicionario_distribuicao(self, nome_classe, nome_diario, dt_diario, nome_caderno, uf,
                                         dt_pub, npu, num_antigo, tipo_dist, nome_comarca=None, tag=None, partes_distribuicoes=None, vara=None, outros=None):

        distribuicao_dict = {}

        distribuicao_dict['nome_comarca'] = nome_comarca

        distribuicao_dict['nome_classe'] = nome_classe


        distribuicao_dict['nome_diario'] = nome_diario
        distribuicao_dict['dt_diario'] = dt_diario
        distribuicao_dict['diario'] = self._arquivo_bd.diario if self._arquivo_bd else None


        distribuicao_dict['nome_caderno'] = nome_caderno
        distribuicao_dict['caderno'] = self._arquivo_bd.caderno if self._arquivo_bd else None

        distribuicao_dict['uf'] = uf

        distribuicao_dict['numero_processo'] = npu if npu else num_antigo

        distribuicao_dict['dt_pub'] = dt_pub
        distribuicao_dict['outros'] = outros
        distribuicao_dict['tipo_dist'] = tipo_dist
        distribuicao_dict['vara'] = vara
        distribuicao_dict['tag'] = tag

        distribuicao_dict['partes_distribuicoes'] = partes_distribuicoes

        return distribuicao_dict


