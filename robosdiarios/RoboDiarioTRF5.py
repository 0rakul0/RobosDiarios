import requests
from bs4 import BeautifulSoup as bs
import re
import datetime
from robosdiarios.RoboDiarioBase import RoboDiarioBase
from util.ConfigManager import ConfigManager
import os.path


class RoboDiarioTRF5(RoboDiarioBase):
    """
    Robo responsavel pelo download de diarios oficias do TRF2.
    """
    def __init__(self):

        self.url_trf5 = 'https://www4.trf5.jus.br/diarioeletinternet/index.jsp'
        super(RoboDiarioTRF5, self).__init__("TRF05", "TRF5_robodiario.txt", "TRF5_robodiario.err")
        self.nome_do_orgao = {5: "TRF5", 80: "SJAL", 81: "SJCE", 82: "SJPB", 83: "SJPE", 84: "SJRN", 85: "SJSE"}
        self.nome_da_edicao = {1: "Judicial", 2: "Administrativo"}

    def download_atualizacao_diaria(self):
        """
        Aciona o metodo de download de diarios oficiais.
        """
        self.download_trf5()

    def data_limite(self):
        """
        Retorna data limite inferior dos diarios que devem ser baixados.
        """
        return datetime.date(2009,1,1)

    def data_inicial(self, filtro, tipo_arquivo="*.pdf", por_tipo=True,somente_inicio_mes=False, subfolders=None):
        """
        Retorna a data do ultimo diario baixado.
        """
        data = super(RoboDiarioTRF5, self).data_inicial(filtro, tipo_arquivo, por_tipo, subfolders)

        if somente_inicio_mes:
            return data.replace(day=1)

        return data

    def escreve_log(self, txt):
        ConfigManager ().escreve_log (txt, self.robo, self.log, verbose=False)

    def download_trf5(self):
        """
        Realiza o download dos diarios para as datas definidas.
        """
        self.escreve_log('########### INICIO TRF05 ###########')
        print('########### INICIO TRF05 ###########')

        primeira_pagina = requests.get(self.url_trf5,
                                       verify=False)

        jsessionid = primeira_pagina.cookies['JSESSIONID']

        cookie = {'JSESSIONID': jsessionid}

        soup = bs(primeira_pagina.text,
                  'html5lib')

        try:
            view_state = soup.select('#javax.faces.ViewState')[0].attrs['value']
        except:
            print(r"Um tag com id='#javax.faces.ViewState' não foi encontrado na página.")

        for orgao in [5, 80, 81, 82, 83, 84, 85]:
            for edicao in [1, 2]:

                data_do_ultimo_download_de_cada_orgao = self.data_inicial(self.nome_da_edicao.get(edicao) + "_" +
                                                                          self.nome_do_orgao.get(orgao))


                print("Ultimo download do orgao: {}, edicao: {} -> {}".format(self.nome_do_orgao.get(orgao),
                                                                              self.nome_da_edicao.get(edicao),
                                                                              data_do_ultimo_download_de_cada_orgao))


                for ano in range(data_do_ultimo_download_de_cada_orgao.year, datetime.date.today().year + 1):


                    parametros_de_busca_com_o_ano = {'AJAXREQUEST': '_viewRoot',
                                                   'autoScroll': '',
                                                   'frmVisao': 'frmVisao',
                                                   'frmVisao:edicao': edicao,
                                                   'frmVisao:j_id42': 'frmVisao:j_id42',
                                                   'frmVisao:meses': '',
                                                   'frmVisao:orgao': orgao,
                                                   'frmVisao:periodo': ano,
                                                   'javax.faces.ViewState': view_state}

                    primeira_busca = requests.post(self.url_trf5,
                                                   verify=False,
                                                   data=parametros_de_busca_com_o_ano,
                                                   cookies=cookie)

                    if ano == datetime.date.today().year:
                        ultimo_mes_do_ano = datetime.date.today().month
                    else:
                        ultimo_mes_do_ano = 12

                    if ano == data_do_ultimo_download_de_cada_orgao.year:
                        primeiro_mes_de_busca_do_ano = data_do_ultimo_download_de_cada_orgao.month
                    else:
                        primeiro_mes_de_busca_do_ano = 1

                    for mes in range(primeiro_mes_de_busca_do_ano, ultimo_mes_do_ano + 1):

                        prametros_de_busca_com_o_mes = {'autoScroll': '',
                                                       'frmVisao': 'frmVisao',
                                                       'frmVisao:edicao': edicao,
                                                       'frmVisao:j_id48': 'Pesquisar',
                                                       'frmVisao:meses': mes,
                                                       'frmVisao:orgao': orgao,
                                                       'frmVisao:periodo': ano,
                                                       'javax.faces.ViewState': view_state}

                        busca_com_o_mes = requests.post(self.url_trf5,
                                                        verify=False,
                                                        data=prametros_de_busca_com_o_mes,
                                                        cookies=cookie)

                        verificador_de_documentos_no_mes_soup = bs(busca_com_o_mes.text, 'html5lib')

                        try:
                            existem_registros_neste_mes = verificador_de_documentos_no_mes_soup.find('div', {'id': 'area-mensagens'}).span.get_text()
                        except AttributeError:
                            existem_registros_neste_mes = 'Registros encontrados.'

                        if existem_registros_neste_mes == 'Nenhum registro encontrado.':
                            print("Nenhum diario para o mes: {}/{}, orgao: {}, edicao: {}.".format(mes,
                                                                                                   ano,
                                                                                                   self.nome_do_orgao.get(orgao),
                                                                                                   self.nome_da_edicao.get(edicao)))
                            self.escreve_log("Nenhum diario para o mes: {}/{}, orgao: {}, edicao: {}.".format(mes,
                                                                                                              ano,
                                                                                                              self.nome_do_orgao.get(orgao),
                                                                                                              self.nome_da_edicao.get(edicao)))
                            continue

                        parametros_de_busca_para_100_arquivos_por_pagina = {'frmPesquisa:pagina': '1',
                                                                            'frmPesquisa:quantidadedeRegistros': '100',
                                                                            'frmPesquisa': 'frmPesquisa',
                                                                            'autoScroll': '',
                                                                            'javax.faces.ViewState': view_state}

                        buscar_com_100_arquivos_por_pagina = requests.post(self.url_trf5,
                                                                           data=parametros_de_busca_para_100_arquivos_por_pagina,
                                                                           verify=False,
                                                                           cookies=cookie)

                        pagina_final_da_busca_soup = bs(buscar_com_100_arquivos_por_pagina.text, 'html5lib')

                        string_contendo_o_total_de_arquivos = pagina_final_da_busca_soup.find('div',{'id': 'frmPesquisa:j_id78'}).tr.td.get_text()

                        numero_de_arquivos_disponiveis_no_mes = re.search(r'(\d+)',
                                                                          string_contendo_o_total_de_arquivos)
                        print("{} diario(s) para o mes: {}/{}, orgao: {}, edicao: {}.".format(numero_de_arquivos_disponiveis_no_mes.group(),
                                                                                              mes,
                                                                                              ano,
                                                                                              self.nome_do_orgao.get(orgao),
                                                                                              self.nome_da_edicao.get(edicao)))
                        self.escreve_log("{} diario para o mes: {}/{}, orgao: {}, edicao: {}.".format(numero_de_arquivos_disponiveis_no_mes.group(),
                                                                                                      mes,
                                                                                                      ano,
                                                                                                      self.nome_do_orgao.get(orgao),
                                                                                                      self.nome_da_edicao.get(edicao)))

                        nomes_de_arquivos_neste_mes = set()
                        contador_de_repeticao_de_nomes = 0

                        for numero_do_arquivo in range(int(numero_de_arquivos_disponiveis_no_mes.group())):

                            parametros_para_download_de_pdf = {'frmPesquisa': 'frmPesquisa',
                                                               'frmPesquisa:_idcl': 'frmPesquisa:tDiarios:' +
                                                               str(numero_do_arquivo) + ':j_id67',
                                                               'autoScroll': '',
                                                               'javax.faces.ViewState': view_state}

                            # arquivo = requests.post(self.url_trf5, data=parametros_para_download_de_pdf, verify=False, cookies=cookie)

                            string_contendo_a_data_do_arquivo = pagina_final_da_busca_soup.find('td',
                                                                                                {'id': 'frmPesquisa:tDiarios:' +
                                                                                                       str(numero_do_arquivo) +
                                                                                                       ':j_id61'}).get_text()

                            data_do_arquivo = re.search(r'(\d\d)\/(\d\d)\/(\d\d\d\d)',
                                                        string_contendo_a_data_do_arquivo)

                            string_contendo_a_descricao_do_arquivo = pagina_final_da_busca_soup.find('td',
                                                                                                {'id': 'frmPesquisa:tDiarios:' +
                                                                                                       str(numero_do_arquivo) +
                                                                                                       ':j_id55'}).get_text()

                            descricao_do_arquivo = re.search(r'(\d{0,4}\.?\d{0,2})/\d{4}',
                                                             string_contendo_a_descricao_do_arquivo)

                            if descricao_do_arquivo:
                                descricao_do_arquivo_str = str(descricao_do_arquivo.group(1)).replace('.','') + '_'
                            else:
                                descricao_do_arquivo_str = ''

                            nome_final_do_arquivo = r'TRF05_' + self.nome_da_edicao.get(edicao) + '_' + \
                                                    self.nome_do_orgao.get(orgao) + '_' + \
                                                    descricao_do_arquivo_str + \
                                                    str(data_do_arquivo.group(3)) + '_' + \
                                                    str(data_do_arquivo.group(2)) + '_' + \
                                                    str(data_do_arquivo.group(1)) + '.pdf'

                            if nome_final_do_arquivo in nomes_de_arquivos_neste_mes:
                                contador_de_repeticao_de_nomes += 1
                                nome_final_do_arquivo = r'TRF05_' + self.nome_da_edicao.get(edicao) + '_' + \
                                                    self.nome_do_orgao.get(orgao) + '_' + \
                                                    descricao_do_arquivo_str + \
                                                    str(contador_de_repeticao_de_nomes) + '_' + \
                                                    str(data_do_arquivo.group(3)) + '_' + \
                                                    str(data_do_arquivo.group(2)) + '_' + \
                                                    str(data_do_arquivo.group(1)) + '.pdf'
                                nomes_de_arquivos_neste_mes.add(nome_final_do_arquivo)
                            else:
                                nomes_de_arquivos_neste_mes.add(nome_final_do_arquivo)

                            data_download = datetime.datetime.strptime(data_do_arquivo.group(0), '%d/%m/%Y')

                            self.filemanager.download(nome_final_do_arquivo, data_download, self.url_trf5, stream=True,
                                                      cookies=cookie, params_post=parametros_para_download_de_pdf)

                            # if arquivo.status_code != 200:
                            #     self.escreve_log('O arquivo {} não foi baixado'.format(nome_final_do_arquivo))
                            #     print('O arquivo {} não foi baixado'.format(nome_final_do_arquivo))
                            #     continue

                            # with open(self.filemanager.caminho(nome_final_do_arquivo) + os.path.sep + nome_final_do_arquivo, 'wb') as f:
                            #     f.write(arquivo.content)
                            #     self.escreve_log('Baixou o diário {}'.format(nome_final_do_arquivo))
                            #     print('Baixou o diário {}'.format(nome_final_do_arquivo))


if __name__ == '__main__':

    robo = RoboDiarioTRF5()
    robo.download_atualizacao_diaria()
    print('########### FIM TRF05 ###########')
