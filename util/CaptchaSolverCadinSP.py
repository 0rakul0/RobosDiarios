# -*- coding: utf-8 -*-
from util.CaptchaSolver import CaptchaSolver
from PIL import Image
import os
import operator
import pytesseract



class CaptchaSolverCadinSP(CaptchaSolver):

    def parse_captcha(self,filename,minuscula):
        # chop = 2
        # print(os.path.join(filename, arquivo))
        img = Image.open(filename)
        imagem = self.black_and_white(filename=filename, img=img, level=235)
        imagem = self.remove_noise(imagem, chop=2)

        # new_file = os.path.join(filename, 'CP_' + arquivo)
        # image.save(new_file)
        # print(pytesseract.image_to_string(Image.open(new_file),
        #     config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ012345789 -psm 6" ))
        imagem = self.mode_filter(filename=imagem, modefilter=1)
        # print(pytesseract.image_to_string(Image.open(imagem),
        #                                   config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ012345789 -psm 6"))
        if minuscula == True:
            textoSemEspaco = (pytesseract.image_to_string(Image.open(imagem),
                                                          config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 -psm 8"))
        else:
            textoSemEspaco = (pytesseract.image_to_string(Image.open(imagem),
                                                          config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -psm 8"))

        #textoSemEspaco = self.tesseract(filename=imagem,number_only=False,whitelist='ABCDEFGHIJKLMNOPQRSTUVWXYZ012345789',use_lstm=False)
        #textoSemEspaco = textoSemEspaco.replace("\n", "")
        #textoSemEspaco.replace(" ","")


        #return self.tesseract(textoSemEspaco)
        #return textoSemEspaco
        return textoSemEspaco
# if __name__ == '__main__':
#      c = CaptchaSolverCadinSP()
#      c.parse_captcha('C:\\Users\\e279950109\\Desktop\\captchas\\img.png',False)
