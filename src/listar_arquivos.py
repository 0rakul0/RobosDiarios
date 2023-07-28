import os
from datetime import date

# Bibliotecas Uteis
from util.gerar_csv import gerar_csv
from util import manipular_arquivos

def obter_ano_pasta(pasta):
    try:
        return int(pasta)
    except ValueError:
        return -1

def obter_pastas_ano(caminho_tipo_arquivo):
    """
    Esta função recebe um caminho de diretório como parâmetro e retorna uma lista com todas as pastas presentes dentro dele.

    :param caminho_tipo_arquivo: O caminho do diretório a ser explorado.
    :return: Uma lista contendo os nomes das pastas presentes no diretório especificado, ordenadas de forma decrescente.
    """
    pastas_ano = os.listdir(caminho_tipo_arquivo)
    pastas_ano.sort(reverse=True)
    return pastas_ano

def obter_ultimo_ano(caminho_tipo_arquivo):
    pasta_ultimo_ano = obter_pastas_ano(caminho_tipo_arquivo)
    item = [i for i in pasta_ultimo_ano if i.isdigit()]
    try:
        pasta_ultimo_ano = item[0]
    except:
        pasta_ultimo_ano = "Verificar Ano"

    return pasta_ultimo_ano

def obter_pasta_recente(pastas_ano, caminho_tipo_arquivo, ano_atual):
    """
    Esta função recebe uma lista de nomes de pastas referentes a diferentes anos (exemplo: "2023", "2010", "1960")
    dentro da pasta de um determinado tipo de arquivo (como "pdf" ou "txt"). O objetivo é encontrar a pasta do ano
    mais recente, que seja igual ou anterior ao ano atual fornecido.

    :param pastas_ano: Lista de nomes de pastas referentes aos anos presentes no diretório do tipo de arquivo.
    :param caminho_tipo_arquivo: O caminho da pasta do tipo de arquivo, incluindo a pasta do ano específico.
    :param ano_atual: O ano atual que será usado para encontrar a pasta mais recente.
    :return: O caminho para a pasta do ano mais recente, ou None caso nenhuma pasta seja encontrada para o ano atual.
    """
    for pasta in pastas_ano:
        caminho_pasta = os.path.join(caminho_tipo_arquivo, pasta)
        if os.path.isdir(caminho_pasta):
            if pasta.isdigit() and int(pasta) <= ano_atual:
                return caminho_pasta
    return None

def obter_caminhos_meses(pasta_recente):
    """
    Obtém os caminhos completos para todas as pastas de meses dentro da pasta fornecida.

    :param pasta_recente: O caminho para a pasta do ano mais recente, contendo pastas para os meses.
    :return: Retorna uma lista de caminhos completos para todas as pastas de meses encontradas.
             Caso nenhuma pasta de mês seja encontrada, a lista será vazia.

    Exemplo de uso:
    obter_caminhos_meses('/mnt/dmlocal/dados/SP/DJSP/pdf/2023')
    ['/mnt/dmlocal/dados/SP/DJSP/pdf/2023/01', '/mnt/dmlocal/dados/SP/DJSP/pdf/2023/02', ...]
    """
    caminhos_meses = []
    for mes in os.listdir(pasta_recente):
        caminho_mes = os.path.join(pasta_recente, mes)
        if os.path.isdir(caminho_mes):
            caminhos_meses.append(caminho_mes)
    return caminhos_meses  # Retornar a lista de caminhos de meses ao invés de imprimir

