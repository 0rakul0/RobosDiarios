import pandas as pd
import datetime

def gerar_csv(dados, nome_arquivo, colunas=None):

    # Criando um DataFrame com os dados filtrados
    df = pd.DataFrame(dados)

    # Verificar se a ordem das colunas foi especificada.
    if colunas is not None:
        df = df[colunas]

    # Salvar o DataFrame como arquivo CSV
    df.to_csv(nome_arquivo, index=False)

    with open('../csv/bateu.txt', 'w') as arq:
        arq.write(str(datetime.date.today()))
        arq.close()

    print("Arquivo CSV gerado com sucesso!")
