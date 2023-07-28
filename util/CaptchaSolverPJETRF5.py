from util.CaptchaSolver import CaptchaSolver
from PIL import Image
import os
import operator
import pytesseract
import requests
from bs4 import BeautifulSoup as bs
from io import BytesIO


class CaptchaSolverPJETRF5(CaptchaSolver):


    def parse_captcha(self, filename):
        img = Image.open(filename)
        imagem = self.black_and_white(filename=filename, img=img, level=235)
        imagem = self.remove_noise(imagem, chop=1)
        imagem = self.mode_filter(filename=imagem, modefilter=2)
        textoSemEspaco = (pytesseract.image_to_string(Image.open(imagem),
                                                      config="-c tessedit_char_whitelist=0123456789 -psm 8"))

        textoSemEspaco = textoSemEspaco.replace(" ","")
        return textoSemEspaco


# if __name__ == '__main__':
#     c = CaptchaSolverPJETRF5()
#     countC = 0
#     countE = 0
#     for x in range(50):
#         resultado = c.parse_captcha(('C:\\Users\\e279950109\\Desktop\\captchas\\captcha{num}.jpeg').format(num = str(x)))
#         os.rename('C:\\Users\\e279950109\\Desktop\\captchas\\CP_captcha{num}.jpeg'.format(num = str(x)), 'C:\\Users\\e279950109\\Desktop\\captchas\\{resultado}_{num}.jpeg'.format(resultado=resultado, num= str(x)))
#         if len(resultado) == 6:
#             print(resultado)
#             print(60 * '*')
#             countC = countC + 1
#
#         else:
#             print("captcha errado " + resultado)
#             print(60 * '*')
#             countE = countE + 1
#
#     print(countC)
#     print(countE)


    # for x in range(50):
    #   s = requests.Session()
    #   urlCaptcha = s.get("https://pje.trf5.jus.br//pje/seam/resource/captcha?f=1540216513925")
    #   ima = Image.open(BytesIO(urlCaptcha.content))
    #   ima.save(('C:\\Users\\e279950109\\Desktop\\captchas\\captcha{num}.jpeg').format(num = str(x)))