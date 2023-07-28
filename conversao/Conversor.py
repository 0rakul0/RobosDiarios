# -*- coding: utf-8 -*-

import os
import sys
import traceback
import logging
# import textract
import html2text
from bs4 import BeautifulSoup
from pdjus.conexao.Conexao import default_schema
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfparser import PDFPage, PDFParser, PDFDocument
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import TextConverter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
from pdjus.service.ArquivoService import ArquivoService
from pdjus.service.DiarioService import DiarioService
from util.FileManager import FileManager
from util.ConfigManager import ConfigManager
from datetime import datetime, date
import re
from util.Converte_Jucesp_HTML import *
from util.ColunaInvertidaFix import *
from util.StringUtil import remove_acentos, remove_varios_espacos
from subprocess import Popen, PIPE, STDOUT
from pdfminer.pdfparser import PDFSyntaxError
import psycopg2
import html
import pdftotext


class Conversor(object):

    def __init__(self, nome, filetype):
        self.__nome = nome
        self.__filetype = filetype
        self.__log = "log_conversao.txt"
        self.__erro = "erro_conversao.txt"

    def converte_diretorio(self):

        try:
            ConfigManager().escreve_log("Iniciando conversor de {} para o {}.".format(self.__nome, self.__filetype),
                                    self.__nome, self.__log)
        except Exception as e:
            print(e)
            return

        total = 0
        erros = 0
        #print("... ok")
        fm = FileManager(self.__nome, self.__log)
        pendentes = fm.listar_datas_conversao_pendente(self.__filetype, converte_tudo=True)
        for data in pendentes:
            dir_entrada = fm.caminho(self.__filetype, data)
            dir_saida = fm.caminho("*.txt", data)
            # dir_saida2 = fm.caminho("*.txt", data, sufixo="_novo")
            dir_saida2 = fm.caminho("*.txt", data)

            ConfigManager().escreve_log("Convertendo todos os {}s em {}".format(self.__filetype.upper(), dir_entrada),
                                        self.__nome, self.__log)

            arql = []

            if os.path.isdir(dir_entrada):
                for arq in sorted(os.listdir(dir_entrada),reverse=False):
                    name_arq = os.path.splitext(arq)[0]
                    ext = os.path.splitext(arq)[1]

                    if ext:
                        if not re.search("_\d{{4,6}}\.{ext}".format(ext=self.__filetype), arq):
                            if 'DJSP' in dir_entrada or 'JUCESP' in dir_entrada:
                                if not os.path.isfile(os.path.join(dir_saida,name_arq + ".txt")) or \
                                        not os.path.isfile(os.path.join(dir_saida2,name_arq + ".txt")):
                                    arql.append(arq)
                            else:
                                if not os.path.isfile(os.path.join(dir_saida,name_arq + ".txt")):
                                    arql.append(arq)
            else:
                ConfigManager().escreve_log("{} não existe.".format(dir_entrada), self.__nome, self.__log)

            if len(arql) > 0:
                if self.__filetype == "pdf":
                    res = self.__converte_bloco_pdf(arql, dir_entrada, dir_saida, dir_saida2)
                elif self.__filetype == "rtf":
                    res = self.__converte_bloco_rtf(arql, dir_entrada, dir_saida)
                else:
                    ConfigManager().escreve_log("Formato de arquivo {}: não reconhecido.".format(self.__filetype.upper()),
                                                self.__nome, self.__erro)

                self.atualiza_extracao_diretorio(dir_saida)

                if res is not None:
                    total += res[0]
                    erros += res[1]
                    ConfigManager().escreve_log(res[2], self.__nome, self.__log, False)

                ConfigManager().escreve_log("Conversão de {} {}s concluída com {} erros. Resultados em {}".format(
                    total, self.__filetype.upper(), erros, dir_saida), self.__nome, self.__log)

    def atualiza_extracao_diretorio(self,dir):
        if dir:
            diario_service = DiarioService()
            arquivo_service = ArquivoService()

            for arq in os.listdir(dir):
                try:
                    arquivo = arquivo_service.preenche_arquivo(arq)
                    if not arquivo and ConfigManager().arquivo_suportado_extrator(arq):
                        nome_diario = arq.split('_')[0]
                        data_diario = re.search('(\d{4}_\d{2}_\d{2})',arq)
                        if data_diario:
                            data = datetime.strptime(data_diario.group(1),'%Y_%m_%d')
                        else:
                            data = None

                        diario = diario_service.preenche_diario(nome_diario, data)

                        arquivo = arquivo_service.preenche_arquivo(arq,diario)
                except Exception as e:
                    print(e)

    def __converte_bloco_pdf(self, arqs, dir_entrada, dir_saida, dir_saida2):
        diario_service = DiarioService()
        arquivo_service = ArquivoService()

        total = 0
        erros = 0
        logs = ""

        for arq in arqs:
            ext = os.path.splitext(arq)[1]

            if ext:
                if ext == ".pdf":
                    try:
                        saida = os.path.join(dir_saida,
                                             os.path.splitext(arq)[0] + ".txt")

                        #Esta linha abaixo corresponde ao conversor antigo
                        # res = self.__converte_pdf(os.path.join(dir_entrada, arq), saida, False)

                        if 'JUCESP' in arq:
                            ano_cad = arq.split('_')[1]
                            mes_cad = arq.split('_')[2]
                            saida2 = os.path.join(dir_saida2,
                                                  os.path.splitext(arq)[0] + ".txt")
                            try:
                                contents, caminho_dir_html_completo = converte_jucesp_html(caminho_arquivo=os.path.join(dir_entrada, arq), filetype='pdf' if '.pdf' in arq else None, ano=ano_cad, mes=mes_cad, diario=arq)
                                checa_coluna_invertida(filepath=caminho_dir_html_completo,diario=arq.replace('.pdf','.html'), ano=ano_cad, mes=mes_cad)
                                continue
                            except Exception as e:
                                print(e)
                                print('Não foi possível converter o arquivo {}'.format(os.path.join(dir_entrada, arq)))
                                continue

                        # Linhas dentro deste IF correspondem ao conversor novo
                        if 'DJSP' in arq or True: # or True adicionado para que todos sejam convertidos pelo conversor novo
                            saida2 = os.path.join(dir_saida2,
                                                  os.path.splitext(arq)[0] + ".txt")
                            try:
                                res = self.__converte_pdf_novo(os.path.join(dir_entrada, arq), saida2, False)
                            except:
                                print('Não foi possível converter o arquivo {}'.format(os.path.join(dir_entrada, arq)))
                                # res = self.__converte_pdf_novo(os.path.join(dir_entrada, arq), saida2, False)

                        if res[0]:
                            total += 1
                            fm = FileManager(self.__nome, self.__log)
                            if 'producao' in default_schema:
                                fm.preenche_csv_arquivo_convertido(os.path.splitext(arq)[0])

                        logs += res[1]
                        nome_diario = arq.split('_')[0]
                        data_diario = re.search('(\d{4}_\d{2}_\d{2})',arq)
                        if data_diario:
                            data = datetime.strptime(data_diario.group(1),'%Y_%m_%d')
                        else:
                            data = None

                        diario = diario_service.preenche_diario(nome_diario, data)

                        nome_arquivo = os.path.splitext(arq)[0] + ".txt"
                        arquivo = arquivo_service.preenche_arquivo(nome_arquivo,diario)

                    except Exception as er:
                        erro = ("Erro: " + traceback.format_exc())
                        print(erro)
                        logs += erro + '\n'
                        erros += 1

        return total, erros, logs

    #TODO Criar conversão jusbrasil juntando todas as paginas em um txt
    def converte_html_jusbrasil(self, file):
        html = '<!DOCTYPE html> <html><body>'
        soup = BeautifulSoup(open(file))
        html = html + soup.find('article').encode('utf-8') + '</body></html>'
        text = html2text.html2text(html)
    #     Falta


    def __converte_pdf_novo_novo(self, pdf, saida, substituir):
        logs = ""
        fp = None
        device = None
        outfp = None

        try:
            if os.path.isfile(saida) and not substituir:
                log = ("{} já convertido. Pulando... ".format(os.path.split(pdf)[1]))
                print(log)
                logs += log + '\n'

                return False, logs
            else:
                log = ("Convertendo (método antigo) " + os.path.split(pdf)[1])
                print(log)
                logs += log + '\n'


                codec = 'utf-8'

                outfp = open(saida, 'w')

                fp = open(pdf, 'rb')

                # Load your PDF
                if fp:
                    pdf_text = pdftotext.PDF(fp)

                # How many pages?
                print(len(pdf_text))

                # Iterate over all the pages
                for page in pdf_text:
                    if page:
                        try:
                            outfp.writelines(page+'\n\n')
                        except:
                            pass

                # Read some individual pages
                # print(pdf[0])
                # print(pdf[1])

                # Read all the text into one string
                # print("\n\n".join(pdf))

                # for page in pages:
                #     page.rotate = (page.rotate+rotation) % 360
                #     if page:
                #         try:
                #             interpreter.process_page(page)
                #         except Exception as e:
                #             pass

                if fp:
                    fp.close()

                if device:
                    device.close()

                if outfp:
                    outfp.close()

                return True, logs

        except Exception as er:
            if fp:
                fp.close()

            if device:
                device.close()

            if outfp:
                outfp.close()

            if os.path.isfile(saida):
                os.remove(saida)

            raise er

    def __converte_pdf(self, pdf, saida, substituir):
        logs = ""
        fp = None
        device = None
        outfp = None

        try:
            if os.path.isfile(saida) and not substituir:
                log = ("{} já convertido. Pulando... ".format(os.path.split(pdf)[1]))
                print(log)
                logs += log + '\n'

                return False, logs
            else:
                log = ("Convertendo (método antigo) " + os.path.split(pdf)[1])
                print(log)
                logs += log + '\n'

                password = ''
                pagenos = set()
                maxpages = 0
                imagewriter = None
                rotation = 0
                codec = 'utf-8'
                caching = True
                laparams = LAParams()

                logging.getLogger('pdfminer').setLevel(logging.ERROR)

                rsrcmgr = PDFResourceManager(caching=caching)

                outfp = open(saida, 'w')

                device = TextConverter(rsrcmgr, outfp, laparams=laparams)

                fp = open(pdf, 'rb')
                parser = PDFParser(fp)
                doc = PDFDocument()
                parser.set_document(doc)
                doc.set_parser(parser)
                doc.initialize('')
                interpreter = PDFPageInterpreter(rsrcmgr, device)

                pages = list(doc.get_pages())
                #pages = list(PDFPage.get_pages(fp, pagenos,
                                              # maxpages=maxpages, password=password,
                                              # caching=caching, check_extractable=True))

                for page in pages:
                    page.rotate = (page.rotate+rotation) % 360
                    if page:
                        try:
                            interpreter.process_page(page)
                        except Exception as e:
                            pass

                if fp:
                    fp.close()

                if device:
                    device.close()

                if outfp:
                    outfp.close()

                return True, logs

        except Exception as er:
            if fp:
                fp.close()

            if device:
                device.close()

            if outfp:
                outfp.close()

            if os.path.isfile(saida):
                os.remove(saida)

            raise er

    def __converte_pdf_novo(self, pdf, saida, substituir):
        logs = ""
        fp = None
        device = None
        outfp = None

        try:
            if os.path.isfile(saida) and not substituir:
                log = ("{} já convertido. Pulando... ".format(os.path.split(pdf)[1]))
                print(log)
                logs += log + '\n'

                return False, logs
            else:
                log = ("Convertendo (novo conversor) " + os.path.split(pdf)[1])
                try:
                    print(log)
                except:
                    pass
                logs += log + '\n'

                outfp = open(saida, 'w')

                cmd = 'pdftohtml -hidden -q -c -s -i -xml {PDF} {XML} && ' \
                      'sed -e s/"<[^>]*>"//g {XML}'.format(PDF=pdf, XML=pdf.replace('.pdf', '.xml'), SAIDA=saida)

                process = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
                (text, err) = process.communicate()
                exit_code = process.wait()
                if os.path.isfile(pdf.replace('.pdf', '.xml')):
                    os.remove(pdf.replace('.pdf', '.xml'))

                if exit_code != 0:
                    raise Exception(err)

                try:
                    conv_text = str(text, encoding='utf-8')
                except:
                    conv_text = str(text, encoding='iso-8859-1')

                outfp.write(html.unescape(conv_text.strip()))

                if outfp:
                    outfp.close()

                return True, logs

        except Exception as er:
            if fp:
                fp.close()

            if device:
                device.close()

            if outfp:
                outfp.close()

            if os.path.isfile(saida):
                os.remove(saida)

            raise er


    def __converte_bloco_rtf(self, arqs, dir_entrada, dir_saida):
        total = 0
        erros = 0
        logs = ""

        for arq in arqs:
            ext = os.path.splitext(arq)[1]

            if ext:
                if ext == ".rtf":
                    try:
                        saida = os.path.join(dir_saida,
                                             os.path.splitext(arq)[0] + ".txt")

                        res = self.__converte_rtf(os.path.join(dir_entrada, arq), saida, True)

                        if res[0]:
                            total += 1
                            fm = FileManager(self.__nome, self.__log)
                            if 'producao' in default_schema:
                                fm.preenche_csv_arquivo_convertido(os.path.splitext(os.path.splitext(arq)[0]))
                        logs += res[1]
                    except Exception as er:
                        erro = ("Erro: " + traceback.format_exc())
                        print(erro)
                        logs += erro + '\n'
                        erros += 1

        return total, erros, logs


    def __converte_rtf(self, rtf, saida, substituir):
        logs = ""

        outfp = None

        try:
            if os.path.isfile(saida) and not substituir:
                log = ("{} já convertido. Pulando... ".format(os.path.split(rtf)[1]))
                print(log)
                logs += log + '\n'

                return False, logs
            else:
                log = ("Convertendo " + os.path.split(rtf)[1])
                print(log)
                logs += log + '\n'

                outfp = open(saida, 'w')

                #text = textract.process(rtf, encoding='utf_8')

                process = Popen(["unrtf", "--text", rtf], stdout=PIPE)
                (text, err) = process.communicate()
                exit_code = process.wait()

                if exit_code != 0:
                    raise Exception(err)

                try:
                    conv_text = str(text, encoding='iso-8859-1')
                except:
                    conv_text = str(text, encoding='utf-8')

                outfp.write(conv_text)

                if outfp:
                    outfp.close()

                return True, logs
        except Exception as er:
            if outfp is not None:
                outfp.close()

            if os.path.isfile(saida):
                os.remove(saida)

            raise er
