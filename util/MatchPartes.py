import pandas as pd
import names
import os.path
import sys

from pdjus.modelo.ParteDistribuicao import ParteDistribuicaoRais
from pdjus.service.ParteDistribuicaoService import ParteDistribuicaoService
from pdjus.service.ParteService import ParteService


class Matcher:

    def match(self, parte, campo_parte, rais, campo_rais):
        return parte[campo_parte] == rais[campo_rais]

    def le_arquivo_para_dataframe(self, filename, chunksize=10 ** 4, adiciona_colunas=False):
        # TODO: setar o dtype é importante!!!!
        for chunk in pd.read_csv(filename, sep='\t', encoding='latin-1',chunksize=chunksize, dtype='str'): # dtype aceita um dicionário contendo nomes de colunas : tipos
            chunk = chunk.fillna('texto indisponível')
            yield chunk

    def itera_chunk(self, chunk):

        for index, c in chunk.iterrows():
            yield index, c

# @profile
def run(teste,arquivo_1,parametro_1,arquivo_2,parametro_2):
    finish = False
    count_matches = 0
    m = Matcher()
    with open("resultados_matches.csv","w") as resultado:
        try:
            if teste:
                if not os.path.isfile(arquivo_1):
                    df = pd.DataFrame(columns=[parametro_1])

                    for i in range(0, 10000):
                        nome = names.get_full_name()
                        df.loc[i] = nome

                    df = df.drop_duplicates(subset=[parametro_1])
                    df.sort_values(by=[parametro_1]).to_csv(arquivo_1, sep='\t', encoding='utf-8',
                                                       mode='w', header=True, index=False)
                chunk_parte_generator = m.le_arquivo_para_dataframe(filename=arquivo_1)

                if not os.path.isfile(arquivo_2):
                    df = pd.DataFrame(columns=[parametro_2])

                    for i in range(0, 100000):
                        nome = names.get_full_name()
                        df.loc[i] = nome

                    df = df.drop_duplicates(subset=[parametro_2])
                    df.sort_values(by=parametro_2).to_csv(arquivo_2, sep='\t', encoding='utf-8',
                                                             mode='w', header=True, index=False)
                chunk_rais_generator = m.le_arquivo_para_dataframe(filename=arquivo_2)
            else:
                chunk_parte_generator = m.le_arquivo_para_dataframe(filename=arquivo_1)
                chunk_rais_generator = m.le_arquivo_para_dataframe(filename=arquivo_2)

            # inicializacao dos chunks, tirando duplicatas e nulos
            chunk_parte = next(chunk_parte_generator).drop_duplicates(subset=[parametro_1])
            chunk_parte = chunk_parte[chunk_parte[parametro_1] != 'texto indisponível']

            chunk_rais = next(chunk_rais_generator).drop_duplicates(subset=[parametro_2])
            chunk_rais = chunk_rais[chunk_rais[parametro_2] != 'texto indisponível']

            curr_parte_generator = m.itera_chunk(chunk_parte)
            curr_parte = next(curr_parte_generator)

            curr_rais_generator = m.itera_chunk(chunk_rais)
            curr_rais = next(curr_rais_generator)

        except Exception as e:
            print(e)
            finish = True

        chunk_parte_count = 0
        chunk_rais_count = 0
        write_parte = True
        write_rais = True

        while not finish:

            while curr_parte[1][parametro_1] < curr_rais[1][parametro_2]:
                try:
                    curr_parte = next(curr_parte_generator)
                    if write_parte or write_rais:
                        print('curr partes: ', curr_parte[1][parametro_1], '----------------' , curr_rais[1][parametro_2])
                        write_parte = False
                        write_rais = False

                except StopIteration as ex:
                    # print(ex)
                    try:
                        chunk_parte = next(chunk_parte_generator).drop_duplicates(subset=[parametro_1])
                        chunk_parte = chunk_parte[chunk_parte[parametro_1] != 'texto indisponível']
                        chunk_parte_count += 1
                        print(chunk_parte_count, chunk_rais_count)
                        write_parte = True
                        curr_parte_generator = m.itera_chunk(chunk_parte)
                    except StopIteration as e:
                        # print(e)
                        finish = True
                        break

            while curr_rais[1][parametro_2] < curr_parte[1][parametro_1]:
                try:
                    curr_rais = next(curr_rais_generator)
                    if write_parte or write_rais:
                        print('curr partes: ', curr_parte[1][parametro_1], '----------------', curr_rais[1][parametro_2])
                        write_parte = False
                        write_rais = False

                except StopIteration as ex:
                    # print(ex)
                    try:
                        chunk_rais = next(chunk_rais_generator).drop_duplicates(subset=[parametro_2])
                        chunk_rais = chunk_rais[chunk_rais[parametro_2] != 'texto indisponível']
                        chunk_rais_count += 1
                        curr_rais_generator = m.itera_chunk(chunk_rais)
                        print(chunk_parte_count, chunk_rais_count)
                        write_rais = True

                    except StopIteration as e:
                        # print(e)
                        finish = True
                        break


            if m.match(curr_rais[1], parametro_2, curr_parte[1], parametro_1):
                count_matches += 1
                print('MATCH:', curr_rais[1][parametro_2], curr_parte[1][parametro_1])
                resultado.write('"'+curr_rais[1]["id"]+'","'+curr_rais[1][parametro_2]+'","'+curr_parte[1]["id"]+'","'+curr_parte[1][parametro_1]+'"\n')

                try:
                    # apenas 1 match por parte OU!!!
                    curr_parte = next(curr_parte_generator)

                    # mais de 1 match por parte
                    # curr_rais = next(curr_rais_generator)
                except StopIteration as ex:
                    # print(ex)
                    try:
                        chunk_parte = next(chunk_parte_generator).drop_duplicates(subset=[parametro_1])
                        chunk_parte = chunk_parte[chunk_parte[parametro_1] != 'texto indisponível']
                        chunk_parte_count += 1
                        curr_parte_generator = m.itera_chunk(chunk_parte)
                        #print(chunk_parte_count, chunk_rais_count)
                        write_parte = True

                    except StopIteration as e:
                        # print(e)
                        finish = True
                        break



    print(count_matches)

