__ones__ = { 'um':   1, 'uma':   1, 'onze':     11,
             'dois':   2, 'duas':   2, 'doze':     12,
             'tres': 3, 'treze':   13,
             'quatro':  4, 'quatorze':   14,
             'cinco':  5, 'quinze':    15,
             'seis':   6, 'dezesseis':    16,
             'sete': 7, 'dezessete':  17,
             'oito': 8, 'dezoito':   18,
             'nove':  9, 'dezenove':   19 }

__tens__ = { 'vinte':  20,
             'trinta':  30,
             'quarenta':   40,
             'cinquenta':   50,
             'sessenta':   60,
             'setenta': 70,
             'oitenta':  80,
             'noventa':  90,
             'cem':     100}

__hundreds__ = { 'cento':     100,
             'duzentos':  200,
             'trezentos':  300,
             'quatrocentos':   400,
             'quinhentos':   500,
             'seiscentos':   600,
             'setecentos': 700,
             'oitocentos':  800,
             'novecentos':  900 }

__groups__ = { 'mil':  1000}

def is_num(word):
    return word in __ones__.keys() or word in __tens__.keys() or word in __hundreds__.keys() or word in __groups__.keys()

def parse_text(text):
    text = text.lower()
    conectivos = ["e", ","]
    words = text.split()
    word_with_number = ""
    result = ""
    for word in words:
        if is_num(word) or (word_with_number and word in conectivos):
            word_with_number += str(word) + " "
        else:
            num = parse(word_with_number)
            word_with_number = ""
            if num:
                result+= str(num) + " "
            result+=word + " "
    if not result and word_with_number:
        num = parse(word_with_number)
        word_with_number = ""
        if num:
            result+= str(num) + " "
    return result.strip().upper()

def parse(words):
    if not words:
        return ""
    words = words.lower()
    words = words.replace("catorze","quatorze")
    words = words.replace(" e "," ")
    words = words.replace(", "," ")
    array_w = words.split()
    result = 0
    for num in array_w:
        if num in __groups__.keys():
            if result > 0:
                result = result * __groups__.get(num)
            else:
                result = __groups__.get(num)
        else:
            if num in __hundreds__.keys():
                result = result + __hundreds__.get(num)
            if num in __tens__.keys():
                result = result + __tens__.get(num)
            if num in __ones__.keys():
                result = result + __ones__.get(num)

    return result

def calculo_dv_cnpj(cnpj):
    if 12<=len(cnpj)<=14:
        if len(cnpj) == 12:
            dv1 = 5*int(cnpj[0])+4*int(cnpj[1])+3*int(cnpj[2])+2*int(cnpj[3])+9*int(cnpj[4])+8*int(cnpj[5])+7*int(cnpj[6])+6*int(cnpj[7])+5*int(cnpj[8])+4*int(cnpj[9])+3*int(cnpj[10])+2*int(cnpj[11])
            dv1 = modulo_dv_cnpj(dv1)
            cnpj += str(dv1)
        if len(cnpj) == 13:
            dv2 = 6*int(cnpj[0])+5*int(cnpj[1])+4*int(cnpj[2])+3*int(cnpj[3])+2*int(cnpj[4])+9*int(cnpj[5])+8*int(cnpj[6])+7*int(cnpj[7])+6*int(cnpj[8])+5*int(cnpj[9])+4*int(cnpj[10])+3*int(cnpj[11])+2*int(cnpj[12])
            dv2 = modulo_dv_cnpj(dv2)
            cnpj += str(dv2)
        return cnpj
    return None

def modulo_dv_cnpj(dv):
    dv %= 11
    if dv <2:
        dv = 0
    else:
        dv = 11 - dv
    return dv