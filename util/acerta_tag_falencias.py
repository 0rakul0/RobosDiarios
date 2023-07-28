import sys
import re
from datetime import datetime

from pdjus.service.HistoricoDadoService import HistoricoDadoService
from pdjus.service.ProcessoService import ProcessoService
#from pdjus.dal.TribunalDao import TribunalDao
from pdjus.dal.ProcTempDao import ProcTempDao

class Acerta_tag_falencias:
    def __init__(self):
        self.proctempdao = ProcTempDao()
        self.processo_service = ProcessoService()
        self.historico_dado_service = HistoricoDadoService()
        self.encontrado = True


    def remove_nao_falencias_da_tag(self):

        start = 1
        end = 5000

        try:

            lista = list(
                set(self.processo_service.dao.listar_processos_falencia(tag="FALENCIAS", rank=sys.argv[1], fatia=sys.argv[2],
                                                                   start=start, stop=end)))

            while len(lista) > 0:
                try:
                    for processo in lista:
                        print(str(processo.npu_ou_num_processo))
                        if processo.is_processo_falencia_recuperacao_convolacao() or (
                                processo.processo_principal and processo.processo_principal.is_processo_falencia_recuperacao_convolacao()):
                            print("PROCESSO DE FALENCIA ... PULANDO")
                        else:
                            historicos_retirados = []
                            for historico in processo.dado_extraido.historicos:
                                if historico.marcador == "FALENCIAS":
                                    historicos_retirados.append(historico)

                            for historico in set(historicos_retirados):
                                if not "_DUVIDOSO" in historico.marcador:
                                    historico.marcador += "_DUVIDOSO"
                                    self.historico_dado_service.salvar(historico, salvar_many_to_many=False,
                                                                  salvar_estrangeiras=False)
                                    print("PROCESSO INCORRETO ... RETTIRANDO A TAG!")

                    start = end + 1
                    end += 501

                    lista = list(set(self.processo_service.dao.listar_processos_falencia(tag="FALENCIAS", rank=sys.argv[1],
                                                                                    fatia=sys.argv[2], start=start,
                                                                                    stop=end)))

                except Exception as e:
                    print("ERRO 1 " + str(e))

        except Exception as e:
            print("ERRO 2 " + str(e))


    def varre_banco_e_cria_tag_falencias_corrigida(self, processo_id):
        processo = self.processo_service.dao.get_por_id(processo_id)
        # if processo_id == 323179:
        #     print()

        if not processo:
            self.encontrado = False
            return

        if processo.dado_extraido and 'FALENCIAS_FINAL' in [marcador.marcador for marcador in list(processo.dado_extraido.historicos)]:
            print(f'Processo {processo_id} ja esta na tag de FALENCIAS_FINAL')
            return

        if processo.is_processo_falencia_recuperacao_convolacao() or (processo.reparticao and re.search('VARA\s*DE\s*FALENCIAS?\s*E?\s*RECUPERAC(?:AO|OES)\s*JUD', processo.reparticao.nome.upper())):
            print(f'Adicionando o processo {processo_id} na tag FALENCIAS_FINAL')
            self.verifica_tag_vinculados(processo, principal_falencia=True)

            if not processo.grau:
                # possivel_processo_com_grau = self.processo_service.dao.get_por_numero_processo_ou_npu(processo.npu_ou_num_processo, grau=1)
                # if possivel_processo_com_grau:
                #     self.processo_service.salvar(possivel_processo_com_grau, tag='FALENCIAS_FINAL')
                # else:
                processo.grau = 1

            # else:
            self.processo_service.salvar(processo, tag='FALENCIAS_FINAL')

        else:
            self.verifica_tag_vinculados(processo)


    # def verifica_processo_com_grau_ja_existente(self, processo):
    #
    #     processo_com_grau = self.processo_service.dao.get_por_numero_processo_ou_npu(processo.npu_ou_num_processo, grau=1)
    #     if not processo_com_grau:
    #         if processo.grau is None:
    #             processo.grau = 1
    #         self.processo_service.salvar(processo, tag='FALENCIAS_FINAL')
    #     else:
    #         qtd_vinculados_ao_processo = len(processo.processos_vinculados)
    #         qtd_vinculados_ao_processo_com_grau = len(processo_com_grau.processos_vinculados)
    #         if qtd_vinculados_ao_processo == qtd_vinculados_ao_processo_com_grau:
    #             self.processo_service.salvar(processo_com_grau, tag='FALENCIAS_FINAL')
    #         else:
    #             if qtd_vinculados_ao_processo > qtd_vinculados_ao_processo_com_grau:
    #                 # TODO: OQ FAZER NESSA SITUAÇAO???
    #                 print('Sinuca de bico. Nao e possivel sobrescrever o processo que ja existe com o grau correto e o processo com grau tem menos vinculados que o sem grau!!!')
    #             else:
    #                 self.processo_service.salvar(processo_com_grau, tag='FALENCIAS_FINAL')
    #
    #
    #     return processo_com_grau


    def verifica_tag_vinculados(self, processo, principal_falencia=False):

        vinculados = list(processo.processos_vinculados)
        if len(vinculados) > 0:
            for vinculado in vinculados:

                if principal_falencia:
                    if vinculado.dado_extraido and 'FALENCIAS_FINAL' in [marcador.marcador for marcador in list(vinculado.dado_extraido.historicos)]:
                        print(f'Vinculado {vinculado.id} ja esta na tag de FALENCIAS_FINAL')
                        continue

                    if not vinculado.grau:
                        vinculado.grau = 1

                    self.processo_service.salvar(vinculado, tag='FALENCIAS_FINAL')

                    print(f'Adicionou o processo vinculado {vinculado.id} na tag de FALENCIAS_FINAL')
                    continue

                if vinculado.is_processo_falencia_recuperacao_convolacao() or (vinculado.reparticao and re.search('VARA\s*DE\s*FALENCIAS?\s*E?\s*RECUPERAC(?:AO|OES)\s*JUD', vinculado.reparticao.nome.upper())):
                    if processo.dado_extraido and 'FALENCIAS_FINAL' in [marcador.marcador for marcador in list(processo.dado_extraido.historicos)]:
                        print(f'Processo {processo.id} ja esta na tag de FALENCIAS_FINAL')
                    else:
                        print(f'Adicionando o processo {processo.id} na tag FALENCIAS_FINAL')

                        if not processo.grau:
                            # possivel_processo_com_grau = self.processo_service.dao.get_por_numero_processo_ou_npu(processo.npu_ou_num_processo, grau=1)
                            # if possivel_processo_com_grau:
                            #     self.processo_service.salvar(possivel_processo_com_grau, tag='FALENCIAS_FINAL')
                            # else:
                            processo.grau = 1

                        # else:
                        self.processo_service.salvar(processo, tag='FALENCIAS_FINAL')

                    self.verifica_tag_vinculados(processo, principal_falencia=True)
                    break



if __name__ == '__main__':
    c = Acerta_tag_falencias()

    rank = int(sys.argv[2])
    fatia = int(sys.argv[1])

    print(f'RANK: {rank}   FATIA: {fatia}')

    print(f'\n[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] - INICIANDO A CORREÇÃO DA TAG DE FALENCIAS')

    processos = c.proctempdao.listar_nao_processados(tag='CORRIGE_TAG', rank=rank, fatia=fatia, limit=1000)

    while len(processos) > 0:

        for id, processo in enumerate(processos, 1):
            processo.processado = True
            print(f'[ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ] - {id}/{len(processos)} - Verificando classe, assunto ou vara do processo: {processo.numero}')
            try:
                c.varre_banco_e_cria_tag_falencias_corrigida(int(processo.numero))
            except Exception as e:
                print(e)
                c.proctempdao.salvar(processo)
                continue
            processo.encontrado = True
            c.proctempdao.salvar(processo)

        processos = c.proctempdao.listar_nao_processados(tag='CORRIGE_TAG', rank=rank, fatia=fatia, limit=1000)

    print(f'\n[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] - PROCESSAMENTO DE CORREÇÃO FOI FINALIZADO')


