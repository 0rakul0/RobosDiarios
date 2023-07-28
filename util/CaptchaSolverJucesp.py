from util.CaptchaSolver import CaptchaSolver
from PIL import Image
import os
import operator
import pytesseract

class CaptchaSolverJucesp(CaptchaSolver):
    def parse_captcha(self, filename):
        img = Image.open(filename)
        #img = Image.open(filename).convert('1')

        #caso estiver errando muito tentar mudar level de balck_and_white para ajuste ou incluir mod_filter(mas acredito q a parte do mod_filter nao vai ajudar muito)


        #filename2 = self.black_and_white(img=img, level=30,filename=filename)

        #textoSemEspaco = (pytesseract.image_to_string(Image.open(imagem),
                                                      #config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -psm 8"))
        #print(textoSemEspaco)
        #img = self.test_limpa_sujeira(filename)
        #imga = Image.fromarray(imagem).convert('1')

        #imagem = self.remove_noise(image= img ,chop=1,filename=filename)

        #imagem = self.teste_captcha_clean(image=None, filename=filename)
        img = self.test_limpa_sujeira(filename)

        #img = self.test_limpa_sujeira(imagem)

        textoSemEspaco = pytesseract.image_to_string(img,
                                                     config="-c 'tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' --psm 7")
        #textoSemEspaco = pytesseract.image_to_string(Image.open(imagem),config="-c 'tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' --psm 8")
        textoSemEspaco = textoSemEspaco.replace(' ','')
        # print(textoSemEspaco)

         #imagem = self.mode_filter(filename=imagem, modefilter=3)
        # textoSemEspaco = (pytesseract.image_to_string(Image.open(imagem),
        #                                               config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -psm 8"))


        print(textoSemEspaco+ ": "+filename)
        return (textoSemEspaco)


if __name__ == '__main__':
        c = CaptchaSolverJucesp()
        captchas = os.listdir('/home/b279950109/Downloads/ca')
        resultado = 0
        for captcha in captchas :
            textoSemEspaco = c.parse_captcha(f'/home/b279950109/Downloads/ca/{captcha}'.format(captcha=captcha))
            if textoSemEspaco.strip().replace("\\n\\f","") == captcha.replace(".jpeg", ''):
                resultado = resultado + 1
        print ("Captchas certos: "+str(resultado))

