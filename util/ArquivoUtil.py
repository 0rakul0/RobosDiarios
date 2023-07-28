import os
import re
import pandas as pd
import csv
import glob
from pathlib import Path
import random
from pdjus.service.ArquivoService import ArquivoService


def verifica_arquivos_com_paginas_sem_merge(caminho, pdf_ou_txt):

    arquivos = []
    lista_arquivos = sorted(list(filter(lambda arq: arq[-1].isdigit(), list(glob.glob(caminho + '/*')))))

    for arquivo in lista_arquivos:
        arquivos_pasta = [str(i) for i in Path(f'{arquivo}').rglob(f'*.{pdf_ou_txt.lower()}')]
        arquivo_pasta = list(filter(lambda arq: re.search('\d{4}_\d{2}_\d{2}_\d{4}', arq), arquivos_pasta))
        arquivos.append(arquivo_pasta)

    arquivos = sorted([item for sublista in list(filter(lambda arq: arq != [], arquivos)) for item in sublista])

    print(arquivos)
    

def lista_acervo_gloob():

    # pastas_busca = ['/mnt/dmlocal/dados/AC/DJAC','/mnt/dmlocal/dados/AL/DJAL','/mnt/dmlocal/dados/AM/DJAM','/mnt/dmlocal/dados/AP/DJAP','/mnt/dmlocal/dados/BA/DJBA','/mnt/dmlocal/dados/CE/DJCE','/mnt/dmlocal/dados/DEJT','/mnt/dmlocal/dados/DF/DJDF','/mnt/dmlocal/dados/DOU','/mnt/dmlocal/dados/ES/DJES','/mnt/dmlocal/dados/GO/DJGO','/mnt/dmlocal/dados/MA/DJMA','/mnt/dmlocal/dados/MG/DJMG','/mnt/dmlocal/dados/MS/DJMS','/mnt/dmlocal/dados/MT/DJMT','/mnt/dmlocal/dados/PA/DJPA','/mnt/dmlocal/dados/PB/DJPB','/mnt/dmlocal/dados/PE/DJPE','/mnt/dmlocal/dados/PI/DJPI','/mnt/dmlocal/dados/PR/DJPR','/mnt/dmlocal/dados/RJ/DJRJ','/mnt/dmlocal/dados/RN/DJRN','/mnt/dmlocal/dados/RO/DJRO','/mnt/dmlocal/dados/RR/DJRR','/mnt/dmlocal/dados/RS/DJRS','/mnt/dmlocal/dados/SC/DJSC','/mnt/dmlocal/dados/SE/DJSE','/mnt/dmlocal/dados/SP/DJSP','/mnt/dmlocal/dados/SP/JUCESP','/mnt/dmlocal/dados/SP/TRTSP','/mnt/dmlocal/dados/STJ','/mnt/dmlocal/dados/TO/DJTO','/mnt/dmlocal/dados/TRF/TRF01','/mnt/dmlocal/dados/TRF/TRF02','/mnt/dmlocal/dados/TRF/TRF03','/mnt/dmlocal/dados/TRF/TRF04','/mnt/dmlocal/dados/TRF/TRF05']

    pastas_busca = glob.glob('/mnt/dmlocal/dados/*/*/pdf')
    pastas_busca = [caminho.replace('/pdf','') for caminho in pastas_busca]

    for busca in pastas_busca:
        caderno = busca.split('/')[-1]

        # print('Gerando lista de aquivos PDF para {}'.format(busca))
        all_files_pdf = [str(i) for i in Path(f'{busca}/pdf').rglob('*.pdf')]

        # print('Gerando lista de aquivos TXT para {}'.format(busca))
        all_files_txt = [str(i) for i in Path(f'{busca}/txt').rglob('*.txt')]

        if len(all_files_pdf) != 0:
            write_file(all_files_pdf, 'pdf', caderno)

        if len(all_files_txt) != 0:
            write_file(all_files_txt, 'txt', caderno)


