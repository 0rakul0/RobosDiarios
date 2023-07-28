# -*- coding: utf-8 -*-
import re
from pdjus.service.EmpresaService import EmpresaService
from pdjus.service.ParteService import ParteService
from util.StringUtil import remove_espaco_e_pontuacao
from util.ConfigManager import ConfigManager
import csv

#tenta encontrar num dado movimento o par nome e CNPJ do falido/recuperando
def procura_empresa_no_movimento(movimento, acompanhamento):
    if not movimento.texto:
        return
    empresa_service = EmpresaService()
    parte_service = ParteService()
    impressao = ''
    encontrou_parte = False
    # ConfigManager().escreve_log(movimento.texto,acomp.nome,'nome_cnpj_sem_erro.txt')
    regex_cnpj = re.compile('(\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2})')
    regex_cnpj_nome_valor = re.compile('(\d{2}\.\d{3}\.\d{3}[\/\.]\d{4}\-\d{2})[,\-\s\.]*([A-Z]([A-Z]|\s[A-Z]|\.\s?[A-Z]).*?)')
    cnpjs_matches = [ match for match in regex_cnpj.finditer(movimento.texto)]
    for index, match in enumerate(cnpjs_matches):
        if index > 0 and cnpjs_matches[index-1].end()> abs(match.start()-200):
            before = cnpjs_matches[index-1].end()
        else:
            before = match.start()-200 if match.start()-200 > 0 else 0
        texto_com_nome_cnpj = movimento.texto[before:match.end()]
        texto_encurtado_com_nome_cnpj = remove_espaco_e_pontuacao(texto_com_nome_cnpj)
        provaveis_partes = []
        for parte in movimento.processo.partes:
            if remove_espaco_e_pontuacao(parte.nome) != '' :
                if parte.nome in texto_com_nome_cnpj or (remove_espaco_e_pontuacao(parte.nome_abreviado) != '' and remove_espaco_e_pontuacao(parte.nome_abreviado) in texto_encurtado_com_nome_cnpj) or (remove_espaco_e_pontuacao(parte.nome_corrigido) != '' and remove_espaco_e_pontuacao(parte.nome_corrigido) in texto_encurtado_com_nome_cnpj):
                    provaveis_partes.append(parte)
        if len(provaveis_partes) >= 1: #caso tenha mais de 1 parte no match, atribuir o cnpj para a parte mais próxima
            parte_correta = None
            for provavel_parte in provaveis_partes:
                if provavel_parte.nome in texto_com_nome_cnpj:
                    posicao_provavel_parte = texto_com_nome_cnpj.index(provavel_parte.nome)
                    nome_provavel_parte = provavel_parte.nome
                elif remove_espaco_e_pontuacao(provavel_parte.nome_corrigido) in remove_espaco_e_pontuacao(texto_encurtado_com_nome_cnpj):
                    posicao_provavel_parte = texto_encurtado_com_nome_cnpj.index(remove_espaco_e_pontuacao(provavel_parte.nome_corrigido))
                    nome_provavel_parte = provavel_parte.nome_corrigido
                else:
                    posicao_provavel_parte =  texto_encurtado_com_nome_cnpj.index(remove_espaco_e_pontuacao(provavel_parte.nome_abreviado))
                    nome_provavel_parte = provavel_parte.nome_abreviado
                if not parte_correta:
                    if ((nome_provavel_parte in texto_com_nome_cnpj and texto_com_nome_cnpj.index(match.group(1)) > texto_com_nome_cnpj.index(nome_provavel_parte))\
                    or (remove_espaco_e_pontuacao(nome_provavel_parte) in texto_encurtado_com_nome_cnpj and texto_com_nome_cnpj.index(match.group(1)) > texto_encurtado_com_nome_cnpj.index(remove_espaco_e_pontuacao(nome_provavel_parte)))):
                        parte_correta = provavel_parte
                else:
                    if parte_correta.nome in texto_com_nome_cnpj:
                        posicao_parte_correta =  texto_com_nome_cnpj.index(parte_correta.nome)
                    elif remove_espaco_e_pontuacao(parte_correta.nome_abreviado) in texto_encurtado_com_nome_cnpj:
                        posicao_parte_correta = texto_encurtado_com_nome_cnpj.index(remove_espaco_e_pontuacao(parte_correta.nome_abreviado))
                    else:
                        continue
                    if ((provavel_parte.nome in texto_com_nome_cnpj and
                            texto_com_nome_cnpj.index(match.group(1)) > posicao_provavel_parte
                            > posicao_parte_correta) or
                        (remove_espaco_e_pontuacao(provavel_parte.nome_abreviado) in texto_encurtado_com_nome_cnpj and
                            texto_com_nome_cnpj.index(match.group(1))
                            > posicao_provavel_parte
                            > posicao_parte_correta)):
                        parte_correta = provavel_parte
            if parte_correta:
                empresa = empresa_service.preenche_empresa(match.group(1),parte_correta.nome,soma_ocorrencias=True)

                if not parte_correta.empresa:
                    parte_correta.empresa = empresa
                    parte_service.salvar(parte_correta)
                    impressao = impressao + 'Parte: {} - CNPJ {}.\n'.format(parte_correta.nome,match.group(1))
                else:
                    impressao = impressao + 'Relação EMPRESA - PARTE já havia sido identificada para o CNPJ {}\n'.format(match.group(1))
                encontrou_parte = True
                # ConfigManager().escreve_log('Parte: {} - CNPJ {}'.format(parte_correta.nome,match.group(1)),acomp.nome,'nome_cnpj_sem_erro.txt')
    if encontrou_parte and impressao != '':
        ConfigManager().escreve_log(impressao, acompanhamento,'nome_cnpj_SEM_NENHUM_erro.txt')


def cria_empresas_a_partir_de_csv(arquivo):
    empresa_service = EmpresaService()
    with open(arquivo, 'r') as arq_csv:
        csv_processos = csv.DictReader(arq_csv, delimiter=';')
        for linha in csv_processos:
            nome = linha['nome_banco']
            cnpj = linha['cnpj']
            empresa = empresa_service.preenche_empresa(cnpj,nome)
            print('EMPRESA {} do CNPJ {} SALVA - id {}'.format(empresa.nome,empresa.cnpj, empresa.id))

# Executando o teste
# from pdjus.dal.MovimentoDao import MovimentoDao
# acomp = AcompanhamentoProcessualDJSP()
# movs = MovimentoDao().listar_movimentos_com_cnpj()
# # procura_empresa_no_movimento(movs[9])
# for mov in movs:
#     # if mov.processo.npu == '02334936820068260100':
#     procura_empresa_no_movimento(mov,acomp)

# cria_empresas_a_partir_de_csv('..\\Instituicoes_financeiras.csv')

#
# from pdjus.dal.RaisDao import RaisDao
# from pdjus.dal.ParteDao import ParteDao
# # rdao = RaisDao()
# pdao = ParteDao()
# partes_rais = processoService.dao.listar()
# for p in partes_rais:
#     p.nome = p.nome
#     print("Atualizou o nome de PARTE {}".format(p.nome))
#     processoService.dao.salvar(p)

#from acompanhamento_processual.AcompanhamentoProcessualDJSP import AcompanhamentoProcessualDJSP

# from pdjus.service.MovimentoService import MovimentoService
# #asp = AcompanhamentoProcessualDJSP()
# mov_service = MovimentoService()
# movimento = mov_service.dao.get_por_id(68807192)
# procura_empresa_no_movimento(movimento,None)
# print('FIM')