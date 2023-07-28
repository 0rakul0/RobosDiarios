
from util.RegexUtil import RegexUtil

__author__ = 'B208833301'
from unicodedata import normalize
from decimal import Decimal
import difflib,re
from datetime import datetime

def sao_iguais(parent,item,ratio=0.8):
    return difflib.SequenceMatcher(None,parent,item).ratio() >= ratio

def remove_sub_str(parent,item):
    array_parent = parent.split()
    array_item = item.split()
    total_porcentual = 0
    i= 0
    for word_item in array_item:
        porcentual_igualdade = difflib.SequenceMatcher(None,array_parent[0], word_item).ratio()
        total_porcentual = total_porcentual + porcentual_igualdade
        i = i + 1
        if porcentual_igualdade > 0.7 or (porcentual_igualdade > 0.5 and total_porcentual/i > 0.8) :
            array_parent.remove(array_parent[0])

    result = ""
    for word_parent in array_parent:
        result = result + word_parent + " "
    return result.strip()

def remove_acentos(txt):
    '''try:
        txt = txt.encode(encoding='UTF-8',errors='ignore')
    except Exception as e:
        pass
    txt = str(txt)'''
    if not txt:
        return txt
    text = str((normalize('NFKD', txt).encode("ascii",errors="ignore")).decode("utf-8",errors="ignore"))
    return text.replace("'","").replace('"',"")

def remove_varios_espacos(txt):
    array = txt.split()
    # result = ""
    # for item in array:
    #     result = result + item + " "
    # return result.strip()
    return " ".join(array).strip()


def remove_caracteres_csv(txt):
    return txt.replace(',', ' ').replace(';', ' ').replace('\"', ' ').replace('\'', ' ')

def range_da_semana(ano,semana):
    data = str(ano)+'_'+str(semana)+'_'
    inicio = datetime.strptime(data+'1','%W_%Y_%w').strftime('%d/%m/%Y')
    final = datetime.strptime(data+'0','%W_%Y_%w').strftime('%d/%m/%Y')
    return inicio, final

def remove_tracos_pontos_barras_espacos(txt):
    return txt.replace('.','').replace('-','').replace('/','').replace(' ','')

def possui_numeros(inputString):
    return any(char.isdigit() for char in inputString)

def remove_espaco_e_pontuacao(txt):
    return remove_pontuacao(txt).replace(' ','')

def remove_parenteses(txt):
    return txt.replace('(','').replace(')','')

def remove_parenteses_e_pontuacao(txt):
    return remove_pontuacao(remove_parenteses(txt))

def remove_pontuacao(txt):
    return txt.replace(',', '').replace(';', '').replace('\"', '').replace('\'', '').replace('.','').replace('-','').\
        replace('/','').replace('?','').replace('$','').replace('!','').replace('—','').replace('–','').replace(':','').replace('\\','')

def extrai_decimal(input):
    str = input
    if "," in str:
        str = str.replace(".","")
        str = str.replace(",",".")
    result = 0.0
    for i in str:
        if not i.isdigit() and not i == ".":
            str = str.replace(i,"")
    result = Decimal(str.strip())
    return result

def remove_links(linha):
    # linha_cortada = linha.split(')')
    # if linha_cortada:
    #     expressao_site = re.compile('\[((\w*\.*\-*)*)\](\(.*)',re.UNICODE)
    #     for i in range (0,len(linha_cortada)):
    #         site_match = re.search(expressao_site,linha_cortada[i])
    #         if site_match:
    #             linha_cortada[i] = linha_cortada[i].replace(site_match.group(0),site_match.group(1))
    #         elif i<len(linha_cortada) -1:
    #             linha_cortada[i] = linha_cortada[i] + ')'
    #     linha_final = ''
    #     for i in range (0,len(linha_cortada)):
    #         linha_final = linha_final+linha_cortada[i]
    #     return linha_final

    linha = re.sub('\<.*?\>','',linha)
    linha = re.sub('([-a-zA-Z0-9@:%_\+.~#?&\/=]*)[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/=;]*)','',linha)

    return linha.strip()

def replace_last(source_string, replace_what, replace_with):
    head, sep, tail = source_string.rpartition(replace_what)
    return head + replace_with + tail

