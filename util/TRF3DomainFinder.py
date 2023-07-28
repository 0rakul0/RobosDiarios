import requests
import json
from bs4 import BeautifulSoup as bs
tribunais_grau = {'JFSP': 1,
                     'JFMS': 1,
                     'JEFSP': 1,
                     'JEFMS': 1,
                     'PJE1': 1,
                     'TRF3R':2,
                     'PJE2': 2
                         }
def TRF3DomainFinder(numero_processo, proxies={'http': 'http://cache.ipea.gov.br:3128', 'https': 'https://cache.ipea.gov.br:3128'}):
    """
    Busca em quais domínios podemos encontrar o processo
    Args:
    :param numero_processo: (str) Número de processo extraído do banco de dados

    Returns:
    :return: json_data: (dict) Dicionário contendo os dominínos os quais o processo pode ser encontrado
    """
    params = {'numeroProcesso' : numero_processo}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
    response = requests.get(r'http://web.trf3.jus.br/sistemasweb/LocalizarProcesso', params=params, headers=headers,proxies=proxies)
    if response.status_code == 200:
        json_data = json.loads(response.text)
        return json_data
    return None

def TRF3Instancias(grau, numero_processo):
    """
    Identifica em quais instancias do grau indicado se encontra o processo
    Args:
    :param grau: (int) Grau do tribunal (i.e: Primeiro Grau ou Segundo Grau)

    :param numero_processo: (str) Número de processo extraído do banco de dados

    Returns:
    :return: tribunais: (list) Lista com os tribunais onde o processo se encontra no grau indicado.
    """
    instanciasTRF3 = {1: ['JFSP', 'JFMS', 'JEFSP', 'JEFMS', 'PJE1'], 2: ['TRF3R', 'PJE2']}
    json_data = TRF3DomainFinder(numero_processo)
    if json_data:
        instancias_do_processo = [json_data[instancia]['Id'] for instancia in range(len(json_data))]
        tribunais = [x for x in instancias_do_processo if x in instanciasTRF3[grau]]
        return tribunais
    return None

"""
    Identifica o tribunal e o grau do processo indicado
    Args:

    :param numero_processo: (str) Número de processo(ou npu) extraído do banco de dados

    Returns:
    :return: dict_tribunais_graus: (dict) Dicionário com {Tribunal:Grau}.
    """
def TRF3DictTRFGrau(numero_processo):
    dict_tribunais_graus = {}
    json_data = TRF3DomainFinder(numero_processo)
    if json_data:
        for data in json_data:
            dict_tribunais_graus[data['Id']]= tribunais_grau[data['Id']]


    return dict_tribunais_graus

def TRF3Graus(numero_processo):
    """
    Identifica o grau do processo indicado
    Args:

    :param numero_processo: (str) Número de processo(ou npu) extraído do banco de dados

    Returns:
    :return: GRAU: (int) Grau do processo.
    """
    instanciasTRF3 = {1: ['JFSP', 'JFMS', 'JEFSP', 'JEFMS', 'PJE1'], 2: ['TRF3R', 'PJE2']}
    json_data = TRF3DomainFinder(numero_processo)
    if json_data:
        instancias_do_processo = [json_data[instancia]['Id'] for instancia in range(len(json_data))]
        lista_graus = []
        if any(instancia_do_processo in instanciasTRF3[1] for instancia_do_processo in instancias_do_processo ):
            lista_graus.append(1)
        if any(instancia_do_processo in instanciasTRF3[2] for instancia_do_processo in instancias_do_processo ):
            lista_graus.append(2)
        return lista_graus
    return None