def write_file(files, ext_file, caderno):

    caminho_arq_saida = '/mnt/ipeajus-temp/lista_acervo'

    if os.path.exists(caminho_arq_saida + '/lista_acervo_diarios_{caderno}_{ext_file}.csv'.format(caderno=caderno,ext_file=ext_file)):
        os.remove(caminho_arq_saida + '/lista_acervo_diarios_{caderno}_{ext_file}.csv'.format(caderno=caderno,ext_file=ext_file))

    print('Criando arquivo lista_acervo_diarios_{caderno}_{ext_file}.csv'.format(caderno=caderno,ext_file=ext_file))

    with open(caminho_arq_saida + f'/lista_acervo_diarios_{caderno}_{ext_file}.csv'.format(caderno=caderno,ext_file=ext_file), mode='a+', encoding='utf-8', errors='surrogateescape') as csvfile:
        escrevelinha = csv.writer(csvfile, delimiter='\n', quoting=csv.QUOTE_MINIMAL)
        escrevelinha.writerow(files)
        csvfile.close()


def lista_nome_tamanho_arquivos_na_pasta(pasta_arquivos):
    '''
    Exemplo de caminho: /mnt/dmlocal/dados/SP/DJSP/txt/
    '''
    arquivo_service = ArquivoService()
    pasta_pdf = Path(pasta_arquivos)

    for arquivo in pasta_pdf.glob ('**/*'):
        if arquivo.is_file():
            if os.path.exists(arquivo):

                nome_arquivo = arquivo.name
                tamanho_arquivo = arquivo.stat().st_size/1000000

                print(f'Arquivo {nome_arquivo} com tamanho de {tamanho_arquivo}MB')

                arquivo_banco = arquivo_service.dao.get_por_nome_arquivo(nome_arquivo)

                if arquivo_banco is None:
                    continue

                arquivo_banco.tamanho = str(tamanho_arquivo)
                arquivo_service.dao.salvar(arquivo_banco)


def conta_quantidade_diarios_pdf_txt():
    path = '/mnt/ipeajus-temp/lista_acervo/'
    itens_pasta = os.listdir(path)
    count_txts = 0
    count_pdfs = 0

    for diario in itens_pasta:
        data = pd.read_csv(path+diario, header=None, warn_bad_lines=False, encoding='latin')

        for caderno in data[0]:
            if caderno.split('.')[-1] == 'txt':
                count_txts += 1
            elif caderno.split('.')[-1] == 'pdf':
                count_pdfs += 1

    print(f"Quantidade de pdf's existentes no acervo do IPEAJUS: {count_pdfs} diarios")
    print(f"Quantidade de txt's existentes no acervo do IPEAJUS: {count_txts} diarios")


def lista_quantidade_ramdomica_de_blocos():

    pastas_busca = glob.glob('/mnt/dmlocal/dados/*/txt')
    pastas_busca = [list(Path(busca).glob('**/*')) for busca in pastas_busca]
    regex = re.compile('(\d{7}\-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4})|(\d{6,7}\-?\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})|(\d{3}\.\d{2}\.\d{4}\.\d{6}(\-\d\/\d{6}\-\d{3})?)|(\d{3}\.\d{2,4}\.\d{6}\-?\d?)|(\\b\d{15}\\b)')
    # lista_de_arquivos = []
    lista_qtd_npus = []
    arq = open('../Quantidade_de_blocos_por_tribunal.csv', encoding='utf-8', mode='a+')
    arq.write('Nome Diário;Resultado')

    for busca in pastas_busca:
        lista_de_arquivos = [arquivo for arquivo in busca if arquivo.is_file()]
        if len(lista_de_arquivos) == 0:
            continue
        for arquivo in range(0, 10):
            try:
                diario = lista_de_arquivos[random.randint(1, len(lista_de_arquivos))]
            except Exception as e:
                print()
            file = open(diario)
            linhas = ' '.join(file.readlines())
            matches = [npu.group(0) for npu in regex.finditer(linhas)]
            lista_qtd_npus.append(len(matches))

        nome_diario = diario.name.split('_')[0]
        media = sum(lista_qtd_npus)/10
        resultado = round(media * len(lista_de_arquivos), 2)
        print(f'{nome_diario};{resultado}')
        arq.write(f'{nome_diario};{resultado}\n')
        arq.flush()




# for ano in range(1999,2022):
#     caminho = f'/mnt/dmlocal/dados/SP/DJSP/txt/{ano}'
caminho = '/mnt/dmlocal/dados/SP/DJSP/txt/2021/04'
lista_nome_tamanho_arquivos_na_pasta(caminho)


#lista_quantidade_ramdomica_de_blocos()
#verifica_arquivos_com_paginas_sem_merge(caminho=caminho, pdf_ou_txt='pdf')