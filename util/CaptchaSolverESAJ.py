# -*- coding: utf-8 -*-
from util.CaptchaSolver import CaptchaSolver
from PIL import Image
import os
import operator


class CaptchaSolverESAJ(CaptchaSolver):

    def parse_captcha(self, filename):
        """Return the text for the image using Tesseract
        """
        img = None

        try:
            c = self.get_letter_color(filename)
            img = self.threshold(filename, min=(c[0]-10, c[1]-10, c[2]-10),
                                 max=(c[0]+10, c[1]+10, c[2]+10), modefilter=0)
            result = self.tesseract(img)

            os.remove(filename)
            os.remove(img)
        except Exception as ex:
            result = ''
            if os.path.isfile(filename):
                os.remove(filename)
            if img and os.path.isfile(img):
                os.remove(img)
            print(ex)

        return result


    def get_letter_color(self, filename):
        # read in colour channels
        with open(filename, 'rb') as f:
            img = Image.open(f)
            # resize to make more clearer
            m = 2
            img = img.resize((int(img.size[0]*m), int(img.size[1]*m))).convert('RGBA')
            pixdata = img.load()

            r = {}
            g = {}
            b = {}

            for y in range(img.size[1]):
                for x in range(img.size[0]):
                    if pixdata[x, y][0] < 250 or pixdata[x, y][1] < 250 or pixdata[x, y][2] < 250:
                        if pixdata[x, y][0] in r:
                            r[pixdata[x, y][0]] += 1
                        else:
                            r[pixdata[x, y][0]] = 0

                        if pixdata[x, y][1] in g:
                            g[pixdata[x, y][1]] += 1
                        else:
                            g[pixdata[x, y][1]] = 0

                        if pixdata[x, y][2] in b:
                            b[pixdata[x, y][2]] += 1
                        else:
                            b[pixdata[x, y][2]] = 0

            r_dom = sorted(list(r.items()), key=operator.itemgetter(1), reverse=True)[0]
            g_dom = sorted(list(g.items()), key=operator.itemgetter(1), reverse=True)[0]
            b_dom = sorted(list(b.items()), key=operator.itemgetter(1), reverse=True)[0]

        return r_dom[0], g_dom[0], b_dom[0]
