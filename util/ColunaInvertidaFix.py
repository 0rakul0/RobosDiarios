import os
import re
from collections import OrderedDict
from bs4 import BeautifulSoup, NavigableString
import codecs
from util.StringUtil import remove_acentos, remove_varios_espacos, remove_caracteres_especiais


# class Coluna_invertida_fix():
def limpa_coluna_insere_em_dic(coluna, colunas_maiores, ajuste_posicao,ajuste_opcional =False):


    #match = regex.search(remove_varios_espacos(remove_acentos(coluna.text.upper())))

    #if len(coluna.text) > 600 or match:
    coluna_limpa = remove_acentos(coluna.text.replace('NIRE',' NIRE'))
    coluna_limpa = remove_varios_espacos(coluna_limpa)
    coluna_limpa = coluna_limpa + ' '

    if ajuste_opcional:
        posicaot = list(colunas_maiores.keys())[-1]
        posicaon = int(posicaot)
    else:
        posicaot = re.search('left.*px', coluna.attrs['style']).group(0)
        posicaon = re.search('\d+', posicaot).group(0)


    if float(posicaon) in colunas_maiores.keys():
        colunas_maiores[float(posicaon) + ajuste_posicao] = coluna_limpa
    else:
        colunas_maiores[float(posicaon)] = coluna_limpa
    colunas_maiores = OrderedDict(sorted(colunas_maiores.items()))
    ajuste_posicao = ajuste_posicao + 0.00000000001
    return colunas_maiores,ajuste_posicao

