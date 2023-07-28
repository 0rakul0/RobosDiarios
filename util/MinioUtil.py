import os
import sys
import glob
import re
from minio import Minio
from bs4 import BeautifulSoup as bs
from datetime import datetime, date, timedelta, timezone
from minio.error import *
from subprocess import Popen, PIPE, STDOUT
'''
PARA LOGAR NO MINIO: mc alias set minio https://minio-spark-rj.ipea.gov.br ipeajus TXBkbR/+V3nDniAayy62jUi8YvjP/TMJF2w9yH7DNQc= --api S3v4dia
PARA SUBIR OS AQUIVOS VIA TERMINAL, USAR O COMANDO 'mc cp {caminho completo do arquivo sem / no final} minio/{pasta onde vai ficar no MinIO} -r'
'''

def faz_upload(bucket, ano,mes,estado,diario=None, filtro=None, ignorar_arquivos=None):
    minioClient = Minio('minio-spark-rj.ipea.gov.br', access_key='ipeajus', secret_key='TXBkbR/+V3nDniAayy62jUi8YvjP/TMJF2w9yH7DNQc=',secure=True)


    if diario:
        # PARA OS CASOS ONDE SE TEM UMA PASTA A MAIS PARA CHEGAR NA PASTA TXT
        diretorio_base = "/mnt/dmlocal/dados/{estado}/{diario}/txt".format(estado=estado,diario=diario)
    else:
        diretorio_base = "/mnt/dmlocal/dados/{estado}/txt".format(estado=estado)

    diretorio_final = f"{diretorio_base}/{ano}/{mes}"
    os.chdir(diretorio_final)
    files = glob.glob('*.*')

    # PARA PEGAR APENAS CADERNOS DE INTERESSE
    if filtro:
        files = list(filter(lambda file: file if re.search(filtro, file) else None, files))

    # PARA IGNORAR DETERMINADOS CADERNOS (MESMO QUE TENHAM SIDOS LISTADOS ACIMA)
    if ignorar_arquivos:
        files = list(filter(lambda file: file if not re.search(ignorar_arquivos, file) else None, files))

    # LISTA OS ARQUIVOS DE DETERMINADO BUCKET EM DETERMINADA PASTA (prefix) E VERIFICA TAMBÉM AS SUBPASTAS
    dir_obj = minioClient.list_objects(bucket, prefix=f'{ano}/{mes}', recursive=True)
    dir_content = [obj.object_name.replace(mes + '/', '') for obj in dir_obj]

    for file in files:
        # CASO O ARQUIVO NÃO EXISTA, PULA PRO PRÓXIMO
        if file is None:
            continue

        # SOBE OS ARQUIVOS QUE NÃO EXISTEM NO MINIO
        if not file in dir_content:
            minioClient.fput_object(bucket, f"{ano}/{mes}/{file}", file)
            print(f"Fez upload do arquivo {file} para o minio no bucket {bucket}")


def faz_upload_html_selenium(principal_vinculado, npu, bucket, minioClient=None):

    try:
        if not minioClient:
            minioClient = Minio('minio-spark-rj.ipea.gov.br', access_key='ipeajus', secret_key='TXBkbR/+V3nDniAayy62jUi8YvjP/TMJF2w9yH7DNQc=')

        if principal_vinculado.lower() == 'principal':
            diretorio = f"../dados/processos/principal/{npu}/{npu}.html"
        elif principal_vinculado.lower() == 'vinculados':
            diretorio = f"../dados/processos/vinculados/{npu}/{npu}.html"
        else:
            print(f'Tipo {principal_vinculado} não existente. Passe "principal" ou "vinculados" no parâmetro principal_vinculado')
            return

        if not minioClient.bucket_exists(bucket):
            minioClient.make_bucket(bucket)
            print(f'Criando o bucket {bucket}')

        try:
            minioClient.fput_object(f'{bucket}', f"{principal_vinculado}/{npu}/{npu}.html", diretorio)
            print(f'Arquivo {npu}.html inserido com sucesso no bucket {bucket} do Minio')
            return True, minioClient
        except Exception as e:
            print(e)
            return False, minioClient

    except Exception as e:
        print(e)
        return False, minioClient


def get_htmls_selenium(bucket, principal_vinculado=None, return_minio_client=False):

    minioClient = Minio('minio-spark-rj.ipea.gov.br', access_key='ipeajus', secret_key='TXBkbR/+V3nDniAayy62jUi8YvjP/TMJF2w9yH7DNQc=', secure=True)

    if not minioClient.bucket_exists(bucket):
        minioClient.make_bucket(bucket)
        print(f'Criando o bucket {bucket}')

    dir_obj = minioClient.list_objects(bucket, prefix=f'{principal_vinculado}' if principal_vinculado else None, recursive=True)

    if not return_minio_client:
        return [obj.object_name for obj in dir_obj]
    else:
        return[obj.object_name for obj in dir_obj], minioClient


