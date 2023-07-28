import os
from datetime import datetime


def listar_arquivos(caminho_pasta):
    try:
        conteudo_pasta = os.listdir(caminho_pasta)
        arquivos = [arquivo for arquivo in conteudo_pasta if os.path.isfile(os.path.join(caminho_pasta, arquivo))]
        # print(arquivos)
        return arquivos
    except OSError as e:
        print(f'Erro ao listar os arquivos: {e}')
        return []


def criar_pastas_anos(caminho_base):
    # Verifique se o caminho base é válido
    if not os.path.exists(caminho_base):
        # print("Caminho base inválido.")
        return

    # Loop de 1960 a 2023 (use 2024 se quiser incluir o ano de 2023)
    for ano in range(1960, 2024):
        # Crie o nome da pasta para cada ano
        nome_pasta = str(ano)
        caminho_pasta = os.path.join(caminho_base, nome_pasta)

        # Verifique se a pasta já existe antes de criar
        if not os.path.exists(caminho_pasta):
            os.mkdir(caminho_pasta)
            # print(f"Pasta '{nome_pasta}' criada em '{caminho_base}'.")
        else:
            # print(f"Pasta '{nome_pasta}' já existe em '{caminho_base}'.")
            pass


def criar_pastas_meses(caminho_base):
    # Verifique se o caminho base é valido
    if not os.path.exists(caminho_base):
        # print("Caminho base inválido")
        return

    # Obter a data atual
    data_atual = datetime.now()

    # Loop de 1960 a 2023 (Estou usando até 2024 para incluir 2023)
    for ano in range(1960, 2024):
        # Crie o nome da pasta para cada ano
        nome_pasta_ano = str(ano)
        caminho_pasta_ano = os.path.join(caminho_base, nome_pasta_ano)

        # Verifique se a pasta do ano já existe
        if not os.path.exists(caminho_pasta_ano):
            # print(f"Pasta do ano '{nome_pasta_ano}' não existe em '{caminho_base}'")
            continue

        # Loop de 1 a 12 (meses)
        for mes in range(1, 13):
            # Crie o nome da pasta para cada mês com 2 dígitos (ex: '01, '02', ..., '12')
            nome_pasta_mes = f"{mes:02d}"
            caminho_pasta_mes = os.path.join(caminho_pasta_ano, nome_pasta_mes)
            # Verifique se a pasta do mês ja existe ou se a data atual é anterior ao mês
            if os.path.exists(caminho_pasta_mes) or (ano == data_atual.year and mes > data_atual.month):
                teste = teste
                # print(f"Pasta do mês '{nome_pasta_mes}' já existe ou não é hora de criar em '{caminho_pasta_ano}.'")
            else:
                os.mkdir(caminho_pasta_mes)
                # print(f"Pasta do mês  '{nome_pasta_mes}' criada em '{caminho_pasta_ano}'.")
