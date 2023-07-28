from pdjus.service.MovimentoService import MovimentoService
from pdjus.service.TipoMovimentoService import TipoMovimentoService
from pdjus.service.ProcessoService import ProcessoService
from util.StringUtil import remove_acentos, remove_varios_espacos, remove_quebras_linha_de_linha, remove_tracos_pontos_barras_espacos
from util.GoogleVisionOCR import converte_pdf
from datetime import datetime, date
from pathlib import Path
import os
import re




def varre_diretorio_atualizando_inteiro_teor_trf1(path, recursao=False):

    procs = ['00000045120104013806', '00003139820074013702', '00005327720084013702', '00010923720084013308', '00011480720084013814', '00012728720164013303', '00012778020144013303', '00015942620154013309', '00016247620164014004', '00036529620114014002', '00041857120104013814', '00043259120124013311', '00043454420104013702', '00043783020114013304', '00043936520134014003', '00044305520134013304', '00047518520134013823', '00053635420064013310', '00214419120134013500', '200633100029996', '200636000082015', '200637000000842', '200637000000842', '200833100005233', '200840000033724', '200939030003231']
    processo_service = ProcessoService()
    movimento_service = MovimentoService()
    tipo_movimento_service = TipoMovimentoService()
    # rank = 4
    # fatia = 5


    try:
        if recursao:
        # diretorios = sorted(Path(path).iterdir(), key=os.path.getmtime, reverse=True)
            diretorios = sorted(os.listdir(path), reverse=False)
            for idx, nome_item_pasta in enumerate(diretorios):
                # if idx % fatia == rank:
                try:
                    # nome_item_pasta = nome_item_pasta.name
                    if '.xml' in nome_item_pasta or '.doc' in nome_item_pasta:
                        continue

                    item_pasta = os.path.join(path, nome_item_pasta)

                    if not os.path.isfile(item_pasta):
                        print("{} - Estou no caminho {}".format(datetime.now(), item_pasta))
                        varre_diretorio_atualizando_inteiro_teor_trf1(item_pasta, recursao=True)

                    else:
                        npu = item_pasta.split('/')[-2]
                        processo = processo_service.dao.get_por_numero_processo_ou_npu(npu, grau=1)

                        if processo:
                            ano = int(''.join(list(nome_item_pasta.split('_')[1].split('.')[0])[0:4]))
                            mes = int(''.join(list(nome_item_pasta.split('_')[1].split('.')[0])[4:6]))
                            dia = int(''.join(list(nome_item_pasta.split('_')[1].split('.')[0])[6:]))

                            tipo_movimento = 'INTEIRO_TEOR - {}'.format(nome_item_pasta.split('_')[0])
                            data = datetime(year=ano, month=mes, day=dia)

                            texto = None
                            tipo_movimento_obj = tipo_movimento_service.dao.get_por_nome(tipo_movimento)
                            movimento = movimento_service.dao.get_por_processo_data_tipo_movimento_texto(processo, data, tipo_movimento_obj, texto)
                            if not movimento:
                                processo = processo_service.dao.get_por_numero_processo_ou_npu(npu, grau=2)
                                movimento = movimento_service.dao.get_por_processo_data_tipo_movimento_texto(processo,data,tipo_movimento_obj,texto)

                            if movimento:
                                contents = None
                                tentativas = 0

                                while not contents and tentativas <= 5:
                                    try:
                                        print('{} - Convertendo arquivo: {}'.format(datetime.now(), item_pasta))
                                        contents = remove_quebras_linha_de_linha \
                                            (remove_acentos(
                                                remove_varios_espacos(converte_pdf(item_pasta, 'trf1')))).upper()

                                    except Exception as e:
                                        contents = None
                                        tentativas += 1
                                        if tentativas != 6:
                                            print('{}. Tentando novamente'.format(tentativas))
                                        continue

                                try:
                                    if contents:
                                        movimento_service.atualiza_movimento(movimento=movimento, texto=contents)
                                        print('{} - Atualizou o movimento {} do processo {}....'.format(datetime.now(),
                                                                                                        tipo_movimento,
                                                                                                        processo.npu_ou_num_processo))
                                    else:
                                        print('{} - PDF {} referente ao processo {} não foi inserido....'.format(
                                            datetime.now(), tipo_movimento,
                                            processo.npu_ou_num_processo))
                                except:
                                    print(contents + 'Arquivo em .{}'.format(
                                        list(nome_item_pasta.split('_')[1].split('.'))[1]))

                        else:
                            continue

                except Exception as e:
                    print(e)
        else:
            for idx, nome_item_pasta in enumerate(procs):
                # if idx % fatia == rank:
                try:
                    # nome_item_pasta = nome_item_pasta.name
                    if '.xml' in nome_item_pasta or '.doc' in nome_item_pasta:
                        continue

                    item_pasta = os.path.join(path, nome_item_pasta)

                    if not os.path.isfile(item_pasta):
                        print("{} - Estou no caminho {}".format(datetime.now(), item_pasta))
                        varre_diretorio_atualizando_inteiro_teor_trf1(item_pasta, recursao=True)

                except Exception as e:
                    print(e)


    except FileNotFoundError:
        print("{} - Não encontrei o diretorio: {}".format(datetime.now(), path))
        return



