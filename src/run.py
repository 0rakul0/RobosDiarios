"""
Inicio da pipeline do devops para os diarios do dm-new.
"""
import pandas as pd
import datetime
from src.listar_arquivos import run as run_1
from robosdiarios import (RoboDiarioES, RoboDiarioAC, RoboDiarioAL, RoboDiarioAM,
                          RoboDiarioCE, RoboDiarioDF, RoboDiarioMS, RoboDiarioPB, RoboDiarioPI, RoboDiarioPR,
                          RoboDiarioJUCESP, RoboDiarioRJ, RoboDiarioRN, RoboDiarioSP, RoboDiarioTO)

# primeira etapa start do csv
run_1()
# segunda etapa ler arquivo csv
df = pd.read_csv('../csv/dadosPastas.csv', sep=',')

try:
    ultima_data = open('../csv/bateu.txt', 'r')
    last_date = ultima_data.read()
    ultima_data.close()
    last_date = last_date.split('-')
    ano = int(last_date[0])
    mes = int(last_date[1])
    dia = int(last_date[2])

    ultima_data = datetime.date(ano, mes, dia)
    data = datetime.date.today()
except:
    ultima_data = None
    data = str(datetime.date.today())


if ultima_data:
    if ultima_data <= data:
        print("inicia atualização do diario")

        for item in df.itertuples():
            estado = item.Estado
            ano = item.Ano
            mes = item.Mes
            tipo = item.Tipo_de_arquivo
            estado = str(estado).split('/')[-1]
            tipo = str(tipo).split('/')[-1]

            if estado == 'PE':
                pass

            # if estado == 'AC':
            #     print(f"### estado {estado} inicio ###")
            #     print(f" estado {estado} no mes {mes} do ano de {ano} ")
            #     print(estado, ano, mes, tipo)
            #     robo = RoboDiarioAC.RoboDiarioAC()
            #     robo.download_atualizacao_diaria_2023()

            # elif estado == 'AL' and tipo == 'pdf':
            #     print(f"### estado {estado} inicio ###")
            #     print(f" estado {estado} no mes {mes} do ano de {ano} ")
            #     print(estado, ano, mes, tipo)
            #     robo = RoboDiarioAL.RoboDiarioAL()
            #     robo.download_atualizacao_diaria()

            # elif estado == 'AM':
            #     print(f"### estado {estado} inicio ###")
            #     print(f" estado {estado} no mes {mes} do ano de {ano} ")
            #     print(estado, ano, mes, tipo)
            #     robo = RoboDiarioAM.RoboDiarioAM()
            #     robo.download_atualizacao_diaria_2023()

            # elif estado == 'ES':
            #     print(f"### estado {estado} inicio ###")
            #     print(f" estado {estado} no mes {mes} do ano de {ano} ")
            #     print(estado, ano, mes, tipo)
            #     robo = RoboDiarioES.RoboDiarioES()
            #     robo.download_atualizacao_diaria_tipo(f'*.{tipo}')

            # elif estado == 'CE':
            #     print(f"### estado {estado} inicio ###")
            #     print(f" estado {estado} no mes {mes} do ano de {ano} ")
            #     print(estado, ano, mes, tipo)
            #     robo= RoboDiarioCE.RoboDiarioCE()
            #     robo.download_atualizacao_diaria()

            # elif estado == 'DF':
            #     print(f"### estado {estado} inicio ###")
            #     print(f" estado {estado} no mes {mes} do ano de {ano} ")
            #     print(estado, ano, mes, tipo)
            #     robo = RoboDiarioDF.RoboDiarioDF()
            #     robo.download_atualizacao_diaria()

            # elif estado == 'MS':
            #     print(f"### estado {estado} inicio ###")
            #     print(f" estado {estado} no mes {mes} do ano de {ano} ")
            #     print(estado, ano, mes, tipo)
            #     robo = RoboDiarioMS.RoboDiarioMS()
            #     robo.download_atualizacao_diaria()

            # elif estado == 'PB':
            #     print(f"### estado {estado} inicio ###")
            #     print(f" estado {estado} no mes {mes} do ano de {ano} ")
            #     print(estado, ano, mes, tipo)
            #     robo = RoboDiarioPB.RoboDiarioPB()
            #     robo.download_atualizacao_diaria()

            # elif estado == 'PI':
            #     print(f"### estado {estado} inicio ###")
            #     print(f" estado {estado} no mes {mes} do ano de {ano} ")
            #     print(estado, ano, mes, tipo)
            #     robo = RoboDiarioPI.RoboDiarioPI()
            #     robo.download_atualizacao_diaria()

            # elif estado == 'PR':
            #     print(f"### estado {estado} inicio ###")
            #     print(f" estado {estado} no mes {mes} do ano de {ano} ")
            #     print(estado, ano, mes, tipo)
            #     robo = RoboDiarioPR.RoboDiarioPR()
            #     robo.download_atualizacao_diaria()

            # elif estado == 'RJ':
            #     print(f"### estado {estado} inicio ###")
            #     print(f" estado {estado} no mes {mes} do ano de {ano} ")
            #     print(estado, ano, mes, tipo)
            #     robo = RoboDiarioRJ.RoboDiarioRJ()
            #     robo.download_atualizacao_diaria()

            # elif estado == 'RN':
            #     print(f"### estado {estado} inicio ###")
            #     print(f" estado {estado} no mes {mes} do ano de {ano} ")
            #     print(estado, ano, mes, tipo)
            #     robo = RoboDiarioRN.RoboDiarioRN()
            #     robo.download_atualizacao_diaria()

            elif estado == 'SP':
                print(f"### estado {estado} inicio ###")
                print(f" estado {estado} no mes {mes} do ano de {ano} ")
                print(estado, ano, mes, tipo)
                robo = RoboDiarioSP.RoboDiarioSP()
                robo.download_atualizacao_diaria()

            # elif estado == 'TO':
            #     print(f"### estado {estado} inicio ###")
            #     print(f" estado {estado} no mes {mes} do ano de {ano} ")
            #     print(estado, ano, mes, tipo)
            #     robo = RoboDiarioTO.RoboDiarioTO()
            #     robo.download_atualizacao_diaria()


    else:
        print("os diarios estão atualizado, na data", ultima_data)
else:
    print("sem ultima data, verificar arquivo")