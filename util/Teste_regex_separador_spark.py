import re
from util.StringUtil import remove_acentos, remove_varios_espacos

#regex = '(?:(?:APELACAO\s*CIVEL\s*(?:N.|\:)?\s*|PROCESSO\s*(?:N.)?\:?\s*|NUMERACAO\s*UNICA\s*:\s*)(\\\\\b\d{7}\-?\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\\\\\b\d{7}\-?\d{2}\.\d{4}\.\d{3}\.\d{4}|\\\\\b\d{3}\.\d{2}\.\d{6}\-\d|\\\\\b\d{4}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\\\\\b\d{4}\.\d{2}\.\d{2}\.\d{6}\-\d|\\\\\b\d{3}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\\\\\b\d{5}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})|\\\\\bN.\s*PROCESSO\s*:\s*(\\\\\b\d{7}\-?\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\\\\\b\d{7}\-?\d{2}\.\d{4}\.\d{3}\.\d{4}|\\\\\b\d{3}\.\d{2}\.\d{6}\-\d|\\\\\b\d{4}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\\\\\b\d{4}\.\d{2}\.\d{2}\.\d{6}\-\d|\\\\\b\d{3}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\\\\\b\d{5}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})|(\\\\\b\d{7}\-?\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\\\\\b\d{7}\-?\d{2}\.\d{4}\.\d{3}\.\d{4}|\\\\\b\d{3}\.\d{2}\.\d{6}\-\d|\\\\\b\d{4}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\\\\\b\d{4}\.\d{2}\.\d{2}\.\d{6}\-\d|\\\\\b\d{3}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\\\\\b\d{5}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})(?:(?:\s*\d+\s*)?-\s*\w+|\s*PROT\.:\d{1,2}/\d{1,2}/\d{4}\s*|\s*\d{5,}\s*\w+|[\s*\w+\s*/]+))'
regex = '(?:\sBANANA\s(?:PROCESSO\s*N..?.{0,10}\s*-\s*(\\b\d{7}\s*[\.\-]\s*?\d{2}\s*[\.\-]\s*\d{4}\s*[\.\-]\s*\d\s*[\.\-]\s*\d{2}\s*[\.\-]\s*\d{4}|\\b\d{7}\s*[\.\-]\s*?\d{2}\s*[\.\-]\s*\d{4}\s*[\.\-]\s*\d{3}\s*[\.\-]\s*\d{4}|\\b\d{3}\s*[\.\-]\s*\d{2}\s*[\.\-]\s*\d{6}\s*[\.\-]\s*\d|\\b\d{4}\s*[\.\-]\s*\d{2}\s*[\.\-]\s*\d{4}\s*[\.\-]\s*\d\s*[\.\-]\s*\d{2}\s*[\.\-]\s*\d{4}|\\b\d{4}\s*[\.\-]\s*\d{2}\s*[\.\-]\s*\d{2}\s*[\.\-]\s*\d{6}\s*[\.\-]\s*\d|\\b\d{3}\s*[\.\-]\s*\d{2}\s*[\.\-]\s*\d{4}\s*[\.\-]\s*\d\s*[\.\-]\s*\d{2}\s*[\.\-]\s*\d{4}|\\b\d{5}\s*[\.\-]\s*\d{2}\s*[\.\-]\s*\d{4}\s*[\.\-]\s*\d\s*[\.\-]\s*\d{2}\s*[\.\-]\s*\d{4}|\\b\d{7}\s*[\.\-]\s*\d\/\d|\\b\d{3}\s*[\.\-]\s*\d{2}\s*[\.\-]\s*\d{4}\s*[\.\-]\s*\d{6}\s*[\.\-]\s*\d\\b|\\b\d{3}\s*[\.\-]\s*\d{3}\s*[\.\-]\s*\d\/\d\\b)))'

file = open('/mnt/dmlocal/dados/DEJT/txt/2020/12/TRT_Judiciario_Caderno_do_TRT_da_2a_Regiao_2020_12_02.txt')

linhas = file.readlines()

linhas = ''.join(linhas).split('\n')
clean_lines = list(map(lambda linha: remove_acentos(linha).upper(), linhas))
clean_lines = list(filter(lambda linha: linha != '', list(map(lambda linha: remove_varios_espacos(re.sub('\s*\n|\t', '',linha)), clean_lines))))
clean_lines = ' BANANA '.join(clean_lines)

splited_lines = re.split(regex, clean_lines)
splited_clean_lines = list(map(lambda linha: re.sub('\sBANANA\s', ' ', linha), splited_lines))[1:]

new_lines = []

for pos, line in enumerate(splited_clean_lines):
  if pos % 2 == 0:
    try:
      new_lines.append(f'{line} {splited_clean_lines[pos+1]}')
    except:
      continue

print(new_lines)


