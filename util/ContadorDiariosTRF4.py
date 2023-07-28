import requests
from bs4 import BeautifulSoup as bs

url_trf4 = "https://www2.trf4.jus.br/trf4/diario/edicoes_anteriores.php"
meses = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
anos = ['2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']

primeira_pagina = requests.post(url_trf4)
soup_primeira_pagina = bs(primeira_pagina.text, 'html5lib')
diarios = 0

for ano in anos:
    if ano == '2018':
        meses = ['1', '2', '3', '4', '5', '6', '7', '8']
    for mes in meses:
        params = {'edAnteriores' : ano + '_' + mes}
        pagina = requests.post(url_trf4, data=params)
        soup_pagina = bs(pagina.text, 'html5lib')
        diarios += len(soup_pagina.select('form.formulario > a'))
        print('Mes: {} Ano: {} Diarios: {}'.format(mes, ano, len(soup_pagina.select('form.formulario > a'))))

print('Número de diarios encontrados: {}'.format(diarios))