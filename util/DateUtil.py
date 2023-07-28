from datetime import timedelta

mes_ext = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6:'Junho', 7:'Julho', 8:'Agosto', 9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'}

mes_ext_abv = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}

def parse_mes_por_extenso_abv(mes):
    return mes_ext_abv[int(mes)]

def parse_mes_por_extenso(mes):
    return mes_ext[mes]

def parse_mes_abv_para_num(mes):
    for k,v in mes_ext_abv.items():
        if v.lower() == mes.lower():
            return k

def parse_mes_para_num(mes):
    for k,v in mes_ext.items():
        if v.lower() == mes.lower():
            return k

def daterange(start_date, end_date): # inclusive range
    for n in range(int ((end_date - start_date).days +1)):
        yield start_date + timedelta(n)