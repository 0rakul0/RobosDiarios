import os
from pathlib import Path

def renomeia(cad_dj=None,novo_nome_dj=None, path=None):

    lista_arquivos_txt = [str(i) for i in Path(path+'txt').rglob('*.txt')] # EX: '/mnt/dmlocal/dados/STJ/'
    lista_arquivos_pdf = [str(i) for i in Path(path+'pdf').rglob('*.pdf')]

    for txt in lista_arquivos_txt:
        if cad_dj in os.path.basename(txt): # EX: 'DJSTJ'
            new_name = os.path.basename(txt).replace(cad_dj,novo_nome_dj)
            print('Renomeando o arquivo {} para {}'.format(os.path.basename(txt),new_name))
            os.renames(txt,os.path.dirname(txt)+'/'+new_name)

    for pdf in lista_arquivos_pdf:
        if cad_dj in os.path.basename(pdf):
            new_name = os.path.basename(pdf).replace(cad_dj,novo_nome_dj)
            print('Renomeando o arquivo {} para {}'.format(os.path.basename(pdf), new_name))
            os.renames(pdf,os.path.dirname(pdf)+'/'+new_name)