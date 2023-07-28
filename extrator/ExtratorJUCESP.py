# -*- coding: utf-8 -*-

import re,io
import ast
import sys
import csv
from datetime import datetime
import json,time
from util.ConfigManager import ConfigManager
from extrator.ExtratorBase import ExtratorBase
from classificadores.ClassificaEdital import ClassificaEdital
from acompanhamento_processual.AcompanhamentoProcessualDJSP import AcompanhamentoProcessualDJSP
from extrator.ProcessaExtrator import ProcessaExtrator
from util.StringUtil import remove_sub_str, possui_numeros, extrai_decimal, remove_acentos,remove_caracteres_especiais, sao_iguais,remove_varios_espacos, remove_pontuacao, remove_quebras_linha_de_linha
from pdjus.service.JuntaComercialService import JuntaComercialService
from pdjus.service.TipoJuntaService import TipoJuntaService
from pdjus.service.CnaeService import CnaeService
from pdjus.service.ObjetoSocialService import ObjetoSocialService
from classificadores.ClassificaCNAE import ClassificaCNAE
from util.RegexUtil import RegexUtil
class ExtratorJUCESP(ExtratorBase):
    nome_diario = "JUCESP"
    def __init__(self, arquivo,acompanhamento,arquivo_bd = None):
        super(ExtratorJUCESP, self).__init__("JUCESP", arquivo, acompanhamento, ClassificaEdital(), arquivo_bd)

    def is_edital(self):
        pass
    def procura_processos_falencia(self,lista_de_linhas):
        pass

    def salva_dados(self,processos):
        return

    def identifica_data_cabecalho(self, expressao_cabecalho, linha_atual):
        return

    def cria_lista_de_linhas(self):
        lista_expressoes_ignoradas = []


        # lista_expressoes_ignoradas.append(re.compile("DIARIO *O. *I?CIAL (JUNTA *COMERCIAL|ESTADO DE SAO PAULO) (.*-FEIRA|.*), *\d* *DE *[A-zçÇ]* *DE *\d{4} *\d* SAO PAULO, *\d* \(\d*\)( \d*)?"))
        # lista_expressoes_ignoradas.append(re.compile("(\d* *.*)?SAO PAULO, *\d* \(\d*\), (.*-FEIRA|.*), *\d*(O)? *DE* *[A-zÇç]* *DE *\d{4}"))
        # lista_expressoes_ignoradas.append(re.compile("(\d*)? D.O.E. * CADERNO JUNTA COMERCIAL, SAO PAULO, *\d* \(\d*\), (.*-FEIRA|.*), *\d*(O)? *DE* *[A-zÇç]* *DE *\d{4}( \d*)?"))
        # lista_expressoes_ignoradas.append(re.compile("DIARIO *O. *I?CIAL *JUNTA *COMERCIAL (.*-FEIRA|.*), *\d* *DE *[A-zçÇ]* *DE *\d{4} *\d* SAO PAULO, *\d* \(\d*\)( \d*)?"))
        # lista_expressoes_ignoradas.append(re.compile("(DIARIO|CADERNO) (.*-FEIRA|.*), *\d* *DE *[A-zçÇ]* *DE *\d{4} *\d* SAO PAULO, *\d* \(\d* \)"))

        # expressao_cabecalho = re.compile("\w*-feira, *\d* *de *[A-zçÇ]* *de *\d{4}",re.IGNORECASE)
        # lista_expressoes_ignoradas.append(expressao_cabecalho)

        expressao_pagina = re.compile("(\d* *. *)?São Paulo, *\d* \(\d*\)( *. *\d*)?",re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_pagina)

        expressao_diario = re.compile("Diário *O. *i?cial *Junta *Comercial", re.IGNORECASE)
        lista_expressoes_ignoradas.append(expressao_diario)

        # separador = '.\n'
        separador = 'NIRE - '

        return super(ExtratorJUCESP, self).cria_lista_de_linhas_removendo_separador(lista_expressoes_ignoradas, separador)

    def procura_empresas(self,lista):
        empresas = []
        for linha in lista:
            empresa,encontrou = self.is_recuperacao(linha)
            if encontrou:
                empresas.append(empresa)
            else:
                empresa,encontrou = self.is_falencia(linha)
                if encontrou:
                    empresas.append(empresa)
        return empresas

    def get_caderno(self):
        return 'JUNTA COMERCIAL'

    def is_recuperacao(self, linha):
        expressao_recuperacao_judicial = re.compile('(.*) *EM *RECUPERACAO *JUDICIAL',re.IGNORECASE)
        valores = linha.split('-')
        for valor in valores:
            rec_jud_match = expressao_recuperacao_judicial.search(valor)
            if rec_jud_match:
                return rec_jud_match.group(1).strip(),True
        return None,False

    def is_falencia(self,linha):
        expressao_com_alteracao = re.compile('\d* *- *N\. *DA *ALTERACAO: *\d*[\/ ]?\d*[- ]?\d *- *(.*)-',re.IGNORECASE)
        expressao_nire_nome = re.compile('\d* *- * *(.*) -')
        entrada = linha.strip()[2:]
        if 'FALENCIA' in entrada:
            match = expressao_com_alteracao.search(entrada)
            if match:
                nome_empresa = match.group(1).split('-')[0].strip()
                return nome_empresa, True
            else:
                match = expressao_nire_nome.search(entrada)
                if match:
                    nome_empresa = match.group(1).split('-')[0].strip()
                    return nome_empresa,True
        return None, False

    def get_nome_caderno(self):
        return 'JUNTA COMERCIAL'

    def extrai(self,tag=None):
        regex_util = RegexUtil()
        try:
            juntaComercialService = JuntaComercialService()
            lista, data_caderno = self.cria_lista_de_linhas()

            if len(lista) < 2:
                print("Diário do dia", data_caderno," Não possui publicações")
                return False

            dataNova = re.search("(A\s*L\s*T\s*E\s*R\s*A\s*C\s*A\s*O|C\s*O\s*N\s*S\s*T\s*I\s*T\s*U\s*I\s*C\s*A\s*O)\:?\s*(\d\s*\d\s*\/\s*\d\s*\d\s*\/\s*\d\s*\d\s*\d\s*\d)",remove_acentos(lista[0]).upper().replace("Ç", "C"))

            regex_tipo = re.compile("(A\s*L\s*T\s*E\s*R\s*A\s*C\s*O\s*E\s*S|C\s*O\s*N\s*S\s*T\s*I\s*T\s*U\s*I\s*C\s*O\s*E\s*S)\s*(S\s*O\s*C\s*I\s*E\s*D\s*A\s*D\s*E\s*S\s*(P\s*O\s*R\s*A\s*C\s*O\s*E\s*S|L\s*I\s*M\s*I\s*T\s*A\s*D\s*A\s*S?)|E\s*I\s*R\s*E\s*L\s*I\s*|C\s*O\s*M\s*A\s*N\s*D\s*I\s*T\s*A\s*S\s*S\s*I\s*M\s*P\s*L\s*E\s*S|E\s*M\s*P\s*R\s*E\s*S\s*A\s*R\s*I\s*O\s*S|E\s*M\s*P\s*R\s*E\s*S\s*A\s*S\s*E\s*S\s*T\s*R\s*A\s*N\s*G\s*E\s*I\s*R\s*A\s*S|C\s*O\s*N\s*S\s*O\s*R\s*C\s*I\s*O\s*S|C\s*O\s*O\s*P\s*E\s*R\s*A\s*T\s*I\s*V\s*A\s*S|F\s*I\s*R\s*M\s*A\s*S\s*(I\s*N\s*D\s*I\s*V\s*I\s*D\s*U\s*A\s*I\s*S|E\s*I\s*R\s*E\s*L\s*I|L\s*I\s*M\s*I\s*T\s*A\s*D\s*A\s*S))",
                flags=re.I)

            print("Iniciando extração para o caderno: ",data_caderno)

            try:
                data = dataNova.group(2)
            except:
                data = data_caderno

            try:
                tipo = re.search(regex_tipo, remove_acentos(lista[0]).upper().replace("Ç", "C")).group(0)
            except AttributeError:
                try:
                    tipo = re.search(regex_tipo, remove_acentos(lista[1]).upper().replace("Ç", "C")).group(0)
                except AttributeError:
                    tipo = 'ALTERACOES GENERICAS'

            trocou = False
            junta = None

            for alteracao in lista[1:]:

                alteracao = remove_acentos(alteracao).upper().replace("Ç", "C")
                dataNova = re.search("(A\s*L\s*T\s*E\s*R\s*A\s*C\s*A\s*O|C\s*O\s*N\s*S\s*T\s*I\s*T\s*U\s*I\s*C\s*A\s*O)\:?\s*(\d\d\/\d\d\/\d\d\d\d)",alteracao)
                tipoNovo = re.search(regex_tipo, alteracao)

                try:
                    # if data_caderno <= datetime.strptime('2006/01/01',"%Y/%m/%d"):
                    #     #possível solução para os diários antigos
                    #     lista_dados = [a for a in alteracao.replace(' -',' - ').replace('- ',' - ').replace(':','').split(" - ") if not re.search('M\.E\.$|E\.P\.P\.$',a)]
                    #     #lista_dados = [a for a in alteracao.replace(' -',' - ').split(" - ") if not re.search('^M\.E\.$|^E\.P\.P\.$',a)]
                    lista_dados = [a for a in alteracao.replace(' -',' - ').replace('- ',' - ').replace(':','').split(" - ") if not re.search('M\.E\.$|E\.P\.P\.$',a)]
                    if dataNova:
                        data = dataNova.group(2)
                    if tipoNovo:

                        junta = self.salva_dados_jucesp(lista_dados,alteracao,tipo,data,data_caderno,juntaComercialService,regex_util)
                        tipo = tipoNovo.group(0).upper()
                        trocou = True
                    if not trocou:
                        junta = self.salva_dados_jucesp(lista_dados,alteracao,tipo,data,data_caderno,juntaComercialService,regex_util)
                    trocou = False

                except Exception as e:
                    print(e)

                if junta:
                    print("Empresa ",nome_empresa," do tipo ",tipo," Salva com o texto: ",texto)

            return True
        except Exception as e:
            print(e)
            return False


    def verifica_nome(self,nome_empresa,alteracao):
        if re.search('M\.E\.',alteracao):
            nome_empresa + ' M.E.'
        if re.search('E\.P\.P\.',alteracao):
            nome_empresa + ' E.P.P.'
        return nome_empresa

    def salva_dados_jucesp(self,lista_dados,alteracao,tipo,data,data_caderno,juntaComercialService,regex_util = None):
        tipoJuntaService = TipoJuntaService()

        if re.search('N.\s*DA\s*ALTERACAO', alteracao):
            nire = lista_dados[0]
            numero_alteracao = lista_dados[1]
            nome_empresa = self.verifica_nome(lista_dados[2], alteracao)
            texto = ''.join(lista_dados[3:])
            if 'CONSTITUICOES' in tipo:
                tipo = 'ALTERACOES GENERICAS'
        elif re.search('COM\s*O\s*OBJE\-?\s*TO\s*SOCIAL\s*DE:', alteracao):
            nire = lista_dados[0]
            nome_empresa = ''.join(re.split("COM\s*O\s*OBJE\-?\s*TO\s*SOCIAL\s*DE:", alteracao)[0].split("-")[1:])
            texto = re.split("COM\s*O\s*OBJE\-?\s*TO\s*SOCIAL\s*DE:", alteracao)[1]
            if len(nome_empresa) > 100:
                nome_empresa = lista_dados[1]
            if 'ALTERACOES' in tipo:
                tipo = 'CONSTITUICOES GENERICAS'
        elif re.search('ANOTACAO\s*DE\s*', alteracao):
            nire = lista_dados[0]
            nome_empresa = lista_dados[1]
            try:
                numero_alteracao = lista_dados[2].split('.')[1].split(',')[0]
            except:
                numero_alteracao = None
            texto = ''.join(lista_dados[2:])
        else:#problema com filiais
            nire = lista_dados[0]
            nome_empresa = lista_dados[1]
            texto = ''.join(lista_dados[3:])

        tipo_junta = tipoJuntaService.preenche_tipo_junta(tipo)

        return juntaComercialService.preenche_junta_comercial(nome_empresa,nire,tipo_junta,data,data_caderno,texto,numero_alteracao,regex_util)

    def extrai_json_mapa(self,nome_empresa=None,nire=None):
        import requests
        s = requests.Session()

        with open('empresas.csv', 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
            linhas = list(reader)
        for linha in linhas:
            if len(linha) < 2:
                continue

            conseguiu = False
            tentativas = 5
            cnpj = None
            while conseguiu == False or tentativas <=0:
                try:
                    linha[1] = remove_varios_espacos(remove_caracteres_especiais(remove_pontuacao(linha[1])))
                    pagina = s.get('https://www.jucesponline.sp.gov.br/GeoJson.aspx?razao={nome_empresa}&objeto=&cnpj=&logradouro=&cep=&bairro=&municipio=&uf=SP&bempresaativa=false&filiais=true&offset=0'.format(nome_empresa=linha[1].strip()))
                    if pagina.json():
                        conseguiu= True
                except json.decoder.JSONDecodeError as e:
                    conseguiu=False
                    tentativas -= 1
                    time.sleep(2)
                except:
                    conseguiu=False
                    tentativas -= 1
                    time.sleep(300)
            achou = False
            if pagina.json()['featureCollection']['features']:
                for empresa in pagina.json()['featureCollection']['features']:
                   if empresa['properties']['NIRE'] == linha[0].replace("\"","").strip():
                       arquivo = open('mapa_empresas.txt', 'r')  # Abra o arquivo (leitura)
                       conteudo = arquivo.readlines()
                       conteudo.append("\n"+str(empresa['properties']))
                       arquivo = open('mapa_empresas.txt', 'w')
                       arquivo.writelines(conteudo)
                       arquivo.close()
                       print("Empresa ",linha[1]," Salva")
                       achou = True
                   # if empresa['properties']['NIRE'] == linha[2].replace("\"", "").strip():
                   #     arquivo = open('mapa_empresas.txt', 'r')  # Abra o arquivo (leitura)
                   #     conteudo = arquivo.readlines()
                   #     conteudo.append("\n" + str(empresa['properties']))
                   #     arquivo = open('mapa_empresas.txt', 'w')
                   #     arquivo.writelines(conteudo)
                   #     arquivo.close()
                   #     print("Empresa ", linha[1], " Salva")
                   #     achou = True


                if not achou:
                   print("Empresa ", linha[1], " Com Nire distinto da jucesp")

    def salva_constituicoes_em_objeto_social(self):
        #from pdjus.dal.EmpresaObjetoSocialDao import EmpresaObjetoSocialDao
        from pdjus.service.EmpresaService import EmpresaService
        #from pdjus.service.CnaeService import CnaeService
        #from pdjus.dal.ObjetoSocialDao import ObjetoSocialDao
        #empresaObjetoDao = EmpresaObjetoSocialDao()
        empresa_service = EmpresaService()
        #cnae_service = CnaeService()
        #objetoDao = ObjetoSocialDao()

        juntaService = JuntaComercialService()

        listaconstituicao = juntaService.dao.listar_constituicoes()

        lista_cnae = self.verifica_cnae()

        for constituicao in listaconstituicao:
            empresa = empresa_service.dao.get_por_id(constituicao.empresa)
            empresa_service.seta_objeto_social(empresa=empresa, nome=constituicao.texto, fonte_dado='1', principal=True,lista_cnae=lista_cnae)
        # for constituicao in listaconstituicao:
        #     objeto = objetoDao.get_por_id(int(constituicao['id']))
        #     cnae_service.verifica_objeto_social_cnae(objeto,lista_cnae)
        # for constituicao in listajunta:
        #     objetos = empresaObjetoDao.listar_objetos_da_empresa(constituicao.empresa)
        #
        #     for obj in objetos:
        #         if len(list(filter(lambda objeto: objeto.principal == True, objetos))) > 0:
        #             empresa_service.seta_objeto_social(empresa=obj.empresa, nome=obj.nome, fonte_dado='1', principal=False,
        #                                                lista_cnae=lista_cnae)
        #         else:
        #             empresa_service.seta_objeto_social(empresa=obj.empresa, nome=obj.nome, fonte_dado='1', principal=True,
        #                                                lista_cnae=lista_cnae)

    def seta_objeto_como_principal_da_empresa(self):
        from pdjus.dal.EmpresaObjetoSocialDao import EmpresaObjetoSocialDao
        from pdjus.service.EmpresaService import EmpresaService
        empresaService = EmpresaService()
        empresaObjetoDao = EmpresaObjetoSocialDao()
        empresa = empresaService.dao.get_por_cnpj('12435359000170')

        objetos = empresaObjetoDao.listar_objetos_da_empresa(empresa)

        list(filter(lambda objeto: objeto.principal == True,objetos))

        print('3')

    def transfor_dict(self):
        with open('match_cnpj_com_banco_da_receita2.csv', 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
            linhas = list(reader)
            dict = {}
            for linha in linhas:
                dict[linha[1]] = linha[0]
            print('')

    def salva_cnae(self):
        from pdjus.service.EmpresaService import EmpresaService
        from classificadores.ClassificaCNAE import ClassificaCNAE

        classifica_cnae = ClassificaCNAE()
        empresaService = EmpresaService()
        #empresa = empresaService.dao.get_por_cnpj('12433411000150')


        with open('mapa_empresas1.txt', 'r', encoding="utf-8") as arquivo:
            conteudo = arquivo.readlines()
            for linha in conteudo:
                dicEmpresa = ast.literal_eval(linha)

                empresa = empresaService.dao.get_por_nire(dicEmpresa['NIRE'])
                if dicEmpresa['CNPJ']:
                    empresa._cnpj = empresa.formata_cnpj(dicEmpresa['CNPJ'])
                empresaService.salvar(empresa, salvar_estrangeiras=True, salvar_many_to_many=True)
                if dicEmpresa['Enquadramento']:
                    empresaService.seta_enquadramento(empresa, dicEmpresa['Enquadramento'])
                if dicEmpresa['Endereco']:
                    empresa.endereco = dicEmpresa['Endereco']
                if dicEmpresa['CEP']:
                    empresa.cep = dicEmpresa['CEP']
                empresaService.salvar(empresa, salvar_estrangeiras=True, salvar_many_to_many=True)


                cnae = empresaService.dao.get_no_banco_da_receita_federal_por_cnpj(dicEmpresa['CNPJ'])

                if len(cnae)> 0:
                    for (chave, valor) in classifica_cnae.dic_cnae_23.items():
                        if cnae[0]['cnae'] == remove_varios_espacos(remove_caracteres_especiais(remove_acentos(chave))):
                            #achou = True
                            objeto_social = remove_varios_espacos(remove_caracteres_especiais(remove_acentos(valor.replace('-',' '))))
                            empresaService.seta_objeto_social(empresa,objeto_social,3,True,cnae=cnae[0]['cnae'])
                            print('Objeto ', objeto_social,'da empresa ',dicEmpresa['Razao'],'Atribuído ao CNAE: ', cnae[0]['cnae'])
            # if achou == False:
            #     print('O padrão cnae ',linha[2],' nao existe no dic')
            #     arquivo = open('mapa_empresas.txt', 'r')  # Abra o arquivo (leitura)
            #     conteudo = arquivo.readlines()
            #     conteudo.append("\n" + "O padrão cnae "+ linha[2] + "nao existe no dic")
            #     arquivo = open('mapa_empresas.txt', 'w')
            #     arquivo.writelines(conteudo)
            #     arquivo.close()
            #lista = empresaService.dao.listar_cnae(empresa)


    def salva_cnpj_das_anotacoes(self):
        from pdjus.dal.JuntaComercialDao import JuntaComercialDao
        from pdjus.dal.TipoAnotacaoDao import TipoAnotacaoDao
        from pdjus.service.EmpresaService import EmpresaService
        juntadao = JuntaComercialDao()
        tipodao = TipoAnotacaoDao()
        empresaService = EmpresaService()


        #tipo_anotacao = tipodao.get_por_nome('ALTERA_INCLUSAO_CGC')

        #listajunta = juntadao.get_por_tipo_anotacao(tipo_anotacao)
        with open('nire_cnpj.csv', 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
            linhas = list(reader)
        for linha in linhas:
            empresa = empresaService.dao.get_por_nire(linha[0])
            empresa._cnpj = empresa.formata_cnpj(linha[1])
            empresaService.dao.salvar(empresa)
            print('CNPJ ',linha[1],' Adicionado na empresa: ', empresa.nome)

    def classifica_anotacos_nao_classificadas(self,fatia=1,rank=0,limit = None):

        from pdjus.dal.JuntaComercialDao import JuntaComercialDao
        from pdjus.service.JuntaComercialService import JuntaComercialService
        from classificadores.ClassificaJucesp import ClassificaJucesp
        regex_util = RegexUtil()
        juntadao = JuntaComercialDao()
        classifica_jucesp = ClassificaJucesp()

        listajunta = juntadao.listar_anotacoes_nao_classificadas(fatia=fatia,rank=rank,limit=limit)
        print(len(listajunta))
        #while listajunta > 0:
        for junta in listajunta:
            if not classifica_jucesp.classica_anotacao(junta, regex_util):
            #classifica_jucesp.classica_anotacao(junta, regex_util)
                print(junta.texto, 'não classificada')
            # else:
            #     junta.classificado = True
            #     juntaservice.dao.salvar(junta, commit=True, salvar_estrangeiras=False, salvar_many_to_many=False)
        #listajunta = juntadao.listar_anotacoes_nao_classificadas(fatia=fatia,rank=rank,limit=limit)

    def valida_objetos_classificados(self,fatia=1,rank=0,limit = None):
        from pdjus.dal.ObjetoSocialDao import ObjetoSocialDao
        from pdjus.service.ObjetoSocialService import ObjetoSocialService

        objetodao = ObjetoSocialDao()
        objetoService = ObjetoSocialService()

        objetos = objetodao.listar_objetos_nao_classificados_para_teste(fatia=fatia, rank=rank)

        arquivo_23 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/cnae_23.txt"
        arquivo_20 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/cnae_20.txt"
        arquivo_10 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/cnae_10.txt"

        arquivo = open("/home/b265522227/PycharmProjects/IpeaJUS/classificadores/teste_cnae{rank}.txt".format(rank=rank),'w')

        for objeto in objetos:
            nome = objeto.nome
            nome = re.sub('(CONSTITUICAO|CNAE)\s*\d+','',nome)

            dic_cnae_10,dic_cnae_20,dic_cnae_23 = self.abre_arquivo_dicionario(arquivo_10,arquivo_20,arquivo_23)
            nome = self.calcula_taxa_classificao(nome,objeto,dic_cnae_10,dic_cnae_20,dic_cnae_23)

            arquivo_23 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/lista_cnae_23.txt"
            arquivo_20 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/lista_cnae_20.txt"
            arquivo_10 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/lista_cnae_10.txt"

            dic_cnae_10, dic_cnae_20, dic_cnae_23 = self.abre_arquivo_dicionario(arquivo_10, arquivo_20, arquivo_23)
            nome = self.calcula_taxa_classificao(nome, objeto, dic_cnae_10, dic_cnae_20, dic_cnae_23)

            perc = '{:.5f}'.format((1-(len(nome)/len(re.sub('(CONSTITUICAO|CNAE)\s*\d+','',objeto.nome))))*100)
            arquivo.writelines(f'{objeto.nome};{nome};{perc}\n')
            print(f'{objeto.nome};{nome};{perc}\n')

    def calcula_taxa_classificao(self,nome,objeto,dic_cnae_10,dic_cnae_20,dic_cnae_23):

        for chave, valor in dic_cnae_23.items():
            if valor.search(objeto.nome):
                nome = re.sub(valor, '', nome)
        for chave, valor in dic_cnae_20.items():
            if valor.search(objeto.nome):
                nome = re.sub(valor, '', nome)
        for chave, valor in dic_cnae_10.items():
            if valor.search(objeto.nome):
                nome = re.sub(valor, '', nome)
        return nome

    def verifica_cnae(self):
        arquivo_23 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/cnae_23.txt"
        arquivo_20 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/cnae_20.txt"
        arquivo_10 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/cnae_10.txt"

        dic_cnae_10, dic_cnae_20, dic_cnae_23 = self.abre_arquivo_dicionario(arquivo_10, arquivo_20, arquivo_23)
        lista_cnae = [dic_cnae_10,dic_cnae_20,dic_cnae_23]
        #lista_cnae = self.preenche_lista_cnae(objeto_social,dic_cnae_23,dic_cnae_20,dic_cnae_10)

        arquivo_23 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/lista_cnae_23.txt"
        arquivo_20 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/lista_cnae_20.txt"
        arquivo_10 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/lista_cnae_10.txt"

        dic_cnae_102, dic_cnae_202, dic_cnae_233 = self.abre_arquivo_dicionario(arquivo_10, arquivo_20, arquivo_23)

        lista_cnae.extend([dic_cnae_102,dic_cnae_202,dic_cnae_233])
        #lista_cnae.extend(self.preenche_lista_cnae(objeto_social,dic_cnae_23,dic_cnae_20,dic_cnae_10))

        return lista_cnae

    def abre_arquivo_dicionario(self, arquivo10, arquivo20, arquivo23):

        arquivo_23 = open(arquivo23)
        arquivo_20 = open(arquivo20)
        arquivo_10 = open(arquivo10)

        lista_cnae_23 = arquivo_23.readlines()
        lista_cnae_20 = arquivo_20.readlines()
        lista_cnae_10 = arquivo_10.readlines()

        arquivo_23.close()
        arquivo_20.close()
        arquivo_10.close()

        dic_cnae_23 = {}
        dic_cnae_20 = {}
        dic_cnae_10 = {}

        for cnae_23 in lista_cnae_23:
            dic_cnae_23[cnae_23.split(':')[0]] = re.compile(
                cnae_23.split(':')[1].replace('\n', '').replace('\\s', '\s'))

        for cnae_20 in lista_cnae_20:
            dic_cnae_20[cnae_20.split(':')[0]] = re.compile(
                cnae_20.split(':')[1].replace('\n', '').replace('\\s', '\s'))

        for cnae_10 in lista_cnae_10:
            dic_cnae_10[cnae_10.split(':')[0]] = re.compile(
                cnae_10.split(':')[1].replace('\n', '').replace('\\s', '\s'))

        del (lista_cnae_23)
        del (lista_cnae_20)
        del (lista_cnae_10)

        return dic_cnae_10, dic_cnae_20, dic_cnae_23

    def classifica_objetos_nao_classificados(self,fatia=1,rank=0):
        from pdjus.dal.ObjetoSocialDao import ObjetoSocialDao
        from pdjus.service.CnaeService import CnaeService
        from pdjus.service.ObjetoSocialService import ObjetoSocialService
        from classificadores.ClassificaCNAE import ClassificaCNAE
        cnae_service = CnaeService()
        objetodao = ObjetoSocialDao()
        objetoService = ObjetoSocialService()
        classifica_cnae = ClassificaCNAE()

        objetos_nao_classificados = objetodao.listar_objetos_nao_classificados(fatia=fatia,rank=rank)

        arquivo_23 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/cnae_23.txt"
        arquivo_20 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/cnae_20.txt"
        arquivo_10 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/cnae_10.txt"

        dic_cnae_10, dic_cnae_20, dic_cnae_23 = self.abre_arquivo_dicionario(arquivo_10, arquivo_20, arquivo_23)

        for objeto_nao_classificado in objetos_nao_classificados:
            if cnae_service.verifica_objeto_social_cnae(objeto_nao_classificado,dic_cnae_23,dic_cnae_20,dic_cnae_10,classifica_cnae):
                objeto_nao_classificado.classificado = True
                objetoService.dao.salvar(objeto_nao_classificado, commit=True, salvar_estrangeiras=False, salvar_many_to_many=False)

        arquivo_23 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/lista_cnae_23.txt"
        arquivo_20 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/lista_cnae_20.txt"
        arquivo_10 = "/home/b265522227/PycharmProjects/IpeaJUS/classificadores/lista_cnae_10.txt"

        dic_cnae_10, dic_cnae_20, dic_cnae_23 = self.abre_arquivo_dicionario(arquivo_10, arquivo_20, arquivo_23)

        for objeto_nao_classificado in objetos_nao_classificados:
            if cnae_service.verifica_objeto_social_cnae(objeto_nao_classificado,dic_cnae_23,dic_cnae_20,dic_cnae_10,classifica_cnae):
                objeto_nao_classificado.classificado = True
                objetoService.dao.salvar(objeto_nao_classificado, commit=True, salvar_estrangeiras=False, salvar_many_to_many=False)

    def extrair_txt_para_banco(self):
        from pdjus.service.EmpresaService import EmpresaService
        empresa_service = EmpresaService()

        lista_cnae = self.verifica_cnae()
        with open('mapa_empresas1.txt','r',encoding="utf-8") as arquivo:
            conteudo = arquivo.readlines()
            for linha in conteudo:
                try:
                    dicEmpresa = ast.literal_eval(linha)
                    if dicEmpresa['Razao'] == None:
                        print("A empresa não possui nome, pulando...")
                        continue
                    empresa = empresa_service.dao.get_por_nire(dicEmpresa['NIRE'])
                    if dicEmpresa['CNPJ']:
                        empresa._cnpj = empresa.formata_cnpj(dicEmpresa['CNPJ'])
                    empresa_service.salvar(empresa, salvar_estrangeiras=True, salvar_many_to_many=True)
                    if dicEmpresa['Objeto']:
                        for count,objeto in enumerate(re.split('#|;',dicEmpresa['Objeto'])):
                            if count == 0:
                                empresa_service.seta_objeto_social(empresa=empresa,nome=objeto,fonte_dado='0',principal=True,lista_cnae=lista_cnae)
                            else:
                                empresa_service.seta_objeto_social(empresa=empresa,nome=objeto,fonte_dado='0',lista_cnae=lista_cnae)
                    if dicEmpresa['Enquadramento']:
                        empresa_service.seta_enquadramento(empresa,dicEmpresa['Enquadramento'])
                    if dicEmpresa['Endereco']:
                        empresa.endereco = dicEmpresa['Endereco']
                    if dicEmpresa['CEP']:
                        empresa.cep = dicEmpresa['CEP']
                    empresa_service.salvar(empresa,salvar_estrangeiras = True,salvar_many_to_many = True)
                    print("Empresa: ",dicEmpresa['Razao']," DE NIRE: ",dicEmpresa['NIRE']," Salva no banco")
                except Exception as e:
                    print("Não foi possível salvar a empresa: ",dicEmpresa['Razao']," Erro:", e)

            arquivo.close()


if __name__ == '__main__':
    p = ExtratorJUCESP("JUCESP","JUCESP")
    #p = ProcessaExtrator("JUCESP", "txt", ExtratorJUCESP, AcompanhamentoProcessualDJSP)
    p.salva_constituicoes_em_objeto_social()
    #p.seta_objeto_como_principal_da_empresa()
    #p.salva_constituicoes_em_objeto_social()
    #p.classifica_objetos_nao_classificados()
    #p.valida_objetos_classificados(fatia = int(sys.argv[1]), rank= int(sys.argv[2]))
    #p.classifica_objetos_nao_classificados(fatia = int(sys.argv[1]), rank= int(sys.argv[2]))
    #p.classifica_anotacos_nao_classificadas(fatia = int(sys.argv[1]), rank= int(sys.argv[2]))
    #p.extrai_arquivo('JUCESP_2019_05_21')
    #p.extrai_json_mapa()
    #p.extrai_diversos_que_nao_foram_extraidos_a_partir_da_data(data=datetime.strptime('2001-12-12',"%Y-%m-%d").date(),fatia = int(sys.argv[1]), rank= int(sys.argv[2]))
    #p.extrai_diversos_independente_de_status(fatia = int(sys.argv[1]), rank= int(sys.argv[2]))
    #extrai_diversos(self, padrao=None,tag=None,rank=0 , fatia = 1)