def download_file_minio(bucket, npu, apenas_principal=False):

    minioClient = Minio('minio-spark-rj.ipea.gov.br', access_key='ipeajus', secret_key='TXBkbR/+V3nDniAayy62jUi8YvjP/TMJF2w9yH7DNQc=')
    part = None

    if not minioClient.bucket_exists(bucket):
        minioClient.make_bucket(bucket)
        print(f'Criando o bucket {bucket}')

    if not apenas_principal:
        try:
            part = minioClient.get_object(bucket, f'vinculados/{npu}/{npu}.html')
        except:
            part = None

    if not part:
        try:
            part = minioClient.get_object(bucket, f'principal/{npu}/{npu}.html')
        except:
            part = None

    if part:
        arquivo = part.data.decode()

        return bs(arquivo, 'html.parser')

    else:
        return None


def get_data_atualizacao_arquivo(bucket, files, range_data_atualizacao, apenas_principal=False):

    if type(files) is str:
        files = [files]

    lista_arquivos_minio, minioClient = get_htmls_selenium(bucket, return_minio_client=True, principal_vinculado='principal' if apenas_principal else None)
    path_date_file_list = []

    # TODO: GARGALO POIS A COMPLEXIDADE DESSE FOR DE UMA LINHA É  PARA CADA 1 ITEM VEZES LEN ARQUIVOS MINIO VEZES LEN FILES (ITEM * len(FILES_MINIO) * len(FILES))
    for file in files: #FOR PARA PEGAR OS CAMINHOS DOS ARQUIVOS NO MINIO E SUAS DATAS DE MODIFICAÇÃO
        try:
            path_date_file_list.append([(item_minio, minioClient.stat_object(bucket, item_minio).last_modified) for item_minio in lista_arquivos_minio if re.search(file, item_minio) is not None][0])
        except:
            continue

    path_file_filtered_list = [re.search('\d+', path).group(0) for path, data_arquivo in path_date_file_list if data_arquivo+timedelta(days=range_data_atualizacao) >= datetime.today().astimezone(timezone.utc)]

    try:
        return path_file_filtered_list
    except:
        return None


def juntar_arquivos(bucket_name, pasta, file_path, prefix_out_file):

    # FAZ CONEXÃO COM O SERVIDOR DO MINIO
    minioClient = Minio('minio-spark-rj.ipea.gov.br', access_key='ipeajus', secret_key='TXBkbR/+V3nDniAayy62jUi8YvjP/TMJF2w9yH7DNQc=',secure=True)


    # LISTA OS ARQUIVOS DE DETERMINADO BUCKET EM DETERMINADA PASTA (prefix)
    dir_obj = minioClient.list_objects(bucket_name,prefix=pasta+'/'+file_path,recursive=True)

    # REMOVENDO OS ARQUIVOS COM 0 BYTES
    dir_content = list(filter(lambda file: file.size != 0, list(dir_obj)))

    # CRIA UM FOR DE UMA LINHA PARA COLETAR APENAS OS NOMES DOS ARQUIVOS TRAZIDOS DO MINIO
    dir_content = [obj.object_name for obj in dir_content]

    # CAMINHO DO ARQUIVO DE SAÍDA
    merged_file = prefix_out_file + file_path

    print(f'Criando o arquivo {merged_file}')

    with open(merged_file, 'w') as f:

        # FOR PARA PEGAR OS ARQUIVOS E MESCLAR EM APENAS UM CSV
        for arq_pos, file in enumerate(dir_content, 1):
            print(f'{arq_pos}/{len(dir_content)} - Fazendo merge do arquivo {file}')
            part = minioClient.get_object(bucket_name, file)
            f.write(part.data.decode())
            f.flush()
        f.close()
        print(f'Criou o arquivo {merged_file}')



#get_data_atualizacao_arquivo('processostjspv2', '00047480520188260565', 7)
#download_file_minio('processostjsp', '10060970220178260358')


# for ano in range(2010,2021):
#     juntar_arquivos("resultado", "DJSP","DJSP_blocos_"+str(ano)+".csv", "../Merged")

for ano in range(2010,2021):
    juntar_arquivos("resultado", "TRT_152aRegiao_blocos_"+str(ano)+".csv", "../Merged_")

# import pandas as pd
#
# data = pd.read_csv('../Merged_DJSP_blocos_Tortura_2019_v2.csv', sep=';', header=None)
# print(data)

# for ano in range(2014, 2021):
#     for mes in range(1,13):
#         if mes < 10:
#             mes = '0'+str(mes)
#         else:
#             mes = str(mes)
#
#         faz_upload('trt', ano, mes, 'DEJT', filtro='ju[dr].*?(_2a|\w_02_\d{4})')
