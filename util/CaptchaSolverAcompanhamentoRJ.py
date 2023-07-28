from __future__ import print_function
import pytesseract
from util.CaptchaSolver import CaptchaSolver
import numpy as np
import os
import time
import re
import cv2
from PIL import Image

class CaptchaSolverAcompanhamentoRJ(CaptchaSolver):

    def remove_fundo(self,numpy_imagem):
        ret, thresh_img = cv2.threshold(numpy_imagem, 150, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 4))
        morph_img = cv2.morphologyEx(thresh_img, cv2.MORPH_CLOSE, kernel)
        return morph_img

    def escreve_le_imagem_tesseract(self,morph_img):
        cv2.imwrite("C:\\Users\\e7609043\\PycharmProjects\\IpeaJUS\\util\\CaptchasRJ\\result11.jpg", morph_img)
        imagem = Image.open('C:\\Users\\e7609043\\PycharmProjects\\IpeaJUS\\util\\CaptchasRJ\\result11.jpg')
        result = pytesseract.image_to_string(imagem, lang='eng', config="--psm 11 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz0123456789 ")
        return result

    def parse_captcha(self, i, filename):
        result = ''
        while len(result)!= 5:
            count_zeros_na_linha = 0
            linha = 0
            count_linhas = 0
            col = 93
            img = Image.open(filename)
            area = (5, 5, 135, 55)
            imagem_recortada = img.crop(area)
            numpy_imagem = np.asarray(imagem_recortada).astype(np.uint8)
            morph_img = self.remove_fundo(numpy_imagem)
            numpy_imagem = cv2.cvtColor(morph_img,cv2.COLOR_BGR2GRAY)
            morph_img = self.remove_fundo(numpy_imagem)
            while count_linhas is not 6:
                while count_zeros_na_linha is not 30:
                    try:
                        if morph_img[24:30][count_linhas][col] == 255:
                            linha += 1
                            break
                        else:
                            morph_img[24:30][count_linhas][col] = 255
                            col += 1
                            count_zeros_na_linha += 1
                    except IndexError as e:
                        linha += 1
                        break
                count_linhas += 1
                count_zeros_na_linha = 0
                col = 93
            cv2.imwrite("C:\\Users\\e7609043\\PycharmProjects\\IpeaJUS\\util\\CaptchasRJ\\result11.jpg", morph_img)
            result = self.escreve_le_imagem_tesseract(morph_img)
            if len(result) == 5:
                i += 1
                print('[', i, ']', result)
                if i >= 100:
                    time.sleep(120)
                return i, result
            else:
                i += 1
                print('[', i, ']', 'Resultado inválido!!!')
                if i >= 100:
                    time.sleep(120)
                return i, result

################################################################ PARA TESTAR EM MASSA ##########################################################################

# class CaptchaSolverAcompanhamentoRJ(CaptchaSolver):
#
#     def remove_fundo(numpy_imagem):
#         ret, thresh_img = cv2.threshold(numpy_imagem, 150, 255, cv2.THRESH_BINARY)
#         kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 4))
#         morph_img = cv2.morphologyEx(thresh_img, cv2.MORPH_CLOSE, kernel)
#         return morph_img
#
#     def escreve_le_imagem_tesseract(morph_img):
#         cv2.imwrite("C:\\Users\\e7609043\\PycharmProjects\\IpeaJUS\\util\\CaptchasRJ\\result11.jpg", morph_img)
#         imagem = Image.open('C:\\Users\\e7609043\\PycharmProjects\\IpeaJUS\\util\\CaptchasRJ\\result11.jpg')
#         result = pytesseract.image_to_string(imagem, lang='eng', config="--psm 11 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz0123456789 ")
#         return result
#
#     i = 0
#     count_zeros_na_linha = 0
#     count_linhas = 0
#     col = 93
#     linha = 0
#     for file in os.listdir('CaptchasRJ\\'):
#         img = Image.open('CaptchasRJ\\{}'.format(file))
#         area = (5, 5, 135, 55)
#         imagem_recortada = img.crop(area)
#         numpy_imagem = np.asarray(imagem_recortada).astype(np.uint8)
#         morph_img = remove_fundo(numpy_imagem)
#         numpy_imagem = cv2.cvtColor(morph_img, cv2.COLOR_BGR2GRAY)
#         morph_img = remove_fundo(numpy_imagem)
#         #TODO Tentariva de limpar o traço mais grosso do meio da imagem na mão
#         while count_linhas is not 6:
#             while count_zeros_na_linha is not 30:
#                 try:
#                     if morph_img[24:30][count_linhas][col] == 255:
#                         linha += 1
#                         break
#                     else:
#                         morph_img[24:30][count_linhas][col] = 255
#                         col += 1
#                         count_zeros_na_linha += 1
#                         # cv2.imwrite("C:\\Users\\e7609043\\PycharmProjects\\IpeaJUS\\util\\CaptchasRJ\\result11.jpg", morph_img)
#                 except IndexError as e:
#                     linha += 1
#                     break
#             count_linhas += 1
#             count_zeros_na_linha = 0
#             col = 93
#             numpy_imagem = remove_fundo(morph_img)
#             cv2.imwrite("C:\\Users\\e7609043\\PycharmProjects\\IpeaJUS\\util\\CaptchasRJ\\result11.jpg", numpy_imagem)
#         count_col = 0
#         result = escreve_le_imagem_tesseract(numpy_imagem)
#
#         while i != len(os.listdir('CaptchasRJ\\')):
#             if result == file.replace('.jpeg', ''):
#                 print('{} Acertou o captcha de {}'.format(i, file))
#                 i += 1
#                 break
#             else:
#                 break
#
#             else:
#                 print('{} Errou o captcha {} usando a resposta {}'.format(i, file, result))
#                 i += 1
#                 break

