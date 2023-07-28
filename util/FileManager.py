# -*- coding: utf-8 -*-
import csv
from pdjus.conexao.Conexao import default_schema
import sys
import os
import re
import time
from datetime import datetime, date, timedelta
from urllib.request import Request, urlopen
import requests
from PyPDF2 import PdfFileReader, PdfFileMerger
from util.ConfigManager import ConfigManager
from util.mailer import Mailer
from collections import Counter
from util.StringUtil import range_da_semana
import ast

class DiarioNaoDisponivel(Exception):
    pass

class MaxTentativasExcedidas(Exception):
    pass

class MaxTentativasCaptchas(Exception):
    pass

class FileManager(object):

    def __init__(self, robo, log=None, erro=None):
        self.__robo = robo
        self.__log = log
        self.__erro = erro
        self.__timeout = 100
        pass

    @property
    def path(self):
        return ConfigManager().le_config(self.__robo)

    @property
    def timeout(self):
        return self.__timeout

    def caminho(self, name, data = None, por_tipo=True, sufixo="", subfolders=None):

        if por_tipo:

            try:
                str_subfolders = ""
                if subfolders:
                    str_subfolders = os.path.join(str_subfolders, *subfolders)
                    arquivo = os.path.join(self.path, str_subfolders,
                                           (os.path.splitext(name)[1].split('.')[1] + sufixo) if name.find(
                                               ".") >= 0 else (name.strip() + sufixo))
                else:
                    arquivo = os.path.join(self.path,
                                       (os.path.splitext(name)[1].split('.')[1] + sufixo) if name.find(".") >= 0 else (name.strip() + sufixo))
            except:
                ConfigManager().escreve_log(name + " - extensão desconhecida. Salvando no "
                                                   "diretório de desconhecidos...", self.__robo, self.__log)
                arquivo = os.path.join(self.path, "desconhecidos")

            if data is None:
                data = self.obter_data(name)

            if data is None:
                path = os.path.join(arquivo, "sem_data")
            else:
                path = os.path.join(arquivo, str(data.year).zfill(4), str(data.month).zfill(2))
        else:
            str_subfolders = ""
            if subfolders:
                str_subfolders = os.path.join(str_subfolders, *subfolders)
                path = os.path.join(self.path, str_subfolders)
            else:
                path = self.path

        if not os.path.exists(path):
            os.makedirs(path)

        return path

    def ja_baixado(self, name, data=None, por_tipo=True, modo=False, subfolders=None):
        """
        :param name: filename do arquivo a ser checado
        :param data: data do diario
        :param por_tipo: ?
        :param modo: se verdadeiro, dada uma parte, busca não só a existência da parte
                    mas também o diário consolidado (após merge das partes)
        :return: True / False
        """

        if data is None:
            data = self.obter_data(name)

        if modo:  # buscar nome exato e nome sem sequencial
            # padrao do nome do diario: ROBONAME_CADERNO_YYYY_MM_DD[_SEQ].pdf
            name = re.search('(.{3,}_[0-9]{0,1}[0-9]{0,1}[\_]{0,1}[A-Z]{3,8}_.{10})[\_0-9]{0,}\.pdf', name).group(1)+".pdf"

        path = self.caminho(name, data, por_tipo, subfolders=subfolders)
        # checar se existe o arquivo
        return os.path.isfile(os.path.join(path, name))

    def download(self, name, data, url, substituir=False, por_tipo=True, tentativas=3, session=requests.Session(), params_post=None, subfolders=None, stream=False, cookies=None,headers=None,proxies=None, print_baixou=True):
        # requests.packages.urllib3.disable_warnings()
        ja_existe = False
        path = self.caminho(name, data, por_tipo, subfolders=subfolders)

        baixou = False  # indica se foi feito o download do arquivo ou algo aconteceu. por exemplo: o arquivo já existe.

        if not os.path.exists(path):
            os.makedirs(path)

        ext = os.path.splitext(name)[1].replace('.', '')

        if self.ja_baixado(name, data, por_tipo, subfolders=subfolders) and not substituir:
            ConfigManager().escreve_log("{} já existe. Pulando...".format(name), self.__robo, self.__log)
            ja_existe = True
        else:
            i = 0
            sucesso = False
            erro = None

            while i < tentativas and not sucesso:
                try:
                    # if session is None:
                    #     if not params_post:
                    #         res = requests.get(url, verify=False, timeout=self.__timeout, stream=stream)
                    #     else:
                    #         res = requests.post(url, params_post, verify=False, timeout=self.__timeout,
                    #                                 stream=stream, cookies=cookies)
                    # else:
                    if not params_post:
                        res = session.get(url, verify=False, timeout=self.__timeout, stream=stream, cookies=cookies, proxies=proxies,headers=headers)
                    else:
                        res = session.post(url, params_post, verify=False, timeout=self.__timeout, stream=stream, cookies=cookies, proxies=proxies,headers=headers)

                    # if mimetypes.guess_type(name)[0] in res.headers['content-type']:
                    try:
                        if res.status_code == 404:
                            erro = FileNotFoundError("Erro 404")
                            i += 1
                        elif self.erro_download(res, ext):
                            erro = DiarioNaoDisponivel("Diário não disponível na data solicitada.")
                            sucesso = True
                            i += 1
                        else:
                            erro = None
                            if not stream:
                                with open(os.path.join(path, name), 'wb') as f:
                                    f.write(res.content)
                                    f.flush()
                                    os.fsync(f.fileno())
                            else:
                                with open(os.path.join(path, name), 'wb') as f:
                                    for chunk in res.iter_content(chunk_size=1024):
                                        if chunk:  # filter out keep-alive new chunks
                                            f.write(chunk)

                            sucesso = True
                            if 'producao' in default_schema:
                                self.preenche_csv_arquivo_baixado(name) # cria arquivos semanais informando quais foram baixados
                            if print_baixou:
                                ConfigManager().escreve_log("Baixou o arquivo  {}".format(name), self.__robo, self.__log)
                            baixou = True
                    except Exception as e:
                        erro = e
                        i += 1
                except Exception as er:
                    erro = er
                    i += 1
                    if os.path.isfile(os.path.join(path, name)):
                        os.remove(os.path.join(path, name))
                    ConfigManager().escreve_log("Erro em {}. Tentativa {}...".format(name, i), self.__robo, self.__erro)


            if not sucesso:
                if erro is not None:
                    if i >= tentativas:
                        raise MaxTentativasExcedidas("Número de tentativas de download excedidas: " + str(erro))
                    else:
                        raise erro
                else:
                    raise Exception("Erro desconhecido no download.")

        return baixou, ja_existe

    def download_urlopen(self, name, data, url, substituir=False, por_tipo=True, tentativas=3, subfolders=None, stream=False, headers=None):
        # USADO PARA O ROBO TRF02 ONDE O SITE POSSUI UMA CAMADA DE SEGURANÇA PRO REQUEST.GET, ENTÃO SE UTILIZA O URLLIB + URLOPEN
        path = self.caminho(name, data, por_tipo, subfolders=subfolders)

        baixou = False  # indica se foi feito o download do arquivo ou algo aconteceu. por exemplo: o arquivo já existe.

        if not os.path.exists(path):
            os.makedirs(path)

        ext = os.path.splitext(name)[1].replace('.', '')

        if self.ja_baixado(name, data, por_tipo, subfolders=subfolders) and not substituir:
            ConfigManager().escreve_log("{} já existe. Pulando...".format(name), self.__robo, self.__log)
        else:
            i = 0
            sucesso = False
            erro = None

            while i < tentativas and not sucesso:
                try:
                    res = Request(url, headers=headers)
                    res = urlopen(res)

                    try:
                        if res.code == 404:
                            erro = FileNotFoundError("Erro 404")
                            i += 1
                        elif self.erro_download(res, ext):
                            erro = DiarioNaoDisponivel("Diário não disponível na data solicitada.")
                            sucesso = True
                            i += 1
                        else:
                            erro = None
                            if not stream:
                                with open(os.path.join(path, name), 'wb') as f:
                                    f.write(res.read())
                                    f.flush()
                                    os.fsync(f.fileno())
                            else:
                                with open(os.path.join(path, name), 'wb') as f:
                                    for chunk in res.iter_content(chunk_size=1024):
                                        if chunk:  # filter out keep-alive new chunks
                                            f.write(chunk)

                            sucesso = True
                            if 'producao' in default_schema:
                                self.preenche_csv_arquivo_baixado(name) # cria arquivos semanais informando quais foram baixados
                            ConfigManager().escreve_log("Baixou o arquivo  {}".format(name), self.__robo, self.__log)
                            baixou = True
                    except Exception as e:
                        erro = e
                        i += 1
                except Exception as er:
                    erro = er
                    i += 1
                    if os.path.isfile(os.path.join(path, name)):
                        os.remove(os.path.join(path, name))
                    ConfigManager().escreve_log("Erro em {}. Tentativa {}...".format(name, i), self.__robo, self.__erro)

            if not sucesso:
                if erro is not None:
                    if i >= tentativas:
                        raise MaxTentativasExcedidas("Número de tentativas de download excedidas: " + str(erro))
                    else:
                        raise erro
                else:
                    raise Exception("Erro desconhecido no download.")

        return baixou

    def download_stream(self, name, data, bytes, substituir=False, por_tipo=True):
        path = self.caminho(name, data, por_tipo)

        erro = None

        if self.ja_baixado(name, data, por_tipo) and not substituir:
            ConfigManager().escreve_log("{} já existe. Pulando...".format(name), self.__robo, self.__log)
        else:
            sucesso = False
            i = 0

            try:
                pdf = open(os.path.join(path, name), 'wb')
                pdf.write(bytes)
                pdf.close()
                sucesso = True
                ConfigManager().escreve_log("Baixou o diario  {}".format(name), self.__robo, self.__log)
            except Exception as er:
                erro = er
                i += 1
                if os.path.isfile(os.path.join(path, name)):
                        os.remove(os.path.join(path, name))
                ConfigManager().escreve_log("Erro em {}.".format(name), self.__robo, self.__erro)

            if not sucesso:
                if erro is not None:
                    raise erro
                else:
                    raise Exception("Erro desconhecido no download.")

    def juntar_pdfs(self, saida, pdfs, apagar_arquivos=False, ordenar=True):

        saida = saida+'.tmp'

        if ordenar:
            pdfs.sort()

        if pdfs and len(pdfs)>0:

            merger = PdfFileMerger(strict=False)
            erro = False

            for filename in pdfs:

                try:
                    with open(filename, 'rb') as f:
                        merger.append(PdfFileReader(f, strict=False))
                except Exception as e:
                    os.unlink(filename)
                    ConfigManager().escreve_log(" - {ARQ} foi removido para nova tentativa de download".format(
                        ARQ=filename),"TRF", "erro_junta_pdf.log")
                    erro = True

            if erro:
                merger.close()
                return

            try:

                merger.write(saida)
                merger.close()
                #os.unlink(saida.split('.tmp')[0])
                os.rename(saida, saida.split('.tmp')[0])

            except Exception as er:
                print(er)
                ConfigManager().escreve_log("Erro em {}.".format(saida), self.__robo, self.__erro)
                os.remove(saida)
                return

            try:
                if apagar_arquivos:
                    for pdf in pdfs:
                        os.remove(pdf)
            except:
                ConfigManager().escreve_log("Erro ao apagar arquivos. {}.".format(saida), self.__robo, self.__erro)


    def data_ultimo_arquivo(self, filtro, tipo_arquivo="*.pdf", por_tipo=True, subfolders=None):

        str_subfolders = ""
        if subfolders:
            str_subfolders = os.path.join(str_subfolders, *subfolders)

        if por_tipo:
            path_download = os.path.join(self.path, str_subfolders, os.path.splitext(tipo_arquivo)[1].split('.')[1])
        else:
            path_download = self.path

        if not os.path.exists(path_download):
            os.makedirs(path_download)

        ultimo = self.__obter_mais_recente(filtro, path_download)

        try:
            s_data = re.search('([0-9]){4}_([0-9]){2}_([0-9]){2}', ultimo).group(0)
            return datetime.strptime(s_data, '%Y_%m_%d')
        except:
            return None


    def ultimo_arquivo(self, filtro, tipo_arquivo="*.pdf", por_tipo=True):
        if por_tipo:
            path_download = os.path.join(self.path, os.path.splitext(tipo_arquivo)[1].split('.')[1])
        else:
            path_download = self.path

        if not os.path.exists(path_download):
            os.makedirs(path_download)
        return self.__obter_mais_recente(filtro, path_download)

    def __obter_mais_recente(self, filtro, path):
        dirs = []
        files = []

        for f in os.listdir(path):
            if os.path.isdir(os.path.join(path, f)):
                dirs.append((os.path.join(path, f)))
            if f.find(filtro) >= 0 or filtro is None or filtro == '':
                files.append((os.path.join(path, f)))

        dirs = sorted(dirs, reverse=True)
        files = sorted(files, reverse=True)
        if len(dirs) > 0:
            if "sem_data" in dirs[0]:
                dirs = dirs[1:]
        if len(files) > 0:
            if "sem_data" in files[0]:
                files = files[1:]
        ls = dirs + files

        if len(ls) > 0:
            mais_recente = None
            atual = 0

            while not mais_recente and atual < len(ls):
                if os.path.isfile(ls[atual]):
                    mais_recente = ls[atual]
                else:
                    mais_recente = self.__obter_mais_recente(filtro, ls[atual])

                atual += 1

            return mais_recente
        return None


    def obter_data(self, nome_arquivo):
        data = re.search('.*([12]\d{3}_[01]\d_[0123]\d)',nome_arquivo)
        data = data.group(1) if (data is not None) else data
        if data:
            return datetime.strptime(data, "%Y_%m_%d")
        else:
            return None

    def __listar_datas_arquivos(self, tipo_arquivo, data_inicio):
        datas = []

        ext = os.path.splitext(tipo_arquivo)[1].split('.')[1].lower() \
                                if tipo_arquivo.find('\.') >= 0 else tipo_arquivo.lower()

        for dir_tipo in os.listdir(self.path):
            if dir_tipo.lower() == ext:
                diretorios_anos_completos = sorted(os.listdir(os.path.join(self.path, dir_tipo)), reverse=True) # Mudar para True quando quiser rodar do atual para trás
                if "sem_data" in diretorios_anos_completos[-1]:
                    diretorios_anos_completos = diretorios_anos_completos[:-1]
                diretorios_anos_maiores = [i for i in diretorios_anos_completos if data_inicio is None or int(i) >= int(data_inicio.year)]
                for dir_ano in diretorios_anos_maiores:
                    if os.path.isdir(os.path.join(self.path, dir_tipo, dir_ano)):
                        try:
                            ano = int(dir_ano)
                            diretorios_meses = sorted(os.listdir(os.path.join(self.path, dir_tipo, dir_ano)), reverse=False)
                            for dir_mes in diretorios_meses:
                                if os.path.isdir(os.path.join(self.path, dir_tipo, dir_ano, dir_mes)):
                                    mes = int(dir_mes)

                                    arqs_dir = sorted(os.listdir(os.path.join(self.path, dir_tipo, dir_ano, dir_mes)), reverse=False)
                                    if len(arqs_dir) > 0:
                                        contem_tipo = self.verifica_se_arquivos_contem_tipo(arqs_dir,ext)
                                        if contem_tipo:
                                            dt = date(ano, mes, 1)

                                            if data_inicio is None:
                                                datas.append(dt)
                                            elif dt >= data_inicio.date():
                                                datas.append(dt)
                        except Exception:
                            if os.path.isdir(os.path.join(self.path, dir_tipo,'sem_data')):
                                arqs_dir= sorted(os.listdir(os.path.join(self.path, dir_tipo,'sem_data')), reverse=False)
                                contem_tipo = self.verifica_se_arquivos_contem_tipo(arqs_dir, ext)
                                if contem_tipo:
                                    datas.append(None)
        return sorted(datas, reverse=True) # Mudar para True quando quiser rodar do atual para trás

    def listar_datas_baixadas(self, tipo_arquivo):
        return self.__listar_datas_arquivos(tipo_arquivo, None)

    def listar_datas_convertidas(self):
        return self.__listar_datas_arquivos('txt', None)

    def listar_datas_conversao_pendente(self, tipo_arquivo, converte_tudo=None):

        if not converte_tudo:
            if 'DJMG' in self.__robo and tipo_arquivo == 'rtf':
                ult_txt = None
                data_inicio = None
                return self.__listar_datas_arquivos(tipo_arquivo, data_inicio)

            if 'DJSP' in self.__robo or 'TRF' in self.__robo:
                ult_txt = None

            else:
                ult_txt = self.data_ultimo_arquivo('', '*.txt')
        else:
            ult_txt = None
            data_inicio = None
            return self.__listar_datas_arquivos(tipo_arquivo, data_inicio)

        if ult_txt:
            data_inicio = (ult_txt.replace(day=1) - timedelta(1)).replace(day=1)
        else:
            data_inicio = None

        return self.__listar_datas_arquivos(tipo_arquivo, data_inicio)

    def verifica_se_arquivos_contem_tipo(self,arqs_dir,ext):
        if len(arqs_dir) > 0:
            for i in range(0,len(arqs_dir)):
                if os.path.splitext(arqs_dir[i])[1].split('.')[1].endswith(ext):
                    return True
        return False

    def listar_arquivos_data(self, data, tipo_arquivo, caminho_completo=False):
        files = []

        dir = self.caminho(tipo_arquivo, data)
        ext = os.path.splitext(tipo_arquivo)[1].split('.')[1] \
                            if tipo_arquivo.find('\.') >= 0 else tipo_arquivo

        for f in os.listdir(dir):
            if os.path.splitext(f)[1].split('.')[1].endswith(ext):
                files.append(os.path.join(dir, f) if caminho_completo else f)

        return files

    #apenas para não ficar definindo a tarefa na chamada dos métodos
    def preenche_csv_arquivo_baixado(self,nome_arquivo):
        self.preenche_csv(nome_arquivo,'Baixado',False)
    def preenche_csv_arquivo_convertido(self,nome_arquivo):
        self.preenche_csv(nome_arquivo,'Convertido',False)

    def preenche_csv_arquivo_extraido(self,nome_arquivo):
        self.preenche_csv(nome_arquivo,'Extraido',True)


    #tarefa = 'Baixado', 'Convertido' ou 'Extraido'
    def preenche_csv(self, nome_arquivo,tarefa,cria_diariamente=False):
        arquivo = self.cria_csv(tarefa,cria_diariamente)
        primeiro_nome = nome_arquivo.split('_')[0]
        data_caderno = re.search("\d{4}_\d{2}_\d{2}",nome_arquivo)
        if data_caderno:
            try:
                data = time.strptime(data_caderno.group(0),"%Y_%m_%d")
                data = time.strftime("%d/%m/%Y",data)
            except:
                data = 'sem_data'
        else:
            data = 'sem_data'
        texto_tarefa = '{} em'.format(tarefa) #Convertido em ou Baixado em
        with open(arquivo,'a',newline='') as csvfile:
            fieldnames = ['Diario', 'Nome do Arquivo', 'Data do caderno', texto_tarefa]
            writer = csv.DictWriter(csvfile,fieldnames=fieldnames,quoting=csv.QUOTE_ALL, delimiter=';')
            writer.writerow({'Diario':primeiro_nome,'Nome do Arquivo':nome_arquivo,'Data do caderno':data,texto_tarefa:datetime.now().strftime(("%d/%m/%Y %H:%M:%S"))})
            csvfile.close()

    def cria_csv(self,tarefa,cria_diariamente=False):
        if tarefa == 'Baixado':
             nome_arquivo = "Downloads"
        elif tarefa == 'Convertido':
            nome_arquivo = 'Convertidos'
        else:
            nome_arquivo = "Extraidos"
        if cria_diariamente:
            data_atual = datetime.today()
            nome_arquivo += "_{ano}_{mes:02d}_{dia:02d}.csv".format(ano=data_atual.year, mes=data_atual.month, dia=data_atual.day)
        else: #cria um arquivo semanalmente
            data_semanal = datetime.now().isocalendar()
            nome_arquivo += "_{ano}_{semana:02d}.csv".format(ano=data_semanal[0], semana=data_semanal[1])
        path = ConfigManager().le_config("RELATORIOS")
        nome_arquivo = os.path.join(path,nome_arquivo)
        if not os.path.isdir(path):
            os.makedirs(path)
        if not os.path.isfile(nome_arquivo):
            relatorios = os.listdir(path)
            if len(relatorios) > 0:
                if tarefa == 'Convertido' or tarefa == 'Extraido':
                    relatorios_tarefa = [row for row in relatorios if tarefa in row]
                else: #tarefa == 'Baixado'
                    relatorios_tarefa = [row for row in relatorios if 'Downloads' in row]
                if len(relatorios_tarefa) > 0:
                    relatorios_tarefa.sort()
                    relatorio_mais_recente = relatorios_tarefa[-1]
                    self.envia_email(tarefa+'s', os.path.join(path,relatorio_mais_recente),cria_diariamente)
            with open(nome_arquivo,'w',newline='') as csvfile:
                fieldnames = ['Diario','Nome do Arquivo','Data do caderno','{} em'.format(tarefa)]
                writer = csv.DictWriter(csvfile,fieldnames=fieldnames,quoting=csv.QUOTE_ALL, delimiter=';')
                writer.writeheader()
        return nome_arquivo

    def envia_email(self,tarefa, anexo=None,cria_diariamente=False):
        if anexo:
            if not cria_diariamente:
                match_data_semanal = re.search('_(\d{4})_(\d{2})\.',anexo)
                if match_data_semanal:
                    inicio,final = range_da_semana(match_data_semanal.group(2),match_data_semanal.group(1))
                    assunto = "Relatório semanal de {} em {} até {}".format(tarefa.lower(),inicio,final)
            else:
                match_data_diaria = re.search('_(\d{4})_(\d{2})_(\d{2})\.',anexo)
                if match_data_diaria:
                    assunto = "Relatório de {} do dia {}/{}/{}".format(tarefa.lower(),match_data_diaria.group(3),match_data_diaria.group(2),match_data_diaria.group(1))
            if not assunto:
                assunto = 'Relatório de {}'.format(tarefa.lower())

            try:
                mailer = Mailer()
                texto = self.gera_resumo_diarios_agregado(tarefa,anexo)
                mailer.send_email(assunto, texto ,anexo)
            except:
                pass


    def gera_resumo_diarios_agregado(self, tarefa, arquivo):
        if os.path.isfile(arquivo) and arquivo.endswith('.csv'):
            csvfile = open(arquivo)
            fieldnames = ['Diario','Nome do Arquivo','Data do caderno','{} em'.format(tarefa)]
            reader = csv.DictReader(csvfile,fieldnames=fieldnames,quoting=csv.QUOTE_ALL, delimiter=';')
            next(reader)
            diarios = [row['Diario'] for row in reader]
            resumo = "Resumo dos arquivos {}:\n\n".format(tarefa.lower())
            for (k,v) in Counter(diarios).items():
                resumo += str(k) + " = " + str(v) + ' arquivos\n\n'
            resumo += "Os dados detalhados seguem em anexo."

            return resumo

    def erro_download(self, res, ext):
        erro = False

        if 'Content-Type' in res.headers and not self.mimetype_valido(res.headers['Content-Type'], ext):
            erro = True

        return erro

    def verificar_pdf(self, arq):
        try:
            PdfFileReader(open(arq, 'rb'))
            return True
        except:
            return False

    def mimetype_valido(self, mime, ext):
        ext = ext.replace('*', '').replace('.', '')

        if ext == "pdf":
            if not mime.startswith("application/pdf") and \
                            not mime.startswith("application/x-pdf") and \
                            not mime.startswith('application/octet-stream') and \
                            not mime.startswith('multipart/form-data'):
                return False
            else:
                return True
        else:
            return True

    def juntar_arquivos_txt(self, path_files, exit_file):

        all_filenames = [caminhho_arquivo for caminhho_arquivo in os.listdir(os.path.abspath(path_files)) if not os.path.isdir(caminhho_arquivo)]

        for file in all_filenames:

            print('Juntando o arquivo {} ao arquivo {}.txt'.format(file, exit_file))

            with open(f'{path_files}/{exit_file}.txt', 'a+', encoding='utf-8') as f:
                try:
                    f.writelines('\n'.join(open(f'{path_files}/{file}', encoding='utf-8').readlines()))
                except:
                    for line in open(f'{path_files}/{file}', encoding='utf-8').readlines():
                        f.write(f'{line}\n')

            f.close()

# if __name__ == '__main__':
#     file_manager = FileManager(robo=None)
#     file_manager.juntar_arquivos_txt('../dados/validacao_cnae', 'validacao_porcentagem_classificados_cnae')