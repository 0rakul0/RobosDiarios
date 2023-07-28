# # -*- coding: utf-8 -*-
#
# __author__ = 'B249025230'
# import re
# from pdjus.modelo.Movimento import Movimento
# from pdjus.modelo.Processo import Processo
# from pdjus.dal.AdvogadoDao import AdvogadoDao
# from pdjus.service.ProcessoService import ProcessoService
# from pdjus.dal.ParteDao import ParteDao
# from pdjus.dal.ParteProcessoDao import ParteProcessoDao
# from util.StringUtil import abrevia_nome,corrige_nome, remove_espaco_e_pontuacao
# from util.ConfigManager import ConfigManager
# from acompanhamento_processual.AcompanhamentoProcessualDJSP import AcompanhamentoProcessualDJSP
# from acompanhamento_processual.AcompanhamentoProcessualBase import AcompanhamentoProcessualBase
#
#
# def corrige_curesp(parteProcesso):
#     if 'CURESP:' in parteProcesso.parte.nome:
#         print('Corrigindo CURESP de : {}'.format(parteProcesso.parte.nome))
#         acompbase = AcompanhamentoProcessualBase("DJSP", 'log_corrige_curesp.txt','erro_corrige_curesp.txt')
#         nome_adv = parteProcesso.parte.nome.split('CURESP:')
#         advogados = nome_adv[1:]
#         if len(advogados) > 0:
#             parteProcesso.parte.nome = nome_adv[0].strip() #atualizando o nome do cliente do curesp
#             acompbase.insere_advogados_na_parte_processo(advogados,AdvogadoDao(),parteProcesso)
#             ParteProcessoDao().salvar(parteProcesso)
#     else:
#         print('Não tem curesp em:  {}'.format(parteProcesso.parte.nome))
#
# partes = ParteDao().list_por_nome_like('CURESP:')
# for parte in partes:
#     for parte_processo in parte.partes_processo:
#         corrige_curesp(parte_processo)