##############################################################################PARA TESTAR APENAS UM CASO#####################################################################################

# class CaptchaSolverAcompanhamentoRJ(CaptchaSolver):
#
#     def remove_fundo(numpy_imagem):
#         ret, thresh_img = cv2.threshold(numpy_imagem, 150, 255, cv2.THRESH_BINARY)
#         kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 4))
#         morph_img = cv2.morphologyEx(thresh_img, cv2.MORPH_CLOSE, kernel)
#         return morph_img
#
#     def escreve_le_imagem_tesseract(morph_img):
#         cv2.imwrite("C:\\Users\\e7609043\\PycharmProjects\\IpeaJUS\\util\\CaptchasRJ\\result11.jpg", morph_img)
#         imagem = Image.open('C:\\Users\\e7609043\\PycharmProjects\\IpeaJUS\\util\\CaptchasRJ\\result11.jpg')
#         result = pytesseract.image_to_string(imagem, lang='eng', config="--psm 11 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz0123456789 ")
#         return result
#
#     i = 0
#     count_zeros_na_linha = 0
#     count_linhas = 0
#     col = 93
#     linha = 0
#
#     img = Image.open('C:\\Users\\e7609043\\PycharmProjects\\IpeaJUS\\util\\CaptchasRJ\\ykd2f.jpeg')
#     area = (5, 5, 135, 55)
#     imagem_recortada = img.crop(area)
#     numpy_imagem = np.asarray(imagem_recortada).astype(np.uint8)
#     morph_img = remove_fundo(numpy_imagem)
#     numpy_imagem = cv2.cvtColor(morph_img, cv2.COLOR_BGR2GRAY)
#     morph_img = remove_fundo(numpy_imagem)
#     #TODO Tentariva de limpar o traço mais grosso do meio da imagem na mão
#     while count_linhas is not 6:
#         while count_zeros_na_linha is not 30:
#             try:
#                 if morph_img[24:30][count_linhas][col] == 255:
#                     linha += 1
#                     break
#                 else:
#                     morph_img[24:30][count_linhas][col] = 255
#                     col += 1
#                     count_zeros_na_linha += 1
#                     cv2.imwrite("C:\\Users\\e7609043\\PycharmProjects\\IpeaJUS\\util\\CaptchasRJ\\result11.jpg", morph_img)
#             except IndexError as e:
#                 linha+=1
#                 break
#         count_linhas += 1
#         count_zeros_na_linha = 0
#         col = 93
#         # numpy_imagem = remove_fundo(morph_img)
#         y = cv2.imwrite("C:\\Users\\e7609043\\PycharmProjects\\IpeaJUS\\util\\CaptchasRJ\\result11.jpg", morph_img)
#     result = escreve_le_imagem_tesseract(morph_img)
#
#
#     if result == re.search('.{5}\.jpeg',img.filename).group(0).replace('.jpeg',''):
#         print('{} Acertou o captcha de {}'.format(i, img))
#         cv2.imshow('imagem', y)
#     else:
#         print('Erooooooooou o captcha .{} dando como resultado .{}'.format(re.search('.{5}\.jpeg',img.filename).group(0), result))
