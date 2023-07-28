# -*- coding: utf-8 -*-

import os
import math
from PIL import Image
from util.CaptchaSolver import CaptchaSolver


class CaptchaSolverTRF1(CaptchaSolver):

    def parse_captcha(self, filename):
        '''fixed = 'fix_' + os.path.split(filename)[1]
        img = Image.open(filename)
        img = img.rotate(-15)
        img.save(fixed)'''

        for f in os.listdir('.\\'):
            if f.endswith('png'):
                self.noise_filter(f, pass_factor=100)
                result = self.tesseract(f, number_only=False, whitelist='abcdefghijklmnopqrstuvwxyz012345789')
                print(result)
                #os.remove(filename)

        #return result

if __name__ == '__main__':
    agoraVai3 = CaptchaSolverTRF1()
    agoraVai3.parse_captcha('.\image.jpg')

