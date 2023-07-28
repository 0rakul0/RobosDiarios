# -*- coding: utf-8 -*-
from util.CaptchaSolver import CaptchaSolver
from PIL import Image
import pytesseract

'''
Para esta classe funcionar é necessario que exista uma variável de ambiente para o caminho do tesseract
'''


class CaptchaSolverTRF3JEF(CaptchaSolver):

    def __init__(self):
        self._tamanho_captcha = 4
        self._config = "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -psm 8"

    def parse_captcha(self, filename):
        imagem = self.mode_filter(filename=filename, modefilter=3)
        imagem = self.black_and_white(img=Image.open(imagem), filename= imagem, level=150)
        imagem = self.remove_noise(imagem, chop=2)

        texto_captcha = (pytesseract.image_to_string(Image.open(imagem), config=self._config))

        if len(texto_captcha) >= self._tamanho_captcha:
            return texto_captcha
        else:
            return None

