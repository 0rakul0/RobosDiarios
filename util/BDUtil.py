def troca_nome_schema_arquivo(nome_arquivo,nome_arquivo_saida,antigo_schema,novo_schema):
    with open(nome_arquivo,"r") as arq:
        linha = " "
        output = open(nome_arquivo_saida,"w")
        while linha:
            try:
                linha = arq.readline()
                linha = linha.replace(antigo_schema,novo_schema)
                output.write(linha)
                print(linha)
            except:
                pass
        output.close()



if __name__ == '__main__':
    caminho = "C:\\Users\\b120558711\\indices\\"
    troca_nome_schema_arquivo(caminho+"indices.sql",caminho+"indice_output.sql","producao_indices","teste_indices")


