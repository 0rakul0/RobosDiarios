# -*- coding: utf-8 -*-
import datetime
import re
import traceback
#import pool as pool
import sys

import os
import requests
from requests.exceptions import ChunkedEncodingError

from pdjus.dal.DistribuicaoDao import DistribuicaoDao
from pdjus.modelo.ParteDistribuicao import ParteDistribuicao
from pdjus.service.DistribuicaoService import DistribuicaoService
from util import Solr
from util.ConfigManager import ConfigManager
from acompanhamento_processual.AcompanhamentoProcessualDJSP import AcompanhamentoProcessualDJSP
from extrator.ProcessaExtrator import ProcessaExtrator
from extrator.ExtratorDJSP import ExtratorDJSP
import time
from util.StringUtil import remove_quebras_linha_de_linha, remove_acentos, remove_varios_espacos
from pdjus.service.ClasseProcessualService import ClasseProcessualService


class ExtratorDJSPIndices(ExtratorDJSP):

    def __init__(self, arquivo, acompanhamento,arquivo_bd = None):
        super(ExtratorDJSPIndices, self).__init__(arquivo, acompanhamento,arquivo_bd)

    def chama_listar_distribuicoes_sem_assunto(self,classe_procesual=None):
        dist_dao = DistribuicaoDao()
        lista_distribuicoes_sem_assunto = dist_dao.listar_distribuicoes_sem_assunto(classe_processual = classe_procesual,rank=0, fatia=1 )
        for distribuicao in lista_distribuicoes_sem_assunto:
            self.busca_assuntos(distribuicao=distribuicao, tag='CLASSE_DistribDiversos')


    def busca_assuntos(self, distribuicao, tag):# def busca_assuntos(self, npu):
        if not distribuicao.is_npu(distribuicao.numero_processo):
             return
        npu = distribuicao.formata_npu_com_pontos(distribuicao.numero_processo)

        #sucesso_buscasolr = False
        #while not sucesso_buscasolr:
            #try:
        jresultado = Solr.consulta_diarios(npu)
        #sucesso_buscasolr = True
            # except ChunkedEncodingError as e:
            #     sucesso_buscasolr = False
            #     print("ChunkedEncodingError: tentando novamente")


        for caderno in jresultado:
            resultado_nome_diario = caderno['id']
            matchs,data = self.parsing_npu(resultado_nome_diario = resultado_nome_diario, npu =npu)
        #self.parsing_diario(matchs, npu, distribuicao)
            if matchs != None:
                self.parsing_diario(matchs,npu,distribuicao,data)
            else:
                continue

    def parsing_diario (self,matchs,npu,distribuicao,data):
    #def parsing_diario (self, matchs, npu,data):
        assunto = None
        distribuicao_service = DistribuicaoService()
        classe_service = ClasseProcessualService()
            # TODO O assunto: "SE CIÊNCIA AO" foi inserido no processo com npu: 1001723-86.2018.8.26.0008 Retirado do match: 1001723-86.2018.8.26.0008 - Execução de Título Extrajudicial - Nota Promissória - Fabio Ricardo Montuori - Dê- se ciência ao
            # TODO Assunto não encontrado:Match do diario : 0000919-61.1999.8.26.0539 (539.01.1999.000919-2/000000-000) Nº Ordem: 000138/1999 - Execução de Título Extrajudicial - Cheque
            # TODO Assunto não encontrado: 0017600-21.2011.8.26.0011 Classe: Assunto: Execução de Título Extrajudicial - Nota Promissória Exeqüente: Banco Bradesco S/A
            #TODO 0002294-62.2009.8.26.0696 (696.09.002294-7) - Execução de Título Extrajudicial - Suely Ribeiro Barbosa Rossi Me - Solange de
            #0033957-25.2010.8.26.0007 (007.10.033957-0) - Execução de Título Extrajudicial - Contratos Bancários - Banco Itaú S/A - Borg
            #0034074-16.2010.8.26.0007 (007.10.034074-8) - Execução de Título Extrajudicial - Contratos Bancários - Wladimir Caressato -
            #0012481-98.2010.8.26.0016 (016.10.012481-5) - Execução de Título Extrajudicial - Cheque - V. A. F. DOS SANTOS DECORAÇÕES ME
        if matchs:
            try:
                for match in matchs:
                    classe_match = None
                    classe = None
                    if not npu + ")" in match:
                        if 'ASSUNTO:' in match.upper():
                            classe_match = remove_varios_espacos(re.split(':', match)[2])
                            classe_match = re.match(".*(?= ASSUNTO)", classe_match.upper()).group(0)
                        elif match.count('-') > 5:
                            classe_match = remove_varios_espacos(re.split('-', match)[5])
                            classe = classe_service.dao.get_por_nome(classe_match)
                            if classe:
                                assunto = remove_varios_espacos(re.split('-', match)[6])
                        if not classe and match.count('-') > 3 and not "CLASSE:" in match.upper() and not re.search('\d*\.\d*\.\d*\.\d*\.\d*',remove_varios_espacos(re.split('-', match)[3])):
                            classe_match = remove_varios_espacos(re.split('-', match)[2])
                            classe = classe_service.dao.get_por_nome(classe_match)
                            if classe:
                                assunto = remove_varios_espacos(re.split('-', match)[3])

                        classe = classe_service.dao.get_por_nome(classe_match)
                        if classe:
                            if 'PROCESSO PRINCIPAL' in match.upper() or 'APENSADO'  in match.upper():
                                assunto = remove_varios_espacos(re.split('-', match)[4])
                            elif 'ASSUNTO:' in match.upper():
                                assunto = remove_varios_espacos(re.split(':', match)[3])
                                assunto = re.match(".*(?= (PUBLICA|REQUERENTE|REQ|EXEQUENTE|EXE|EXEQ|EXEQTE|REQTE|REQUETE))", assunto).group(0)
                            elif '-SE' in match.upper():
                                assunto = remove_varios_espacos(re.split('-', match)[3])
                            elif 'ORDEM' in match.upper():
                                assunto = remove_varios_espacos(re.split('-', match)[3])
                            # elif 3 < match.upper().count('-') <= 5 and not re.search('\d*\.\d*\.\d*\.\d*\.\d*',remove_varios_espacos(re.split('-', match)[3])):
                            #     assunto = remove_varios_espacos(re.split('-', match)[3])
                            # elif match.upper().count('-') > 5:
                            #    assunto = remove_varios_espacos(re.split('-', match)[6])
                            elif 'CLASSE - ASSUNTO' in match.upper():
                                assunto = remove_varios_espacos(re.split('-', match)[3])
                                assunto = re.match(".*(?= REQUERENTE|REQU|REQTE|REQ)", assunto)
                        # if not classe:
                        #     classe_match = remove_varios_espacos(re.split('-', match)[3])
                        #     classe = classe_service.dao.get_por_nome(classe_match)
                        #     if classe:
                        #         assunto = remove_varios_espacos(re.split('-', match)[3])
                        #     else:
                        #         ConfigManager().escreve_log("###Classe não encontrada: " + match,
                        #                                     log='distribuicao_assuntos_Log.txt')
                        if assunto:
                            assunto = remove_varios_espacos(assunto.upper().replace('REQTE','').replace('REQUERENTE',''))
                            distribuicao_service.seta_assunto(distribuicao=distribuicao, nome_assunto=assunto , data = data)
                            distribuicao_service.salvar(obj=distribuicao,tag=tag)
                            ConfigManager().escreve_log('##### ''O assunto: "' + assunto + '"'' foi inserido no processo com npu: ' + npu + ' Retirado do match: ' + match)
                        else:
                            ConfigManager().escreve_log("Assunto não encontrado:Match do diario : " + match,
                                                        log='distribuicao_assuntos_Log.txt')
                    else:
                        ConfigManager().escreve_log("O npu encontrado não é principal: " + match,
                                                    log='distribuicao_assuntos_Log.txt')
            except Exception as e:
                ConfigManager().escreve_log("###Assunto não encontrado: " + match,
                                            log='distribuicao_assuntos_Log.txt')
                print(str(e))
        else:
            print("###Processo não encontrado")



    def parsing_npu(self,resultado_nome_diario,npu):
        #resultado_texto = resultado_json_para_texto_doc['_text_']
        data = re.search("\d{0,4}_\d{0,2}_\d{0,2}", resultado_nome_diario).group(0).replace('_', '/')
        #caderno = re.search("\/DJSP_.*$", resultado_nome_diario).group(0).replace("/", "\\")
        #caminho_base = 'C:\\Users\\e279950109\\dados\\SP\\DJSP'
        #resultado_nome_diario = caminho_base + caderno
        try:
            with open(resultado_nome_diario, encoding='utf8') as texto:


                resultado_texto = texto.read()



                resultado_texto = remove_quebras_linha_de_linha(resultado_texto)


                matchs = re.findall(npu + ".{0,100}", resultado_texto)
                return matchs,data
        except FileNotFoundError as e:
            return None,None

    #@profile
    def extrai_recortes(self):
        try:
            start = time.time()


            filtro_escopo_distribuicao = "^PROCESSO\s*?\\n?:\s*?(?P<NUM>[\d[\-|\/}\.]+)\s*(\\n?.*?\\n?)(^VARA\s*\\n?\:.*?$)"
            #filtro_escopo_distribuicao = "^PROCESSO\s*?:\s*?(?P<NUM>[\d[\-|\/}\.]+)\s*(\\n?.*?\\n?)CLASSE\s*:\s*(?P<NUM_CLASSE>\d+)?(\-)?(?P<CLASSE>(.*?\\n?){1,2})?(?P<TIPOEPARTE>((?P<tp>^[A-Z]+.*\\n?\:)(?P<pte>.*\\n))*?)(?:V\s*a\s*r\s*a\s*:\s*(?P<VARA>.*?$))"
            #"^PROCESSO\s*?:\s*?(?P<NUM>[\d\-\.]+)\s*(\\n?.*?\\n?)CLASSE\s*:\s*(?P<NUM_CLASSE>\d+)?(\-)?(?P<CLASSE>(.*\\n?){1,2})(?P<parte>(^[A-Z]+)\s+(?:^.*\s)+?)(?:V\s*a\s*r\s*a\s*:\s*(?P<VARA>.*$))"
            #"^PROCESSO\s*?:\s*?(?P<NUM>[\d\-\.]+)\s*(\\n?.*?\\n?)CLASSE\s*:\s*(?P<NUM_CLASSE>\d+)?(\-)?(?P<CLASSE>.*?)(?P<parte>(.*)\s*(?:^.*\s)+?)(?:V\s*a\s*r\s*a\s*:\s*(?P<VARA>.*$))"
            #"^PROCESSO\s*?:\s*?(?P<NUM>[\d\-\.]++)\s*+CLASSE\s*+:\s*+(?P<NUM_CLASSE>\d++)?\-?(?P<CLASSE>.+?)(\s*?)(?P<parte>"+ partes_regex +"*\s*(?:^.*\s)+?)(?:V\s*+a\s*+r\s*+a\s*+:\s*+(?P<VARA>.*$))"
            #"^PROCESSO\s*?:\s*?(?P<NUM>[\d\-\.]++)\s*+\n?.*?\n?CLASSE\s*+:\s*+(?P<NUM_CLASSE>\d++)?\-?(?P<CLASSE>.+?)(\s*?)(?P<parte>(.*)\s*(?:^.*\s)+?)(?:V\s*+a\s*+r\s*+a\s*+:\s*+(?P<VARA>.*$))"
            self.extrai_distribuicoes_por_classe_assunto("CLASSE_DistribDiversos",
                                        filtro_classe=filtro_escopo_distribuicao,partes_regex=self.partes_regex)

            print("Regular: " + str(time.time() - start))

            return True
        except Exception as e:
            ConfigManager().escreve_log("Erro ao extrair os indices: " + traceback.format_stack(e),
                                        'DJSP', self.__erro_indice)
            return False

    def extrai(self,tag=None):
        return self.extrai_recortes()



    # @profile
    def extrai_distribuicoes_por_classe_assunto(self, nome, saida=None, filtro_classe=None, filtro_assunto=None,
                                                classes_regex=None, assuntos_regex=None, partes_regex=None,
                                                remover_quebras=False, somente_falencias=False):
        lista_distribuicoes = []

        diario = os.path.basename(self._arquivo.name)

        start_time = time.time()

        if self.is_primeira_instancia():
            try:
                ConfigManager().escreve_log(nome + " - extraindo " + diario + "...",
                                            self._acompanhamento.nome, self.__erro_indice)

                self._arquivo.seek(0)
                texto = self._arquivo.read().upper()
                if not self._arquivo_bd:
                    arquivo = self.arquivo_service.dao.get_por_nome_arquivo(self._arquivo.name)
                    if arquivo:
                        self._arquivo_bd = arquivo
                try:
                    data = datetime.datetime.strptime(re.search("(\d{4}_\d{2}_\d{2}).*?\.txt", diario).group(1),
                                                      "%Y_%m_%d")
                except:
                    data = None
                    ConfigManager().escreve_log('Data invalida para ' + diario + '. Pulando...',
                                                self._acompanhamento.nome, self.__erro_indice)

                if data:
                    texto = self.__remove_separadores_de_pagina(texto)

                    if remover_quebras:
                        texto = remove_quebras_linha_de_linha(texto)

                    texto = re.sub("((\:\s*)|(\s*\:))", ":", texto)
                    secoes = None

                    secoes = list(re.finditer(
                        'RELA[CÇ][ÃA]O.{1,20}?FEITOS(.|\n|\r){1,400}?[0-9]{1,2} ?\/ ?[0-9]{1,2} ?\/ ?[0-9]{4}',
                        texto, re.MULTILINE))

                    flags = re.I | re.M | re.U | re.X | re.S

                    # texto = re.sub("-\s*", "", texto) #texto.replace(":\n",":").replace(": \n",":").replace("\n:",":").replace("- \n","").replace("-\n","")
                    matches_todas = re.finditer(filtro_classe, texto, flags)

                    filtro_bloco = re.compile(
                        "^PROCESSO\s*:\s*(?P<NUM>[\d[\-|\/}\.]+)(\s*)((?!PROCESSO\s*:).*\\n){1,15}?(^VARA\s*\\n?\:.*?$)",
                        flags=re.MULTILINE)
                    filtro_distribuicao = re.compile(
                        "^PROCESSO\s*?:\s*?(?P<NUM>[\d[\-|\/}\.]+)\s*(\s*.*?\s*)CLASSE\s*:\s*(?P<NUM_CLASSE>\d+)?(\-)?(?P<CLASSE>(.*?\s){1,3})(?P<TIPOEPARTE>((?P<tp>^[A-Z]+.*\s\:)(?P<pte>.*\s*))*?)(?:V\s*a\s*r\s*a\s*:\s*(?P<VARA>.*?$))",
                        flags)
                    filtro_classe_processual = re.compile(
                        "CLASSE\s*:\s*(?P<NUM_CLASSE>\d+)?(\-)?(?P<CLASSE>(.*?\s*))(?P<TIPOEPARTE>((?P<tp>^[A-Z]+.*\s*\:)(?P<pte>.*\s*))*?)(?:V\s*a\s*r\s*a\s*:\s*(?P<VARA>.*?$))",
                        flags)
                    filtro_npu = re.compile("^PROCESSO\s*?:\s*?(?P<NUM>[\d[\-|\/}\.]+)\s*(\s*.*?\s*)", flags)
                    filtro_tipo = re.compile(
                        "CLASSE\s*:\s*(?P<NUM_CLASSE>\d+)?(\-)?(?P<CLASSE>(.*?\s))(?P<TIPOEPARTE>((?P<tp>^[A-Z]+.*\s*\:)(?P<pte>.*\s*))*?)(?:V\s*a\s*r\s*a\s*:\s*(?P<VARA>.*?$))",
                        flags)

                    indice_falha = 0
                    indice_correto = 0
                    try:
                        for match_bloco_inicial in matches_todas:
                            match_bloco = filtro_bloco.search(match_bloco_inicial.group(0))
                            if not match_bloco:
                                print(match_bloco_inicial.group(0))
                                continue
                            texto_distribuicao = ""
                            try:
                                for linha in match_bloco.group(0).split("\n"):
                                    if ":" in linha:
                                        texto_distribuicao += linha + "\n"
                                    else:
                                        texto_distribuicao = texto_distribuicao[:-1]
                                        texto_distribuicao += linha + "\n"
                                match = filtro_distribuicao.match(texto_distribuicao)
                                if not match:
                                    indice_falha += 1
                                    print("\n deu merda \n\n" + match_bloco.group(0))
                                    continue
                            except Exception as e:
                                print(e)
                                continue
                            assunto = None
                            i = 0

                            # print(texto_distribuicao)
                            match_classe = filtro_classe_processual.search(texto_distribuicao)
                            match_npu = filtro_npu.search(texto_distribuicao)
                            match_tipo = filtro_tipo.search(texto_distribuicao)

                            if assuntos_regex:
                                assuntos = list(assuntos_regex.keys())

                                while i < len(assuntos) and not assunto:
                                    alias_assunto = assuntos[i]

                                    match_assunto = re.search(filtro_assunto.format(
                                        ASSUNTO=assuntos_regex[alias_assunto]), match.group(0),
                                        re.MULTILINE)

                                    if match_assunto:
                                        assunto = alias_assunto
                                    else:
                                        i += 1

                            if not assunto:
                                assunto = 'DEMAIS'

                            start = match_bloco_inicial.start()
                            end = match_bloco_inicial.end()
                            pos = 0
                            tipo_pub, dt_pub, nome_comarca = self.__identifica_secao(match, secoes, start, end)
                            if not nome_comarca:
                                print("seção errada pulando ...")
                                continue

                            if tipo_pub is None or tipo_pub == '':
                                tipo_pub = 'OUTRAS'

                            if dt_pub is None:
                                dt_pub = data

                            poss_npu = list(self.regex_npu.finditer(texto, start, end))
                            poss_n_antigo = list(self.regex_n_antigo.finditer(texto, start, end))

                            npu = None
                            num_antigo = None

                            if len(poss_npu) > 0:
                                npu = poss_npu[pos].group(0).replace(' ', '')

                            if len(poss_n_antigo) > 0:
                                num_antigo = poss_n_antigo[pos].group(0).replace(' ', '')

                            if not npu == match_npu.group("NUM") and not num_antigo == match_npu.group("NUM"):
                                num_antigo = match_npu.group("NUM")

                            comarca = nome_comarca

                            tem_restricao_de_classe = False
                            if classes_regex:
                                tem_restricao_de_classe = True
                            classe = None
                            if match_classe.group("CLASSE"):
                                classe = match_classe.group("CLASSE").replace("\\n", '').strip()
                                if classes_regex:
                                    for classe_correta, classe_regex in classes_regex.items():
                                        if re.match(classe_regex, classe):
                                            classe = classe_correta
                                            tem_restricao_de_classe = False
                                            # Quer dizer que encontrou a classe e passou da restricao
                                            break

                            if not tem_restricao_de_classe:
                                outros = ""
                                vara = None
                                partes_distribuicao = []
                                if match_tipo.group("TIPOEPARTE"):
                                    todas_partes_texto = match_tipo.group("TIPOEPARTE")
                                    todas_partes_texto = remove_acentos(todas_partes_texto)
                                    tipo_partes_e_partes = re.split("\n(?!\:)", todas_partes_texto)

                                    for tipo_parte_e_parte in tipo_partes_e_partes.copy():

                                        tipo_parte = tipo_parte_e_parte.split(":")[0].replace("\n", ' ').strip()
                                        if len(tipo_parte_e_parte.split(":")) > 1:
                                            parte = tipo_parte_e_parte.split(":")[1].replace("\n", ' ').strip()
                                            if len(tipo_parte_e_parte.split(":")) > 2 and re.match(self.partes_regex,
                                                                                                   parte):
                                                tipo_parte = parte
                                                parte = tipo_parte_e_parte.split(":")[2].replace("\n", ' ').strip()
                                        else:
                                            parte = ""

                                        limpa_espaco_tipo_parte = ""
                                        for palavra in tipo_parte.split(" "):
                                            limpa_espaco_tipo_parte += palavra + ' '
                                        tipo_parte = limpa_espaco_tipo_parte.strip()
                                        match_tipo_partes = re.match(self.partes_regex, tipo_parte)

                                        if not match_tipo_partes:
                                            tipo_partes_e_partes.remove(tipo_parte_e_parte)
                                            if tipo_parte_e_parte.strip():
                                                outros = outros + tipo_parte_e_parte.replace('\n', '').strip() + ";"
                                            continue

                                        parte_distribuicao = ParteDistribuicao()
                                        parte_distribuicao.tipo_parte = self.tipo_parte_service.preenche_tipo_parte(
                                            tipo_parte)

                                        if parte_distribuicao.tipo_parte.is_advogado():
                                            numero_oab = parte.split("-")[0]
                                            advogado = parte.split("-")[-1]
                                            try:
                                                if advogado and advogado.strip():
                                                    partes_distribuicao[-1].advogado = advogado
                                                    partes_distribuicao[-1].numero_oab = numero_oab
                                            except Exception as e:
                                                print('\n\nErro tipo parte não cadastrado ' + todas_partes_texto)
                                                print("\n\nTexto da distribuicao\n" + texto_distribuicao)
                                        else:
                                            parte_distribuicao.parte = parte

                                            partes_distribuicao.append(parte_distribuicao)
                                if match.group("VARA"):
                                    vara = match.group("VARA")
                                distribuicao_dict = self.preenche_dicionario_distribuicao(classe, 'DJSP', data,
                                                                                          self.get_nome_caderno(), 'SP',
                                                                                          dt_pub, npu, num_antigo,
                                                                                          tipo_pub, comarca, nome,
                                                                                          partes_distribuicoes=partes_distribuicao,
                                                                                          vara=vara, outros=outros)
                                lista_distribuicoes.append(distribuicao_dict)
                                indice_correto += 1
                        print("\nDiario: " + diario + "\nFalharam: " + str(indice_falha) + " vezes\nAcertaram: " + str(
                            indice_correto) + " vezes\n")
                        print("Tempo: " + str(time.time() - start_time) + " \n")
                        with open("arquivo_erros_extracao.txt", 'a+') as arq:
                            arq.write("\nDiario: " + diario + "\n")
                            arq.write("Falharam: " + str(indice_falha) + " vezes\n")
                            arq.write("Acertaram: " + str(indice_correto) + " vezes\n")
                            arq.write("Tempo: " + str(time.time() - start_time) + " \n")
                        try:
                            start_time = time.time()
                            for i, distribuicao_dict in enumerate(lista_distribuicoes):
                                if i % 1000 == 0:
                                    print(str(i))
                                    self.distribuicao_service.dao.commit()
                                self.distribuicao_service.preenche_distribuicao(distribuicao_dict['nome_classe'],
                                                                                distribuicao_dict['nome_diario'],
                                                                                distribuicao_dict['dt_diario'],
                                                                                distribuicao_dict['nome_caderno'],
                                                                                distribuicao_dict['uf'],
                                                                                distribuicao_dict['dt_pub'],
                                                                                distribuicao_dict['numero_processo'],
                                                                                distribuicao_dict['tipo_dist'],
                                                                                distribuicao_dict['nome_comarca'],
                                                                                distribuicao_dict['tag'],
                                                                                distribuicao_dict[
                                                                                    'partes_distribuicoes'],
                                                                                distribuicao_dict['vara'],
                                                                                distribuicao_dict['outros'],
                                                                                distribuicao_dict['diario'],
                                                                                distribuicao_dict['caderno'])

                            self.distribuicao_service.dao.commit()
                            print("Tempo: " + str(time.time() - start_time) + " \n")
                        except Exception as e:
                            self.distribuicao_service.dao.commit()
                            raise
                    except Exception as e:
                        try:
                            for i, distribuicao_dict in enumerate(lista_distribuicoes):
                                if i % 1000 == 0:
                                    print(str(i))
                                    self.distribuicao_service.dao.commit()
                                self.distribuicao_service.preenche_distribuicao(distribuicao_dict['nome_classe'],
                                                                                distribuicao_dict['nome_diario'],
                                                                                distribuicao_dict['dt_diario'],
                                                                                distribuicao_dict['nome_caderno'],
                                                                                distribuicao_dict['uf'],
                                                                                distribuicao_dict['dt_pub'],
                                                                                distribuicao_dict['numero_processo'],
                                                                                distribuicao_dict['tipo_dist'],
                                                                                distribuicao_dict['nome_comarca'],
                                                                                distribuicao_dict['tag'],
                                                                                distribuicao_dict[
                                                                                    'partes_distribuicoes'],
                                                                                distribuicao_dict['vara'],
                                                                                distribuicao_dict['outros'],
                                                                                distribuicao_dict['diario'],
                                                                                distribuicao_dict['caderno'])
                            self.distribuicao_service.dao.commit()
                        except Exception as e:
                            self.distribuicao_service.dao.commit()
                        print("\nDiario: " + diario + "\nFalharam: " + str(indice_falha) + " vezes\nAcertaram: " + str(
                            indice_correto) + " vezes\n")
                        with open("arquivo_erros_extracao.txt", 'a+') as arq:
                            arq.write("\nDiario: " + diario + "\n")
                            arq.write("Falharam: " + str(indice_falha) + " vezes\n")
                            arq.write("Acertaram: " + str(indice_correto) + " vezes\n")
                            arq.write("Tempo: " + str(time.time() - start_time) + " \n")
                        raise
            except:
                ConfigManager().escreve_log(traceback.format_exc(), self._acompanhamento.nome, self.__erro_indice)




if __name__ == '__main__':
    extrator = ExtratorDJSPIndices("",AcompanhamentoProcessualDJSP)
    #lista = ['0082632-34.2010.8.26.0002', '0001085-17.2011.8.26.0008', '0000158-57.2011.8.26.0006', '0000420-13.2011.8.26.0004', '0006491-37.2011.8.26.0002']
    #for npu in lista:
    #extrator.busca_assuntos(npu)
    extrator.chama_listar_distribuicoes_sem_assunto("TITEXEC")
    # p = ProcessaExtrator("DJSP", "txt", ExtratorDJSPIndices, AcompanhamentoProcessualDJSP)
    # if len(sys.argv) > 2:
    #     p.extrai_diversos(rank= sys.argv[1],fatia= sys.argv[2])
    # else:
    #     p.extrai_diversos()
    #
    #
    # distirbuicao_service = DistribuicaoService()
    # distirbuicao_service.dao.atualiza_indice_contagem()