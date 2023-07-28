__author__ = 'B249025230'
import requests
from bs4 import BeautifulSoup

def varre_tabela_noticias(nome_arquivo):
    site_tjsp = 'http://www.tjsp.jus.br'
    for i in range(1,502):
        noticias = []
        print('pagina '+str(i))
        link = 'http://www.tjsp.jus.br/Segmento/Magistrados/Designacoes?pagina={}'
        htm = requests.get(link.format(i))
        pagina = htm.content
        soup = BeautifulSoup(pagina,'html5lib')
        artigos = soup.find_all('article')
        for artigo in artigos:
            link_artigo = artigo.find('a')
            if link_artigo:
                link_artigo = site_tjsp + link_artigo['href']
                noticias.append(link_artigo)
                print(link_artigo)
        for noticia in noticias:
            visita_noticia(noticia,nome_arquivo)


def visita_noticia(link,arquivo):
    with open(arquivo,'a') as file:
        htm = requests.get(link)
        pagina = htm.content
        soup = BeautifulSoup(pagina,'html5lib')
        cabecalho = soup.find_all('header')[2]
        titulo = cabecalho.h3.text
        data = cabecalho.time.text
        paragrafos = soup.find('div',{'class':'noticia-content'}).find_all('p')
        for paragrafo in paragrafos:
            texto = paragrafo.text.strip()
            if texto != '':
                if '\n\n' in texto:
                    texto = texto.replace('\n\n', '"\n"{}";"{}":"'.format(titulo,data))
                print('"{}";"{}";"{}"'.format(titulo,data,texto))
                file.write('"{}";"{}";"{}"\n'.format(titulo,data,texto))


nome_arquivo = 'correcao_noticia.csv'
with open(nome_arquivo,'w') as file:
    file.write('"{}";"{}";"{}"\n'.format('titulo','data','texto'))
varre_tabela_noticias(nome_arquivo)
# visita_noticia('http://www.tjsp.jus.br/Segmento/Magistrados/Noticia?codigoNoticia=50707&pagina=1',nome_arquivo)