# -*- coding: utf-8 -*-

import os
import math
import numpy as np
import sys
from PIL import Image
from util.CaptchaSolver import CaptchaSolver as cs

from util.CaptchaSolver import CaptchaSolver


class CaptchaSolverMG(CaptchaSolver):

    def parse_captcha(self, filename):
        """Return the text for the image using Tesseract
        """
        if filename.endswith(".svl"):
            if os.path.isfile(filename):
                if os.path.isfile(filename.replace(".svl", ".bmp")):
                    os.remove(filename.replace(".svl", ".bmp"))
                os.rename(filename, filename.replace(".svl", ".bmp"))
        if ".svl" in filename:
            filename = filename.replace(".svl",".bmp")

        # answer = self.teste_repair(filename)
        cut1 = self.separate_chars(filename)

        fixed = self.fix_letter_ccw(cut1, (0, 29), (0, 39), 22)
        # bw = self.black_and_white(filename=filename, img=fixed, level=100)

        #fixed2 = self.fix_letter_ccw(fixed, (85, 109), (0, 39), 5)
        cut2 = self.separate_chars(fixed)
        img = self.threshold(cut2, min=(35, 0, 0), max=(255, 190, 190),modefilter=3)
        try:
            result = self.tesseract(img, number_only=True)

            os.remove(filename)
            os.remove(fixed)
            os.remove(img)
            os.remove(cut1)
            os.remove(cut2)
            return result

        except:
            os.remove(filename)
            os.remove(fixed)
            os.remove(img)
            os.remove(cut1)
            os.remove(cut2)
            return None





    # def ocr(self, filename, threshold=200, alphabet="0123456789"):
    #     img = Image.open (filename)
    #     img = img.convert ("RGB")
    #     box = (8, 8, 58, 18)
    #     img = img.crop (box)
    #     pixdata = img.load ()
    #
    #     letters = Image.open ('captcha.png')
    #     ledata = letters.load ()
    #
    #     # Clean the background noise, if color != white, then set to black.
    #     for y in range (img.size[1]):
    #         for x in range (img.size[0]):
    #             if (pixdata[x, y][0] > threshold) \
    #                     and (pixdata[x, y][1] > threshold) \
    #                     and (pixdata[x, y][2] > threshold):
    #
    #                 pixdata[x, y] = (255, 255, 255, 255)
    #             else:
    #                 pixdata[x, y] = (0, 0, 0, 255)
    #
    #     counter = 0
    #     old_x = -1
    #
    #     letterlist = []
    #
    #     for x in range (letters.size[0]):
    #         black = True
    #         for y in range (letters.size[1]):
    #             if ledata[x, y][0] != 0:
    #                 black = False
    #                 break
    #         if black:
    #             if True:
    #                 box = (old_x + 1, 0, x, 10)
    #                 letter = letters.crop (box)
    #                 t = (img, letter)
    #                 print (counter, x, t)
    #                 letterlist.append ((t[0], alphabet[counter], t[1]))
    #             old_x = x
    #             counter += 1
    #
    #     box = (old_x + 1, 0, 140, 10)
    #     letter = letters.crop (box)
    #     t = (img, letter)
    #     letterlist.append ((t[0], alphabet[counter], t[1]))
    #
    #     t = sorted (letterlist)
    #     t = t[0:5]  # 5-letter captcha
    #
    #     final = sorted (t, key=lambda e: e[2])
    #     answer = ''
    #     for l in final:
    #         answer = answer + l[1]
    #
    #     return answer
    # print (ocr(sys.argv[0]))

    def decoder(self, filename, threshold=200,mask="letters.bmp",alphabet="0123456789"):

        img = Image.open (filename)
        img = img.convert ("RGB")
        box = (8, 8, 58, 18)
        img = img.crop (box)
        pixdata = img.load ()

        # open the mask
        letters = Image.open (mask)
        ledata = letters.load ()

        def test_letter(img, letter):
            A = img.load ()
            B = letter.load ()
            mx = 1000000
            max_x = 0
            x = 0
            for x in range (img.size[0] - letter.size[0]):
                _sum = 0
                for i in range (letter.size[0]):
                    for j in range (letter.size[1]):
                        _sum = _sum + abs (A[x + i, j][0] - B[i, j][0])
                if _sum < mx:
                    mx = _sum
                    max_x = x
            return mx, max_x

        # Clean the background noise, if color != white, then set to black.
        for y in range (img.size[1]):
            for x in range (img.size[0]):
                if (pixdata[x, y][0] > threshold) \
                        and (pixdata[x, y][1] > threshold) \
                        and (pixdata[x, y][2] > threshold):

                    pixdata[x, y] = (255, 255, 255, 255)
                else:
                    pixdata[x, y] = (0, 0, 0, 255)

        counter = 0
        old_x = -1

        letterlist = []

        for x in range (letters.size[0]):
            black = True
            for y in range (letters.size[1]):
                if ledata[x, y][0] != 0:
                    black = False
                    break
            if black:
                box = (old_x + 1, 0, x, 10)
                letter = letters.crop (box)
                t = test_letter (img, letter)
                letterlist.append ((t[0], alphabet[counter], t[1]))
                old_x = x
                counter += 1

        box = (old_x + 1, 0, 140, 10)
        letter = letters.crop (box)
        t = test_letter (img, letter)
        letterlist.append ((t[0], alphabet[counter], t[1]))

        t = sorted (letterlist)
        t = t[0:5]  # 5-letter captcha

        final = sorted (t, key=lambda e: e[2])

        answer = ''.join (map (lambda l: l[1], final))
        return answer

    # if __name__ == '__main__':
    #     print (decoder (sys.argv[1]))
