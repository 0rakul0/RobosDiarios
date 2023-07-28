## USAR O VARREDOR!!!!


# from pdjus.modelo.Caderno import Caderno
# from pdjus.service.ArquivoService import ArquivoService
# from pdjus.service.CadernoService import CadernoService
# from pdjus.service.DiarioService import DiarioService
# from util.FileManager import FileManager
#
# __author__ = 'B249025230'
# import os
# import shutil
# from pdjus.dal.ArquivoDao import ArquivoDao
# from datetime import datetime
# import re
#
# def mkdir_recursive( path):
#     print('Criando diretório {}'.format(path))
#     sub_path = os.path.dirname(path)
#     if not os.path.exists(sub_path):
#         mkdir_recursive(sub_path)
#     if not os.path.exists(path):
#         os.mkdir(path)
#
# def move_arquivos_para_pasta_correta(path='.'):
#     print('Estou no path {}'.format(path))
#     arquivos = os.listdir(path)
#     expressao_ano_mes_dia = re.compile('.*_(\d{4})_(\d{2})_\d{2}')
#
#     for arquivo in arquivos:
#         #Verificacao apenas para evitar erros bobos
#         if arquivo.endswith('.pdf') or arquivo.endswith('.txt') or arquivo.endswith('.html') or arquivo.endswith('.rtf'):
#             if arquivo.endswith('.pdf'):
#                 destino_inicial = os.path.join(path,'../pdf')
#             if arquivo.endswith('.txt'):
#                 destino_inicial = os.path.join(path,'../txt')
#             if arquivo.endswith('.rtf'):
#                 destino_inicial = os.path.join(path,'../rtf')
#             if arquivo.endswith('.html'):
#                 destino_inicial = os.path.join(path,'../html')
#             match = expressao_ano_mes_dia.search(arquivo)
#             if not match:
#                 print('{} problema com match, adicionando na pasta sem_data'.format(arquivo))
#                 destino_final = os.path.join(destino_inicial,'sem_data')
#             else:
#                 ano = match.group(1)
#                 mes = match.group(2)
#                 destino_final = os.path.join(destino_inicial,'{}/{}/'.format(ano,mes))
#             print('movendo o arquivo {} para {}'.format(os.path.join(path,arquivo),destino_final))
#             if not os.path.isdir(destino_final):
#                 mkdir_recursive(destino_final)
#             if not os.path.isfile(os.path.join(destino_final,arquivo)):
#                 shutil.move(os.path.join(path,arquivo),destino_final)
#                 print('MOVIDO!')
#             else:
#                 print('o {} já existe', arquivo)
#                 os.remove(os.path.join(path,arquivo))
#     if not os.listdir(path):
#         print('Removendo {}'.format(path))
#         shutil.rmtree(path)
#
#
# def movimentacao_pastas_padrao(caminho):
#
#     caminho_a_converter = os.path.join(caminho, 'pdf_a_converter')
#     if os.path.isdir(caminho_a_converter):
#         move_arquivos_para_pasta_correta(caminho_a_converter)
#     else:
#         print('Não existe {}'.format(caminho_a_converter))
#
#     caminho_pdf_repositorio = os.path.join(caminho, 'pdf_repositorio')
#     if os.path.isdir(caminho_pdf_repositorio):
#         move_arquivos_para_pasta_correta(caminho_pdf_repositorio)
#     else:
#         print('Não existe {}'.format(caminho_pdf_repositorio))
#
#     caminho_a_extrair = os.path.join(caminho, 'txt_a_extrair')
#     if os.path.isdir(caminho_a_extrair):
#         move_arquivos_para_pasta_correta(caminho_a_extrair)
#     else:
#         print('Não existe {}'.format(caminho_a_extrair))
#
#     caminho_txt_repositorio = os.path.join(caminho, 'txt_repositorio')
#     if os.path.isdir(caminho_txt_repositorio):
#         move_arquivos_para_pasta_correta(caminho_txt_repositorio)
#     else:
#         print('Não existe {}'.format(caminho_txt_repositorio))
#
#     caminho_html_repositorio = os.path.join(caminho, 'html_repositorio')
#     if os.path.isdir(caminho_html_repositorio):
#         move_arquivos_para_pasta_correta(caminho_html_repositorio)
#     else:
#         print('Não existe {}'.format(caminho_html_repositorio))
#
#     caminho_html_a_converter= os.path.join(caminho, 'html_a_converter')
#     if os.path.isdir(caminho_html_a_converter):
#         move_arquivos_para_pasta_correta(caminho_html_a_converter)
#     else:
#         print('Não existe {}'.format(caminho_html_a_converter))
#
#     caminho_rtf_repositorio = os.path.join(caminho, 'rtf_repositorio')
#     if os.path.isdir(caminho_rtf_repositorio):
#         move_arquivos_para_pasta_correta(caminho_rtf_repositorio)
#     else:
#         print('Não existe {}'.format(caminho_rtf_repositorio))
#
#     caminho_rtf_a_converter= os.path.join(caminho, 'rtf_a_converter')
#     if os.path.isdir(caminho_rtf_a_converter):
#         move_arquivos_para_pasta_correta(caminho_rtf_a_converter)
#     else:
#         print('Não existe {}'.format(caminho_rtf_a_converter))
#
#     caminho_zip= os.path.join(caminho, 'zip')
#     if os.path.isdir(caminho_zip):
#         move_arquivos_para_pasta_correta(caminho_zip)
#     else:
#         print('Não existe {}'.format(caminho_zip))
#
#
# def percorre_path_para_encontrar_arquivos(path):
#     diretorios_primeiro_nivel = os.listdir(path) #[RJ,RS,DOU]
#
#     for dir1 in diretorios_primeiro_nivel:
#         caminho_primeiro_nivel = os.path.join(path,dir1) #PATH/DOU, PATH/RJ
#         if os.path.isdir(caminho_primeiro_nivel):
#             diretorios_segundo_nivel = os.listdir(caminho_primeiro_nivel) #DJRJ,DJRS
#
#             if('pdf_a_converter' in diretorios_segundo_nivel or 'pdf_repositorio' in diretorios_segundo_nivel or
#                 'txt_a_extrair' in diretorios_segundo_nivel or 'txt_repositorio' in diretorios_segundo_nivel or
#                 'html_repositorio' in diretorios_segundo_nivel or 'html_a_converter' in diretorios_segundo_nivel or
#                 'rtf_repositorio' in diretorios_segundo_nivel or 'rtf_a_converter' in diretorios_segundo_nivel or
#                 'zip' in diretorios_segundo_nivel):
#                 movimentacao_pastas_padrao(caminho_primeiro_nivel)
#             else:
#                 for dir2 in diretorios_segundo_nivel:
#                     caminho_segundo_nivel = os.path.join(caminho_primeiro_nivel, dir2) #PATH/RS/DJRS/
#                     movimentacao_pastas_padrao(caminho_segundo_nivel)
#
# def verifica_arquivo_existente_banco():
#     try:
#         arquivo_service = ArquivoService()
#         arquivos = arquivo_service.dao.listar()
#         for arquivo in arquivos:
#
#             caminho = FileManager(arquivo.diario.nome,"log.txt","erro.txt").caminho(arquivo.nome_arquivo)
#             caminho_arquivo = os.path.join(caminho,arquivo.nome_arquivo)
#             if not os.path.exists(caminho_arquivo):
#                 print(arquivo.nome_arquivo + " arquivo não existe.")
#                 arquivo_service.dao.excluir(arquivo)
#     except Exception as e:
#         print(e)
#
# def verifica_arquivo_data_correta_pasta(path):
#     try:
#         diretorios_diarios = listdir_fullpath(path)
#         for diretorio_diario in diretorios_diarios:
#             diretorios_tipo_arquivos = listdir_fullpath(diretorio_diario)
#             diario = get_dir(diretorio_diario)
#             for diretorio_tipo_arquivo in diretorios_tipo_arquivos:
#                 diretorios_anos = listdir_fullpath(diretorio_tipo_arquivo)
#                 for diretorio_ano in diretorios_anos:
#                     diretorios_meses = listdir_fullpath(diretorio_ano)
#                     for diretorio_mes in diretorios_meses:
#                         arquivos = os.listdir(diretorio_mes)
#                         for arquivo in arquivos:
#                             try:
#                                 data = FileManager(diario).obter_data(arquivo)
#                             except Exception as e:
#                                 os.remove(os.path.join(diretorio_mes,arquivo))
#
#     except Exception as e:
#         print(e)
#
# def listdir_fullpath(path):
#     return [os.path.join(path, f)  for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
#
# def get_dir(path):
#     return os.path.split(path)[-1]
#
# #espero receber \\SRJN3\diario-mining\dados\MG\DJMG\html
# def insere_arquivos_a_serem_extraidos_ao_banco(path_inicial,extensao='html'):
#     arquivo_service = ArquivoService()
#     diario_service = DiarioService()
#     caderno_service = CadernoService()
#     diretorios_primeiro_nivel = os.listdir(path_inicial)
#     for dir1 in diretorios_primeiro_nivel:
#         path_dir1 = os.path.join(path_inicial,dir1)
#         print("Estou no caminho {}".format(path_dir1))
#         diretorios_segundo_nivel = os.listdir(path_dir1)
#         for dir2 in diretorios_segundo_nivel:
#             path_dir2 = os.path.join(path_dir1,dir2)
#             print("Estou no caminho {}".format(path_dir2))
#             arquivos_terceiro_nivel = os.listdir(path_dir2)
#             for arq in arquivos_terceiro_nivel:
#                 if arq.endswith(extensao):
#
#                     nome_diario = arq.split('_')[0]
#                     data_diario = re.search('(\d{4}_\d{2}_\d{2})',arq)
#                     if data_diario:
#                         try:
#                             data = datetime.strptime(data_diario.group(1),'%Y_%m_%d')
#                         except:
#                             print("Arquivo {} não conseguiu esxtrair a data".format(str(arq)))
#                             continue
#                     else:
#                         data = None
#
#                     diario = diario_service.preenche_diario(nome_diario, data)
#
#                     nome_caderno = Caderno.get_nome_caderno(arq,diario)
#
#                     caderno = caderno_service.preenche_caderno(nome_caderno,diario)
#
#                     arquivo = arquivo_service.preenche_arquivo(arq,diario,caderno)
#
#
# def remove_paginas_orfas(path, ext="pdf"):
#     for root, dirs, files in os.walk(path):
#         for file in files:
#             if re.search(' \.' + ext, file) or re.search('_[0-9]{6}\.' + ext, file):
#                 orfao = os.path.join(root, file)
#                 print("Deletando {}...".format(orfao))
#                 os.remove(orfao)
#
# def move_jucesp(pathantigo, pathnovo):
#     for root, dirs, files in os.walk(pathantigo):
#         for file in files:
#             res = re.search('DJSP_(\d{4}_\d{2}_\d{2})_Junta_Comercial\.pdf', file)
#
#             if res:
#                 data = datetime.strptime(res.group(1), '%Y_%m_%d')
#                 original = os.path.join(root, file)
#
#                 novodir = os.path.join(pathnovo, str(data.year), '{0:02d}'.format(data.month))
#
#                 if not os.path.exists(novodir):
#                     os.makedirs(novodir)
#
#                 novo = os.path.join(novodir, 'JUCESP_{}.pdf'.format(data.strftime('%Y_%m_%d')))
#
#                 print("Movendo {} para {}...".format(original, novo))
#
#                 try:
#                     os.rename(original, novo)
#                 except FileExistsError:
#                     os.remove(original)
#                     print("{} já existe. Pulando...".format(novo))
#
#
# #remove_paginas_orfas('Z:\\dados\\SP\\JUCESP\\txt_novo','txt')
# #move_jucesp('Z:\\dados\\SP\\DJSP\\pdf',
# #            'Z:\\dados\\SP\\JUCESP\\pdf')
#
# insere_arquivos_a_serem_extraidos_ao_banco('/mnt/dmlocal/dados/TRF/TRF01/txt', 'txt')
#
#
# #insere_arquivos_a_serem_extraidos_ao_banco("/mnt/dmlocal/dados/TRF/TRF01/txt/",'txt')
# #insere_arquivos_a_serem_extraidos_ao_banco("/mnt/dmlocal/dados/TRF/TRF03/txt/",'txt')
# #insere_arquivos_a_serem_extraidos_ao_banco("/mnt/dmlocal/dados/TRF/TRF04/txt/",'txt')
#
# if __name__ == "__main__":
#     insere_arquivos_a_serem_extraidos_ao_banco("/mnt/dmlocal/dados/TRF/TRF01/txt/",'txt')
#     insere_arquivos_a_serem_extraidos_ao_banco("/mnt/dmlocal/dados/TRF/TRF02/txt/", 'txt')
#     insere_arquivos_a_serem_extraidos_ao_banco("/mnt/dmlocal/dados/TRF/TRF03/txt/", 'txt')
#     insere_arquivos_a_serem_extraidos_ao_banco("/mnt/dmlocal/dados/TRF/TRF04/txt/", 'txt')
#     insere_arquivos_a_serem_extraidos_ao_banco("/mnt/dmlocal/dados/TRF/TRF05/txt/", 'txt')
#     # insere_arquivos_a_serem_extraidos_ao_banco("C:\\Users\\b249025230\\dados\\SP\\DJSP\\txt",'txt')
#     # insere_arquivos_a_serem_extraidos_ao_banco("/mnt/dmlocal/dados/TRF/TRF03/txt/",'txt')
#     # insere_arquivos_a_serem_extraidos_ao_banco("/mnt/dmlocal/dados/TRF/TRF04/txt/",'txt')
#     # insere_arquivos_a_serem_extraidos_ao_banco("/mnt/dmlocal/dados/TRF/TRF05/txt/",'txt')
#
# #move_arquivos_para_pasta_correta('C:\\Users\\b249025230\\PycharmProjects\\Falências\\dados\\SP\\DJSP\\txt')
# #insere_arquivos_a_serem_extraidos_ao_banco('\\\\SRJN3\\diario-mining\\dados\\SP\\DJSP\\pdf\\', 'pdf')
# #path = '/mnt/diario-mining/dados/'
# #path = '\\\\SRJN3\\diario-mining\\dados\\SP'
# #percorre_path_para_encontrar_arquivos(path)
# # verifica_arquivo_data_correta_pasta(path)