def varre_diretorio_atualizando_inteiro_teor_trf2(path, recursao=False):
    procs = ['00000597720094025109', '00007578320094025109', '00010684420094025119', '00093987920124025101', '00148223420144025101']
    processo_service = ProcessoService()
    movimento_service = MovimentoService()
    # rank = 4
    # fatia = 5

    try:
        saida = False
        if recursao:
        # diretorios = sorted(Path(path).iterdir(), key=os.path.getmtime, reverse=True)
            diretorios = sorted(os.listdir(path), reverse=False)
            for idx, nome_item_pasta in enumerate(diretorios):
                # if idx % fatia == rank:
                if saida is True:
                    saida = False
                    break
                try:
                    # nome_item_pasta = nome_item_pasta.name
                    if '.xml' in nome_item_pasta or '.doc' in nome_item_pasta:
                        continue

                    item_pasta = os.path.join(path, nome_item_pasta)

                    if not os.path.isfile(item_pasta):
                        print("{} - Estou no caminho {}".format(datetime.now(), item_pasta))
                        varre_diretorio_atualizando_inteiro_teor_trf2(item_pasta, recursao=True)

                    else:
                        npu = item_pasta.split('/')[-2]
                        processo = processo_service.dao.get_por_numero_processo_ou_npu(npu, grau=2)

                        # if not processo:
                        #     processo = processo_service.dao.get_por_numero_processo_ou_npu(npu, grau=2)

                        if processo:
                            lista_movs_inteiro_teor = []
                            saida = False
                            for mov in list(processo.movimentos):
                                if mov.texto == None and re.search('INTEIRO_TEOR', mov.tipo_movimento.nome):
                                    lista_movs_inteiro_teor.append(mov)

                            lista_arqs = []

                            if len(lista_movs_inteiro_teor) == 0:
                                saida = True
                                break

                            for idx, mov_inteiro_teor in enumerate(lista_movs_inteiro_teor):

                                for arq in diretorios:
                                    if saida is True and idx != len(lista_movs_inteiro_teor)-1:
                                        saida = False
                                        break
                                    elif saida is True and idx == len(lista_movs_inteiro_teor)-1:
                                        saida = True
                                        break

                                    if mov_inteiro_teor.tipo_movimento.nome.split('-')[1].replace('_','') in arq.upper().replace('_','') and '.pdf' in arq and arq not in lista_arqs:

                                        # if saida is True:
                                        #     break
                                        data_list = list(arq.split('_')[-1].split('.')[0])
                                        ano = int(''.join(data_list[0:4]))
                                        mes = int(''.join(data_list[4:6]))
                                        dia = int(''.join(data_list[6:8]))

                                        data = date(day=dia, month=mes, year=ano)

                                        if data == mov_inteiro_teor.data:
                                            contents = None
                                            tentativas = 0
                                            while not contents and tentativas <= 5:
                                                try:
                                                    print('{} - Convertendo arquivo: {}'.format(datetime.now(), path+'/'+arq))
                                                    contents = remove_quebras_linha_de_linha \
                                                            (remove_acentos(
                                                            remove_varios_espacos(converte_pdf(path+'/'+arq, 'trf2')))).upper()

                                                except Exception:
                                                    contents = None
                                                    tentativas += 1
                                                    if tentativas != 6:
                                                        print('{}. Tentando novamente'.format(tentativas))
                                                    continue

                                                try:
                                                    if contents:
                                                        movimento_service.atualiza_movimento(movimento=mov_inteiro_teor,
                                                                                             texto=contents)
                                                        print('{} - Atualizou o movimento {} do processo {}....'.format(
                                                            datetime.now(),
                                                            mov_inteiro_teor.tipo_movimento.nome,
                                                            processo.npu_ou_num_processo))
                                                        lista_arqs.append(arq)
                                                        saida = True
                                                    else:
                                                        print(
                                                            '{} - PDF {} referente ao processo {} não foi inserido....'.format(
                                                                datetime.now(), mov_inteiro_teor.tipo_movimento.nome,
                                                                processo.npu_ou_num_processo))
                                                        saida = True
                                                except:
                                                    print(contents + 'Arquivo em .{}'.format(
                                                        list(nome_item_pasta.split('_')[1].split('.'))[1]))

                                                    saida = True


                        else:
                            continue

                except Exception as e:
                    print(e)
        else:
            for idx, nome_item_pasta in enumerate(procs):
                # if idx % fatia == rank:
                try:
                    # nome_item_pasta = nome_item_pasta.name
                    if '.xml' in nome_item_pasta or '.doc' in nome_item_pasta:
                        continue

                    item_pasta = os.path.join(path, nome_item_pasta)

                    if not os.path.isfile(item_pasta):
                        print("{} - Estou no caminho {}".format(datetime.now(), item_pasta))
                        varre_diretorio_atualizando_inteiro_teor_trf2(item_pasta, recursao=True)

                except Exception as e:
                    print(e)


    except FileNotFoundError:
        print("{} - Não encontrei o diretorio: {}".format(datetime.now(), path))
        return