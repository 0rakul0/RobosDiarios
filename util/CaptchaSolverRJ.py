# -*- coding: utf-8 -*-

import os
import math
from PIL import Image
from util.CaptchaSolver import CaptchaSolver


class CaptchaSolverRJ(CaptchaSolver):

    def parse_captcha(self, filename):
        #self.noise_filter(filename, pass_factor=100)
        result = self.tesseract(filename, number_only=False)

        os.remove(filename)

        return result