def importa_resultado():
    with open("resultados_matches.csv", "r") as resultado:
        parte_service = ParteService()
        parte_distribuicao_service = ParteDistribuicaoService()
        i=0
        for linha in resultado:
            id_rais = int(linha.split("\",\"")[0].strip("\""))
            id_parte_distribuicao = int(linha.split("\",\"")[2].strip("\""))
            nome_parte_distribuicao = linha.split("\",\"")[3].strip("\"")

            #parte = parte_distribuicao_service.dao.get_por_nome(nome_parte_distribuicao)
            print(nome_parte_distribuicao)
            #if parte:
            #print(i)
            parte_distribuicao_rais = ParteDistribuicaoRais()
            parte_distribuicao_rais.parte_distribuicao_id = id_parte_distribuicao
            parte_distribuicao_rais.rais_id = id_rais

            parte_distribuicao_rais.save()

            i+=1
            if i%100 == 0:
                print("Salvos "+ str(i))
                parte_service.dao.commit()


def slice_input(teste,arquivo_1, slice_size):
    m = Matcher()
    try:
        chunk_parte_generator = m.le_arquivo_para_dataframe(filename=arquivo_1, chunksize=slice_size)

        if not os.path.isfile("1_" + arquivo_1):

            slice_number = 0
            for chunk in chunk_parte_generator:
                slice_number += 1
                chunk.to_csv(str(slice_number) + "_" + arquivo_1, sep='\t', encoding='utf-8', mode='a', header=True)

    except Exception as e:
        print(e)
        sys.exit(0)


if __name__ == '__main__':

    # Consulta para gerar entrada ordenada:
    # select * from producao.parte order by nome collate "C"
    # collate "C" faz com que o postgresql ordene utilizando o critério do valor em bytes da string, que é o mesmo usado pelo python.

    importa_resultado()

    # is_teste = False
    # dt_inicio = datetime.now()
    # #
    # run(is_teste,"C:\\Users\\b120558711\\parte_distribuicao.csv","parte","C:\\Users\\b120558711\\rais.csv","razao_social")
    # #
    # print('inicio', dt_inicio)
    # print('fim', datetime.now())