# -*- coding: utf-8 -*-

import os
import re
import subprocess
from subprocess import Popen, PIPE, STDOUT
import math
import abc

import sys
from PIL import Image, ImageFilter
import pytesseract


class CaptchaSolver(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def parse_captcha(self, filename):
        return

    def threshold(self, filename, min=(35, 0, 0), max=(255, 190, 190), modefilter=6):
        # read in colour channels
        img = Image.open(filename)
        # resize to make more clearer
        m = 2
        img = img.resize((int(img.size[0]*m), int(img.size[1]*m))).convert('RGBA')
        pixdata = img.load()

        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if pixdata[x, y][0] <= max[0] and pixdata[x, y][1] <= max[1] and pixdata[x, y][2] <= max[2]\
                        and pixdata[x, y][0] >= min[0] and pixdata[x, y][1] >= min[1] and pixdata[x, y][2] >= min[2]:
                    # make dark color black
                    pixdata[x, y] = (0, 0, 0, 255)
                else:
                    # make light color white
                    pixdata[x, y] = (255, 255, 255, 255)

        outp = os.path.join(os.path.split(filename)[0], 'threshold_' + os.path.split(filename)[1])
        img.save(outp)

        #self.mode_filter(outp, modefilter)

        #self.chop(1, 'tmp/threshold_' + filename, 'tmp/threshold_' + filename)

        return outp # convert image to single channel greyscale

    def mode_filter(self, filename, modefilter=6):
        imgf = Image.open(filename)
        #imgf = imgf.filter(ImageFilter.)
        imgf = imgf.filter(ImageFilter.ModeFilter(modefilter))
        imgf = imgf.convert('L')
        new_file = os.path.join(os.path.dirname(filename),'CP_'+os.path.basename(filename))
        imgf.save(new_file)
        return new_file

    def remove_noise(self,filename,chop):
        image = Image.open(filename).convert('1')

        width, height = image.size
        data = image.load()

        # Iterate through the rows.
        for y in range(height):
            for x in range(width):

                # Make sure we're on a dark pixel.
                if data[x, y] > 128:
                    continue

                # Keep a total of non-white contiguous pixels.
                total = 0

                # Check a sequence ranging from x to image.width.
                for c in range(x, width):

                    # If the pixel is dark, add it to the total.
                    if data[c, y] < 128:
                        total += 1

                    # If the pixel is light, stop the sequence.
                    else:
                        break

                # If the total is less than the chop, replace everything with white.
                if total <= chop:
                    for c in range(total):
                        data[x + c, y] = 255

                # Skip this sequence we just altered.
                x += total

        # Iterate through the columns.
        for x in range(width):
            for y in range(height):

                # Make sure we're on a dark pixel.
                if data[x, y] > 128:
                    continue

                # Keep a total of non-white contiguous pixels.
                total = 0

                # Check a sequence ranging from y to image.height.
                for c in range(y, height):

                    # If the pixel is dark, add it to the total.
                    if data[x, c] < 128:
                        total += 1

                    # If the pixel is light, stop the sequence.
                    else:
                        break

                # If the total is less than the chop, replace everything with white.
                if total <= chop:
                    for c in range(total):
                        data[x, y + c] = 255

                # Skip this sequence we just altered.
                y += total

        new_file = os.path.join(os.path.dirname(filename), 'CP_CP' + os.path.basename(filename))
        image.save(new_file)
        return new_file

    def chop(self, chop, input, output):
        image = Image.open(input).convert('1')
        width, height = image.size
        data = image.load()

        # Iterate through the rows.
        for y in range(height):
            for x in range(width):

                # Make sure we're on a dark pixel.
                if data[x, y] > 128:
                    continue

                # Keep a total of non-white contiguous pixels.
                total = 0

                # Check a sequence ranging from x to image.width.
                for c in range(x, width):

                    # If the pixel is dark, add it to the total.
                    if data[c, y] < 128:
                        total += 1

                    # If the pixel is light, stop the sequence.
                    else:
                        break

                # If the total is less than the chop, replace everything with white.
                if total <= chop:
                    for c in range(total):
                        data[x + c, y] = 255

                # Skip this sequence we just altered.
                x += total


        # Iterate through the columns.
        for x in range(width):
            for y in range(height):

                # Make sure we're on a dark pixel.
                if data[x, y] > 128:
                    continue

                # Keep a total of non-white contiguous pixels.
                total = 0

                # Check a sequence ranging from y to image.height.
                for c in range(y, height):

                    # If the pixel is dark, add it to the total.
                    if data[x, c] < 128:
                        total += 1

                    # If the pixel is light, stop the sequence.
                    else:
                        break

                # If the total is less than the chop, replace everything with white.
                if total <= chop:
                    for c in range(total):
                        data[x, y + c] = 255

                # Skip this sequence we just altered.
                y += total

        image.save(output)

    def change_contrast(self, filename, level):
        img = Image.open(filename)

        factor = (259 * (level + 255)) / (255 * (259 - level))

        def contrast(c):
            return 128 + factor * (c - 128)

        img = img.point(contrast)
        img.save(filename)

    def black_and_white(self, img, filename, level):
        if not img:
            img = Image.open(filename)

        def bw(c):
            return 0 if c <= level else 255

        img = img.point(bw)
        new_file = os.path.join(os.path.dirname(filename), 'CP_' + os.path.basename(filename))
        img.save(new_file)
        return new_file

    def noise_filter(self, filename, pass_factor):
        """Transform image to greyscale and blur it"""
        img = Image.open(filename)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        if 'L' != img.mode:
            img = img.convert('L')
        img = self.__remove_noise(img, pass_factor)
        img.save(filename)

    def __remove_noise(self, img, pass_factor):
        for column in range(img.size[0]):
            for line in range(img.size[1]):
                value = self.__remove_noise_by_pixel(img, column, line, pass_factor)
                img.putpixel((column, line), value)
        return img

    def __remove_noise_by_pixel(self, img, column, line, pass_factor):
        if img.getpixel((column, line)) < pass_factor:
            return (0)
        return (255)

    def call_command(self, *args):
        """call given command arguments, raise exception if error, and return output
        """
        #bloqueia popup de telas do prompt de comando
        #CREATE_NO_WINDOW = 0x08000000
        CREATE_NO_WINDOW= None
        if "win" in sys.platform.lower():
            #CREATE_NO_WINDOW = None
            linha = ""
            for arg in args:
                linha += arg + " "
            args = linha.strip()

        if CREATE_NO_WINDOW:
            c = Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,creationflags = CREATE_NO_WINDOW)
        else:
            c = Popen(' '.join(args).replace('////','/').replace('//','/').strip(), stdout=PIPE, stderr=PIPE, shell=True)
        output, error = c.communicate()
        if c.returncode != 0:
            if error:
                print(error)
            print("Error running `%s'" % ' '.join(args))
        return output


    def tesseract(self, filename, number_only=False, whitelist=None, use_lstm=True):
        """Decode image with Tesseract
        """
        # create temporary file for tiff image required as input to tesseract

        # perform OCR
        output_filename = filename.replace(os.path.splitext(filename)[1], '.txt')

        oem = '-oem 2'

        if not use_lstm:
            oem = '-oem 0'


        if number_only:
            self.call_command('tesseract ', filename, output_filename.replace('.txt', ''), "nobatch", "digits", "-psm 7", oem)
        elif whitelist:
            self.call_command('tesseract ', filename, output_filename.replace('.txt', ''), "-psm 7", oem, "-c tessedit_char_whitelist=" + whitelist)
        else:
            self.call_command('tesseract ', filename,output_filename.replace('.txt', ''), "-psm 7",oem)

        # read in result from output file
        result = open(output_filename).read()
        os.remove(output_filename)
        return self.clean(result)

    def pytesseract(self, filename, number_only=False, whitelist=None, use_lstm=True):
        """Decode image with pyTesseract
        """
        imagem = Image.open(filename)

        oem = '-oem 2'

        if not use_lstm:
            oem = '-oem 0'

        if number_only:
            return pytesseract.image_to_string(Image.open(imagem),config="digits -psm 7 {oem}".format(whitelist=whitelist, oem=oem))
        elif whitelist:
            return pytesseract.image_to_string(Image.open(imagem),
                                        config="-c tessedit_char_whitelist={witelist}} -psm 7 {oem}".format(whitelist=whitelist,oem=oem))
        else:
            return pytesseract.image_to_string(Image.open(imagem),config="-psm 7 {oem}".format(whitelist=whitelist, oem=oem))


    def clean(self, s):
        """Standardize the OCR output
        """
        # remove non-alpha numeric text
        return re.sub('[\W]', '', s)

    def separate_chars(self, filename, cuts=(30, 31, 32, 43, 44, 65, 66, 84, 85)):
        img = Image.open(filename)

        pixdata = img.load()

        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if x in cuts:
                    pixdata[x, y] = (255, 255, 255, 255)

        outp = os.path.join(os.path.split(filename)[0], 'cut_' + os.path.split(filename)[1])
        img.save(outp)

        return outp

    def _is_in_line(self,pixdata,x,y):
        if pixdata[x, y] == pixdata[x - 1, y] or \
            pixdata[x, y] == pixdata[x + 1, y] or \
            pixdata[x, y] == pixdata[x - 1, y-1] or \
            pixdata[x, y] == pixdata[x + 1, y-1] or \
            pixdata[x, y] == pixdata[x - 1, y + 1] or \
            pixdata[x, y] == pixdata[x + 1, y + 1]:
            return True
        else:
            return False

    def _calculate_first_y_black(self,img,pixdata,x):
        for y in range(img.size[1]):
            if pixdata[x, y] == (0, 0, 0, 255):
                return y
        return math.inf

    def try_align_chars(self, filename, cuts=[(1,10),(20,30),(40,60),(70,80)]):
        img = Image.open(filename)

        pixdata = img.load()

        init_letter = {}
        clone_pixdata = {}
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                clone_pixdata[x,y] = pixdata[x, y]
                if not x in init_letter.keys() and pixdata[x, y] == (0, 0, 0, 255):
                    min_y = y
                    if self._is_in_line(pixdata,x,y):
                        for z in range(x+1,img.size[0]):
                            novo_min = self._calculate_first_y_black(img,pixdata,z)
                            if min_y > novo_min:
                                min_y = novo_min
                            elif pixdata[z,min_y] == (255, 255, 255, 255):
                                break


                    init_letter[x] = min_y


        for x in range(img.size[0]):
            z =0
            for y in range(img.size[1]):
                if y < 5 or not x in init_letter.keys():
                    pixdata[x, y] = (255, 255, 255, 255)
                else:
                    if y+init_letter[x] < img.size[1]:
                        print(x, y)
                        pixdata[x, y] = clone_pixdata[x,init_letter[x]+z]
                        z+=1
                    else:
                        print(x, y)
                        z=0
                        pixdata[x, y] = (255, 255, 255, 255)



        outp = os.path.join(os.path.split(filename)[0], 'cut_' + os.path.split(filename)[1])
        img.save(outp)

        return outp

    def clean_box(self, filename):
        img = Image.open(filename)

        pixdata = img.load()

        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if self._is_border(img,x,y):
                    pixdata[x, y] = (255, 255, 255, 255)

        outp = os.path.join(os.path.split(filename)[0], 'clean_box_' + os.path.split(filename)[1])
        img.save(outp)

        return outp

    def _is_border(self,img,x,y):
        return True if x == 0 or y == 0 or x == img.size[0]-1 or y == img.size[1]-1 else False

    def fix_letter_ccw(self, filename, boundsx, boundsy, angle):
        img = Image.open(filename)

        pixdata = img.load()

        for y in range(boundsy[1], boundsy[0], - 1):
            for x in range(boundsx[0], boundsx[1]):
                ny = int(y - math.sin(math.radians(angle)) * (boundsx[1] - x))

                if ny > boundsy[1]:
                    ny = boundsy[1]

                if ny > 0:
                    pixdata[x, y] = pixdata[x, ny]
                else:
                    pixdata[x, y] = (255, 255, 255, 255)

        avg_diff = int(math.sin(math.radians(angle)) * ((boundsx[1] + boundsx[0]) / 2))

        for y in range(boundsy[0], boundsy[1]):
            for x in range(boundsx[0], boundsx[1]):
                ny = y + avg_diff

                if ny > boundsy[1]:
                    ny = boundsy[1]
                elif ny < 0:
                    ny = 0

                pixdata[x, y] = pixdata[x, ny]

        outp = os.path.join(os.path.split(filename)[0], 'fix_' + os.path.split(filename)[1])
        img.save(outp)

        return outp

    def fix_letter_cw(self, filename, boundsx, boundsy, angle):
        img = Image.open(filename)

        pixdata = img.load()

        for y in range(boundsy[0], boundsy[1]):
            for x in range(boundsx[0], boundsx[1]):
                ny = int(y - math.sin(math.radians(angle)) * (x - boundsx[0]))

                if ny > boundsy[1]:
                    ny = boundsy[1]

                if ny > 0:
                    pixdata[x, y] = pixdata[x, ny]
                else:
                    pixdata[x, y] = (255, 255, 255, 255)

        avg_diff = int(math.sin(math.radians(angle)) * ((boundsx[1] + boundsx[0]) / 2))

        for y in range(boundsy[0], boundsy[1]):
            for x in range(boundsx[0], boundsx[1]):
                ny = y - avg_diff

                if ny > boundsy[1]:
                    ny = boundsy[1]
                elif ny < 0:
                    ny = 0

                pixdata[x, y] = pixdata[x, ny]

        outp = os.path.join(os.path.split(filename)[0], 'fix_' + os.path.split(filename)[1])
        img.save(outp)

        return outp




if __name__ == '__main__':
    c = CaptchaSolver()
    filename = "C:\\Users\\b120558711\\Pictures\\0101.png"
    imagem = c.clean_box(filename=filename)
    filename = "C:\\Users\\b120558711\\Pictures\\clean_box_0101.png"
    imagem = c.try_align_chars(filename=filename)
    #imagem = c.remove_noise(imagem, chop=0)

