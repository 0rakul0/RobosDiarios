from datetime import timedelta, datetime, date
import requests
import time
from bs4 import BeautifulSoup as bs
from util.ConfigManager import ConfigManager
from robosdiarios.RoboDiarioBase import RoboDiarioBase


class RoboDiarioPB(RoboDiarioBase):
    def __init__(self):

        self.url_inicial = 'https://app.tjpb.jus.br/dje/paginas/diario_justica/publico/buscas.jsf?'
        self.data_url_acervo = 'tipoBusca=intervalo&dtInicio={dtInicio}&dtFinal={dtFinal}&'
        self.url_intermediaria_para_qtd_pags = 'https://app.tjpb.jus.br/dje/paginas/diario_justica/publico/buscas.jsf?tipoBusca=intervalo&dtInicio={dtInicio}&dtFinal={dtFinal}'
        self.incremento = '&formDownload=formDownload&javax.faces.ViewState={viewstate}&{tabela}={tabela}'
        self.url_xml = 'https://app.tjpb.jus.br/dje/paginas/diario_justica/publico/buscas.jsf?tipoBusca=intervalo&dtInicio={data_inicio}&dtFinal={data_fim}&javax.faces.partial.ajax=true&javax.faces.source=tabela&javax.faces.partial.execute=tabela&javax.faces.partial.render=tabela&tabela=tabela&tabela_pagination=true&tabela_first={num_dez_em_dez}&tabela_rows={max_diarios}&tabela_encodeFeature=true&formDownload=formDownload&javax.faces.ViewState={view_state}'
        super(RoboDiarioPB, self).__init__("DJPB", "log_robo_pb.txt", "erro_robo_pb.txt")


    def download_atualizacao_diaria(self):
        dtInicio = self.data_inicial('DJPB').strftime('%d/%m/%Y')
        # dtInicio = datetime.now().strftime('%d/%m/%Y')
        dtFinal = datetime.now().strftime('%d/%m/%Y')

        soup_intermediario, s, jsessionid = self.faz_requisicao(dtInicio,dtFinal)

        try:
            qtd_pags = int(soup_intermediario.find('span', {'class': 'ui-paginator-current'}).text.split()[-1].replace(')', ''))
        except AttributeError:
            qtd_pags = 1

        soup, header_cadernos, view_state = self.xml_page(qtd_pags, soup_intermediario, jsessionid, s)

        tabela = self.get_tabela(soup)

        if tabela is None:
            self.escreve_log('Não houveram cadernos no dia {}'.format(dtFinal))
            self.escreve_log('########### FIM ROBÔ DJPB ###########')
            quit()

        posicao_tabela_caderno = self.get_data_posicao_caderno (tabela)

        for data, caderno in posicao_tabela_caderno.items ():
            data_caderno_list = data.split ('/')
            data_caderno = date (int (data_caderno_list[2]), int (data_caderno_list[1]), int (data_caderno_list[0]))

            name = 'DJPB_{}.pdf'.format (data_caderno.strftime ('%Y_%m_%d'))
            link_caderno = self.url_inicial + self.data_url_acervo.format(dtInicio=dtInicio, dtFinal=dtFinal) + self.incremento.format (viewstate=view_state, tabela=caderno) + self.data_url_acervo.replace('tipoBusca', '')
            self.escreve_log ('Baixando o diário {}'.format (name))
            self.filemanager.download (name=name, data=data_caderno, url=link_caderno, headers=header_cadernos)


    def faz_requisicao(self,dtInicio,dtFinal):
        s = requests.Session ()

        header_inicial = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                          'Accept-Encoding': 'gzip, deflate, br',
                          'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                          'Connection': 'keep-alive',
                          'Host': 'app.tjpb.jus.br',
                          'Sec-Fetch-Dest': 'document',
                          'Sec-Fetch-Mode': 'navigate',
                          'Sec-Fetch-Site': 'none',
                          'Sec-Fetch-User': '?1',
                          'Upgrade-Insecure-Requests': '1',
                          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
        try:
            html_inicial = s.get (self.url_inicial, headers=header_inicial)
        except:
            time.sleep (3)
            html_inicial = s.get (self.url_inicial, headers=header_inicial)

        jsessionid = html_inicial.headers._store['set-cookie'][1].split (';')[0]

        header_intermediario = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                                'Connection': 'keep-alive',
                                'Cookie': 'primefaces.download=true; ' + jsessionid,
                                'Host': 'app.tjpb.jus.br',
                                'Sec-Fetch-Dest': 'document',
                                'Sec-Fetch-Mode': 'navigate',
                                'Sec-Fetch-Site': 'none',
                                'Sec-Fetch-User': '?1',
                                'Upgrade-Insecure-Requests': '1',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

        html_intermediario = s.get (self.url_intermediaria_para_qtd_pags.format(dtInicio=dtInicio, dtFinal=dtFinal), headers=header_intermediario).text

        soup_intermediario = bs (html_intermediario, 'html5lib')

        return soup_intermediario, s, jsessionid


    def xml_page(self, qtd_pags, soup_intermediario, jsessionid, s, data_inicio=None):

        data_fim = datetime.now ().strftime ('%d/%m/%Y')

        if data_inicio is None:
            data_inicio = data_fim

        num_dez_em_dez = 0
        max_diarios = qtd_pags * 10
        view_state = soup_intermediario.find ('input', {'name': 'javax.faces.ViewState'}).attrs['value']

        headers_xml = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                       'Accept-Encoding': 'gzip, deflate, br',
                       'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                       'Cache-Control': 'max-age=0',
                       'Connection': 'keep-alive',
                       'Cookie': 'primefaces.download=true; ' + jsessionid,
                       'Host': 'app.tjpb.jus.br',
                       'Sec-Fetch-Dest': 'document',
                       'Sec-Fetch-Mode': 'navigate',
                       'Sec-Fetch-Site': 'none',
                       'Sec-Fetch-User': '?1',
                       'Upgrade-Insecure-Requests': '1',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

        get_xml_page = s.get (self.url_xml.format (data_inicio=data_inicio, data_fim=data_fim, num_dez_em_dez=num_dez_em_dez, max_diarios=max_diarios, view_state=view_state), headers=headers_xml)
        get_xml_page = str (get_xml_page.text).replace ("<?xml version='1.0' encoding='UTF-8'?>", '').replace ('<![CDATA[<tr data-ri="0" class="ui-widget-content ui-datatable-even" role="row">', '').replace ('<script type="text/javascript" src="/dje/javax.faces.resource/jsf.js.jsf?ln=javax.faces">', '').replace ('</script>', '')
        soup = bs (get_xml_page, 'lxml')

        header_cadernos = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                           'Accept-Encoding': 'gzip, deflate, br',
                           'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                           'Connection': 'keep-alive',
                           'Cookie': 'primefaces.download=true; ' + jsessionid,
                           'Host': 'app.tjpb.jus.br',
                           'Sec-Fetch-Dest': 'document',
                           'Sec-Fetch-Mode': 'navigate',
                           'Sec-Fetch-Site': 'none',
                           'Upgrade-Insecure-Requests': '1',
                           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

        return soup, header_cadernos, view_state


    def atualiza_acervo(self):

        dtInicio = '01/07/2023'
        dtFinal = datetime.now().strftime('%d/%m/%Y')

        soup_intermediario, s, jsessionid = self.faz_requisicao(dtInicio,dtFinal)

        qtd_pags = int (soup_intermediario.find ('span', {'class': 'ui-paginator-current'}).text.split ()[-1].replace (')', ''))

        soup, header_cadernos, view_state = self.xml_page(qtd_pags, soup_intermediario, jsessionid, s)

        tabela = self.get_tabela(soup)

        posicao_tabela_caderno = self.get_data_posicao_caderno(tabela)

        for data, caderno in posicao_tabela_caderno.items():
            data_caderno_list = data.split('/')
            data_caderno = date(int(data_caderno_list[2]), int(data_caderno_list[1]), int(data_caderno_list[0]))

            name = 'DJPB_{}.pdf'.format(data_caderno.strftime('%Y_%m_%d'))
            link_caderno = self.url_inicial + self.data_url_acervo.format(dtInicio=dtInicio, dtFinal=dtFinal) + self.incremento.format(viewstate=view_state, tabela=caderno) + self.data_url_acervo.replace('tipoBusca', '')
            self.escreve_log('Baixando o diário {}'.format(name))
            self.filemanager.download(name=name,data=data_caderno, url=link_caderno, headers=header_cadernos)


    def get_tabela(self, soup):
        return soup.find('update',{'id':'tabela'})


    def get_data_posicao_caderno(self, tabela):
        cadernos = {}
        for data, posicao_caderno in zip(tabela.find_all('td',{'class':''}),tabela.find_all('td',{'class':'w10'})):
            try:
                cadernos[data.text] = posicao_caderno.find('a').attrs['onclick'].split('\'')[3]
            except:
                continue

        return cadernos


    def escreve_log(self, txt):
        ConfigManager ().escreve_log ('[' + datetime.now ().strftime ("%Y-%m-%d %H:%M") + '] ## ' + txt, self.robo, self.log)

    def data_limite(self):
        return date(2023, 7, 20)


if __name__ == '__main__':
    robo = RoboDiarioPB()
    robo.escreve_log('########### INÍCIO ROBÔ DJPB ###########')
    # robo.atualiza_acervo()
    robo.download_atualizacao_diaria()
    robo.escreve_log('########### FIM ROBÔ DJPB ###########')



