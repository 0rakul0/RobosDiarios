import requests
from bs4 import BeautifulSoup as bs
import os
from util.CaptchaSolverTRF3JEF import CaptchaSolverTRF3JEF

for i in range(100):

    first = requests.post(r'http://jef.trf3.jus.br/')
    first_soup = bs(first.text, 'html5lib')
    params = {'tela': 1}
    second = requests.get(r'http://jef.trf3.jus.br/consulta/consultapro.php', params=params)
    second_soup = bs(second.text,'html5lib')
    image = requests.get(r'http://jef.trf3.jus.br/consulta/' + second_soup.select('img')[0]['src'])
    filename = r'C:\Users\b2552833\Documents\IpeaJUS\util\CaptchaSolverTRF3JEFDataset\Captcha' + '_' + str(i) + '_'

    with open(filename + '.jpg', 'wb') as f:
        f.write(image.content)

    Solver = CaptchaSolverTRF3JEF()

    prediction = Solver.parse_captcha(filename + '.jpg')

    os.remove(r'C:\Users\b2552833\Documents\IpeaJUS\util\CaptchaSolverTRF3JEFDataset\CP_Captcha' + '_' + str(i) + '_' + '.jpg')
    os.remove(r'C:\Users\b2552833\Documents\IpeaJUS\util\CaptchaSolverTRF3JEFDataset\CP_CP_Captcha' + '_' + str(i) + '_' + '.jpg')
    os.remove(r'C:\Users\b2552833\Documents\IpeaJUS\util\CaptchaSolverTRF3JEFDataset\CP_CPCP_CP_Captcha' + '_' + str(i) + '_' + '.jpg')

    if prediction is None:
        prediction = 'error'

    os.rename(filename + '.jpg', filename + prediction + '.jpg')