def checa_coluna_invertida(filepath,diario,ano,mes):

    diario = '-html.'.join(diario.split('.'))
    filepath = '-html.'.join(filepath.split('.'))
    caminho_dir_html_ano = re.sub('html.*', 'txt/{ano}'.format(ano=ano), filepath)
    caminho_dir_html_ano_mes = re.sub('html.*', 'txt/{ano}/{mes}'.format(ano=ano, mes=mes), filepath)
    if not os.path.exists(caminho_dir_html_ano):
        os.mkdir(caminho_dir_html_ano)
    if not os.path.exists(caminho_dir_html_ano_mes):
        os.mkdir(caminho_dir_html_ano_mes)


    with codecs.open(filepath, 'r',encoding="utf-8") as diariohtml:
        soup = BeautifulSoup(diariohtml.read(),"html5lib")
        paginas = soup.find_all('div',{"id" : re.compile('page.*')})
        regex_titulo = re.compile("(A\s*L\s*T\s*E\s*R\s*A\s*C\s*O\s*E\s*S|C\s*O\s*N\s*S\s*T\s*I\s*T\s*U\s*I\s*C\s*O\s*E\s*S)\s*(S\s*O\s*C\s*I\s*E\s*D\s*A\s*D\s*E\s*S\s*(P\s*O\s*R\s*A\s*C\s*O\s*E\s*S|L\s*I\s*M\s*I\s*T\s*A\s*D\s*A\s*S?)|E\s*I\s*R\s*E\s*L\s*I\s*|C\s*O\s*M\s*A\s*N\s*D\s*I\s*T\s*A\s*S\s*S\s*I\s*M\s*P\s*L\s*E\s*S|E\s*M\s*P\s*R\s*E\s*S\s*A\s*R\s*I\s*O\s*S|E\s*M\s*P\s*R\s*E\s*S\s*A\s*S\s*E\s*S\s*T\s*R\s*A\s*N\s*G\s*E\s*I\s*R\s*A\s*S|C\s*O\s*N\s*S\s*O\s*R\s*C\s*I\s*O\s*S|C\s*O\s*O\s*P\s*E\s*R\s*A\s*T\s*I\s*V\s*A\s*S|F\s*I\s*R\s*M\s*A\s*S\s*(I\s*N\s*D\s*I\s*V\s*I\s*D\s*U\s*A\s*I\s*S|E\s*I\s*R\s*E\s*L\s*I|L\s*I\s*M\s*I\s*T\s*A\s*D\s*A\s*S))")
        regex_nire = re.compile("(NIRE\s*-\s)")
        regex = re.compile("((A\s*L\s*T\s*E\s*R\s*A\s*C\s*O\s*E\s*S|C\s*O\s*N\s*S\s*T\s*I\s*T\s*U\s*I\s*C\s*O\s*E\s*S)\s*(S\s*O\s*C\s*I\s*E\s*D\s*A\s*D\s*E\s*S\s*(P\s*O\s*R\s*A\s*C\s*O\s*E\s*S|L\s*I\s*M\s*I\s*T\s*A\s*D\s*A\s*S?)|E\s*I\s*R\s*E\s*L\s*I\s*|C\s*O\s*M\s*A\s*N\s*D\s*I\s*T\s*A\s*S\s*S\s*I\s*M\s*P\s*L\s*E\s*S|E\s*M\s*P\s*R\s*E\s*S\s*A\s*R\s*I\s*O\s*S|E\s*M\s*P\s*R\s*E\s*S\s*A\s*S\s*E\s*S\s*T\s*R\s*A\s*N\s*G\s*E\s*I\s*R\s*A\s*S|C\s*O\s*N\s*S\s*O\s*R\s*C\s*I\s*O\s*S|C\s*O\s*O\s*P\s*E\s*R\s*A\s*T\s*I\s*V\s*A\s*S|F\s*I\s*R\s*M\s*A\s*S\s*(I\s*N\s*D\s*I\s*V\s*I\s*D\s*U\s*A\s*I\s*S|E\s*I\s*R\s*E\s*L\s*I|L\s*I\s*M\s*I\s*T\s*A\s*D\s*A\s*S))|(NIRE\s*-\s))")
        #count = 0
        for pagina in paginas:
            colunas = pagina.children
            quantiP = len(pagina.find_all('p'))
            #posicao_colunas = []
            colunas_maiores = {}
            #count = count + 1
            #if count >=135:
            ajuste_posicao= 0.00000000001
            match_teste_quantp = None
            i = 0
            listcolunas = list(colunas)
            if quantiP > 30:
                while i < len(listcolunas) and not match_teste_quantp:
                    if listcolunas[i] != '\n':
                        match_teste_quantp= regex_nire.search(remove_varios_espacos(remove_acentos(listcolunas[i].text.upper())))
                    i = i + 1
                if match_teste_quantp:
                    for coluna in listcolunas:
                        try:
                            match_titulo_bigp = regex_titulo.search(remove_varios_espacos(remove_acentos(coluna.text.upper())))
                            match_nire_bigp =  regex_nire.search(remove_varios_espacos(remove_acentos(coluna.text.upper())))

                            if match_titulo_bigp or match_nire_bigp:
                                colunas_maiores,ajuste_posicao = limpa_coluna_insere_em_dic(coluna, colunas_maiores,ajuste_posicao)
                            else:
                                chave_ultimo_item = list(colunas_maiores.keys())[-1]
                                match_posicao_anterior = regex_nire.search(remove_varios_espacos(remove_acentos(colunas_maiores[chave_ultimo_item].upper())))
                                if match_posicao_anterior:
                                    colunas_maiores,ajuste_posicao = limpa_coluna_insere_em_dic(coluna,colunas_maiores,ajuste_posicao,ajuste_opcional =True)
                        except Exception as e:
                            if 'NavigableString' in e.args[0]:
                                continue
                            elif 'list index out of range' not in e.args[0]:
                                print(e)
            else:
                for coluna in listcolunas:
                    try:
                        match = regex.search(remove_varios_espacos(remove_acentos(coluna.text.upper())))
                        #if len(coluna.text) > 600 and match
                        if len(coluna.text) > 600 or match:
                            colunas_maiores,ajuste_posicao = limpa_coluna_insere_em_dic(coluna,colunas_maiores,ajuste_posicao)
                    except Exception as e:
                        if 'NavigableString' in e.args[0]:
                            continue
                        else:
                            print(e)

            caminho_novo = (caminho_dir_html_ano_mes+"/"+diario.replace("-html.html",".txt"))
            #caminho_novo = (filepath.replace("-html.html", ".txt"))
            diario_acertado = open(caminho_novo, "a+")
            diario_acertado.writelines(list(colunas_maiores.values()))
            diario_acertado.close()








            #log_coluna =open("C:\\Users\\e279950109\\IpeaJUS\\log_coluna_invertidas.txt","a+")
            #log = new_txt +" : "+pagina.attrs["id"]
            #log_coluna.write(log)
            #log_coluna.write("\n")
            #colunas_maiores.reverse()



            # else:
            #     diario_acertado = open(caminho_novo.format(arquiv = new_txt), "a+")
            #     diario_acertado.writelines(colunas_maiores)





        print('Converteu o caderno {}'.format(caminho_novo))
        return "caminho:diario.txt"

if __name__ == '__main__':
    #checa_coluna_invertida ("/home/b279950109/JUCESP_2013_06_18-html.html",diario= 'JUCESP_2013_06_18-html.html',ano='2013',mes="06")
    for ano in range(2001,2021):
        for mes in range(1,13):
            if mes < 10:
                mes = "0" + str(mes)
            diarios = os.listdir('/mnt/dmlocal/dados/SP/JUCESP/html/{ano}/{mes}'.format(ano=ano,mes = mes))
            for diario in diarios:
                checa_coluna_invertida(filepath="/mnt/dmlocal/dados/SP/JUCESP/html/{ano}/{mes}/{diario}".format(ano=ano,mes = mes,diario=diario),diario= diario,ano=ano,mes=mes)