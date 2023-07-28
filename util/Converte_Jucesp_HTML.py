from subprocess import Popen, PIPE, STDOUT
import abc,os,traceback

import re
import sys

# class Converte_Jucesp_HTML():

def converte_jucesp_html(caminho_arquivo, filetype, ano, mes, diario):
    contents = "Não foi possível ler conteúdo do arquivo."

    if not 'linux' in sys.platform:
        print("Conversão funciona somente em linux")

    elif filetype == "pdf":
        caminho_dir_html_ano = re.sub('pdf.*', 'html/{ano}'.format(ano=ano), caminho_arquivo)
        caminho_dir_html_ano_mes = re.sub('pdf.*', 'html/{ano}/{mes}'.format(ano=ano, mes=mes), caminho_arquivo)
        if not os.path.exists(caminho_dir_html_ano):
            os.mkdir(caminho_dir_html_ano)
        if not os.path.exists(caminho_dir_html_ano_mes):
            os.mkdir(caminho_dir_html_ano_mes)

        caminho_dir_html_completo = caminho_dir_html_ano_mes + "/" + diario.replace(".pdf", ".html")

        cmd = 'pdftohtml -hidden -q -c -s -i {PDF} {html} && ' \
              'sed -e s/"<[^>]*>"//g {html}'.format(PDF=caminho_arquivo, html=(
        caminho_dir_html_completo))

        process = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
        (text, err) = process.communicate()
        exit_code = process.wait()

        try:
            contents = text.decode("utf-8")
            print("Convertendo (JUCESP to HTML): {}".format(caminho_dir_html_completo))
        except:
            print('Impossível converter o caderno {} para HTML'.format(diario))
            pass
    else:
        print("conversão para este tipo ainda não foi implementada")

    return contents, caminho_dir_html_completo

# if __name__ == '__main__':
#     t = Converte_Jucesp_HTML
#     for ano in range(2001,2021):
#         for mes in range(1,13):
#             if mes < 10:
#                 mes = "0" + str(mes)
#             diarios = os.listdir('/mnt/dmlocal/dados/SP/JUCESP/pdf/{ano}/{mes}'.format(ano=ano,mes = mes))
#             for diario in diarios:
#                 t.converte_jucesp_html(caminho_arquivo='/mnt/dmlocal/dados/SP/JUCESP/pdf/{ano}/{mes}/{diario}'.format(ano=ano,mes = mes,diario=diario),filetype='pdf',ano = ano,mes=mes,diario = diario)