def percorrer_pastas(diretorio_raiz, tipo_arquivos_pastas=None):
    """
    Percorre as pastas e arquivos em busca de informações sobre o estado, órgão, ano mais recente e arquivos encontrados.
    :param diretorio_raiz: O caminho do diretório raiz a ser percorrido inicialmente.
    :param tipo_arquivos_pastas: Lista opcional de siglas para filtrar pastas de tipos específicos.
                                 Se não fornecida, todas as pastas serão consideradas.
    :return: Retorna uma lista de dicionários com as informações coletadas. Cada dicionário contém:
             - 'Estado': O caminho para a pasta do estado.
             - 'Orgao': O caminho para a pasta do órgão.
             - 'Tipo de arquivo': O caminho para a pasta do tipo de arquivo.
             - 'Pasta do ano mais recente': O caminho para a pasta do ano mais recente encontrado dentro do tipo de arquivo.
             - 'Arquivos': Uma lista com os nomes dos arquivos encontrados na pasta do ano mais recente.
    A função percorrer_pastas tem a funcionalidade de percorrer pastas e arquivos, verificando por estado e orgaos a existencia
    de ano e mes correspondente ao estado e orgao especificado.
    '/mnt/dmlocal/dados/SP/DJSP/pdf/2023/07/*.pdf'
    :param diretorio_raiz: O diretorio_raiz recebe o caminho a ser percorrido inicialmente.
    :return: Retorna um dicionario com as informações coletadas.
    """
    siglas_estados = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR",
                          "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
    # siglas_estados = ["MA"]

    dados = []
    nomes_arquivos_gerados = []

    for estado in os.listdir(diretorio_raiz):
        caminho_estado = os.path.join(diretorio_raiz, estado)
        if os.path.isdir(caminho_estado) and estado in siglas_estados:

            for orgao in os.listdir(caminho_estado):
                caminho_orgao = os.path.join(caminho_estado, orgao)
                if os.path.isdir(caminho_orgao):

                    for tipo_arquivo in os.listdir(caminho_orgao):
                        siglas_pastas = tipo_arquivos_pastas

                        caminho_tipo_arquivo = os.path.join(caminho_orgao, tipo_arquivo)
                        if os.path.isdir(caminho_tipo_arquivo) and tipo_arquivo in siglas_pastas:

                            ano_atual = date.today().year
                            # print(ano_atual)
                            pastas_ano = obter_pastas_ano(caminho_tipo_arquivo)

                            pasta_ultimo_ano = obter_ultimo_ano(caminho_tipo_arquivo)

                            pasta_recente = obter_pasta_recente(pastas_ano, caminho_tipo_arquivo, ano_atual)

                            caminhos_meses = obter_caminhos_meses(pasta_recente) if pasta_recente else []

                            # Verificar o mês mais recente
                            mes_mais_recente = None
                            for caminho_mes in caminhos_meses:
                                mes_str = caminho_mes.split("/")[-1]
                                mes = int(mes_str)
                                if not mes_mais_recente or mes > mes_mais_recente:
                                    mes_mais_recente = mes

                            for arquivo in caminhos_meses:
                                lista_arquivos = manipular_arquivos.listar_arquivos(arquivo)
                                nomes_arquivos_gerados.extend(lista_arquivos)


                            dados.append({
                                "Estado": caminho_estado,
                                "Orgao": caminho_orgao,
                                "Tipo_de_arquivo": caminho_tipo_arquivo,
                                "Ano": pasta_ultimo_ano,
                                "Mes": mes_mais_recente if mes_mais_recente else "Nenhum mês encontrado",
                            })

    return dados

def imprimir_dados(dados):
    """
    Imprime os dados coletados pela função 'percorrer_pastas' de forma organizada e legível.

    :param dados: Uma lista de dicionários contendo informações sobre estados, órgãos, tipos de arquivo,
                  pastas do ano mais recente e caminhos para as pastas dos meses.
    :return: Nenhum valor é retornado explicitamente.

    """
    for dado in dados:
        print("Estado:", dado['Estado'])
        print("Órgão:", dado['Orgao'])
        print("Tipo de arquivo:", dado['Tipo de arquivo'])
        print("Pasta do ano mais recente:", dado['Pasta do ano mais recente'])
        print("Caminho dos meses.")
        for caminho_mes in dado['Caminho dos meses']:
            print("  -", caminho_mes)

def run():
    """
    Executa o processo principal do programa.

    Esta função é responsável por executar o processo principal do programa, que inclui a coleta de informações sobre
    os estados, órgãos e tipos de arquivo em um diretório específico. Ela chama a função 'percorrer_pasta' para realizar
    a coleta e, em seguida, gera um arquivo CSV com os dados coletados usando a função 'gerar_csv'.

    :param None
    :return: Nenhum valor é retornado explicitamente.
    """
    tipo_arquivos_pastas = ["txt", "pdf"]

    # pasta alvo
    caminho = '/mnt/dmlocal/dados/'
    dados = percorrer_pastas(caminho, tipo_arquivos_pastas)
    # dados_atualizados = [dado for dado in dados if dado["Ano"].endswith("/2023")]

    nome_arquivo = "../csv/dadosPastas.csv"

    # Lista com as colunas desejadas
    colunas_desejadas = ["Estado", "Ano", "Mes", "Tipo_de_arquivo" ]

    gerar_csv(dados, nome_arquivo, colunas=colunas_desejadas)


if __name__ == "__main__":
    run()