def remove_quebras_linha_de_linha(texto):
    return texto.replace('\n', ' ').replace('\r', '').strip()

def recupera_tipo_empresa(nome):
    tipo = []

    nome = remove_varios_espacos(nome.replace('.', ' ').strip())
    nome = re.sub('-.*?REC.*?JUD.*', '', nome).strip()
    nome = re.sub('-.*?MASS.*?FAL.*', '', nome).strip()

    if nome.endswith(' ME'):
        tipo.append('ME')
    if nome.endswith('EPP'):
        tipo.append('EPP')

    if nome.endswith('LTDA') or ((nome.endswith('ME') or nome.endswith('EPP')) and 'LTDA' in nome):
        tipo.append('LTDA')
    if nome.endswith('SA') or 'S/A' in nome or ' S A ' in nome:
        tipo.append('SA')
    if nome.endswith('MEI'):
        tipo.append('MEI')

    return tipo

def normaliza_tipo_empresa(nome):
    nome = remove_varios_espacos(nome.replace('.', '').strip())
    nome = re.sub('-.*?REC.*?JUD.*', '', nome).strip()
    nome = re.sub('-.*?MASS.*?FAL.*', '', nome).strip()

    nome = nome.replace('S/A', 'SA').replace(' S A ', 'SA')
    nome = re.sub('LTDA.*?M\.?E\.?', 'LTDA ME', nome)
    nome = re.sub('LTDA.*?E\.?P\.?P\.?', 'LTDA ME', nome)

    return nome

def iniciais_palavra(palavra):
    iniciais = []

    palavra = remove_varios_espacos(palavra).upper().strip()

    for parte in palavra.split(' '):
        parte = parte.strip()

        if parte != '':
            iniciais.append(parte[0])

    return iniciais

def encontra_primeira_letra(s):
    i = re.search("[A-Za-z]", s, re.IGNORECASE)
    return -1 if i == None else i.start()

def corrige_nome(nome):
    nome_corrigido = nome
    regex_util = RegexUtil()
    for regex in regex_util.nome_corrigido_regex:

        nome_corrigido = regex[0].sub(regex[1],nome_corrigido)

    return nome_corrigido

def corrige_nome_classe(nome):
    regex_util = RegexUtil()
    for regex in regex_util.nome_classe_corrigido_regex:
        if regex[0].search(nome):
            return regex[1]

def remove_caracteres_especiais(nome):
    nome_corrigido = nome
    nome_corrigido = re.sub('[\\\/,;<>\.\?\/\!\*\-\+\_\=\@\#%:\(\)'']+', '', nome_corrigido)
    nome_corrigido = re.sub('\(\)', '', nome_corrigido)
    nome_corrigido = re.sub('\s{2,}', ' ', nome_corrigido)
    nome_corrigido = re.sub('^\s+', '', nome_corrigido)
    nome_corrigido = re.sub('\s+$', '', nome_corrigido)
    return nome_corrigido

def remove_caracteres_especiais_para_quadro(nome):
    nome_corrigido = nome
    nome_corrigido = re.sub('\s{2,}', ' ', nome_corrigido)
    nome_corrigido = re.sub('^\s+', '', nome_corrigido)
    nome_corrigido = re.sub('\s+$', '', nome_corrigido)
    return nome_corrigido

def abrevia_nome(nome):
    nome_abreviado = nome
    regex_util = RegexUtil()

    for regex in regex_util.nome_abreviado_regex:
        nome_abreviado = regex[0].sub(regex[1], nome_abreviado)

    nome_abreviado = remove_varios_espacos(nome_abreviado.strip())
    return nome_abreviado

def acerta_valor_string_para_decimal(valor):
    if not valor[-1].isdigit() :
        valor = valor[:-1]
    ultimo_ponto = valor.rfind('.')
    ultima_virgula = valor.rfind(',')
    ultimo_digito = max(ultima_virgula,ultimo_ponto)
    inteiro = valor[:ultimo_digito]
    centavos = valor[ultimo_digito+1:]
    inteiro = inteiro.replace('.','').replace(',','')
    return Decimal(inteiro+'.'+centavos)