from datetime import datetime
from pdjus.dal.ProcTempDao import ProcTempDao
from pdjus.service.ProcessoService import ProcessoService

class AcertaBancoProducao:
    def __init__(self):
        self.proctempdao = ProcTempDao()
        self.processoservice = ProcessoService()
        self.lista_id_proc_correto_incorreto = []
        self.arquivo = open('../Processos_com_problema_de_grau.txt', mode='a+')

    def corrige_banco(self, processo_id):

        processo_sem_grau = self.processoservice.dao.get_por_id(processo_id)

        # if 'CORRECAO_FALEN' in [hd.marcador for hd in processo_sem_grau.dado_extraido.historicos]:
        #     return

        processo_com_grau = self.processoservice.dao.get_por_numero_processo_ou_npu(processo_sem_grau.npu_ou_num_processo, grau=1)

        self.verifica_movimentos(processo_incorreto_ou_sem_grau=processo_sem_grau, processo_correto_ou_com_grau=processo_com_grau)


    def verifica_movimentos(self, processo_incorreto_ou_sem_grau, processo_correto_ou_com_grau, vinculado=False):

        mov_processo_incorreto_ou_sem_grau = sorted([(movimento.data, movimento.id) for movimento in processo_incorreto_ou_sem_grau.movimentos], key=lambda x: x[0])
        mov_processo_correto_ou_com_grau = sorted([(movimento.data, movimento.id) for movimento in processo_correto_ou_com_grau.movimentos], key=lambda x: x[0])

        if len(mov_processo_incorreto_ou_sem_grau) == 0 and len(mov_processo_correto_ou_com_grau) == 0:
            if not vinculado:
                self.cria_merge_processos(processo_correto=processo_correto_ou_com_grau, processo_incorreto=processo_incorreto_ou_sem_grau)
            else:
                return processo_correto_ou_com_grau, processo_incorreto_ou_sem_grau

        elif len(mov_processo_incorreto_ou_sem_grau) > 0 and len(mov_processo_correto_ou_com_grau) == 0:
            if not vinculado:
                self.cria_merge_processos(processo_correto=processo_incorreto_ou_sem_grau, processo_incorreto=processo_correto_ou_com_grau)
            else:
                return processo_incorreto_ou_sem_grau, processo_correto_ou_com_grau

        elif len(mov_processo_correto_ou_com_grau) > 0 and len(mov_processo_incorreto_ou_sem_grau) == 0:
            if not vinculado:
                self.cria_merge_processos(processo_correto=processo_correto_ou_com_grau, processo_incorreto=processo_incorreto_ou_sem_grau)
            else:
                return processo_correto_ou_com_grau, processo_incorreto_ou_sem_grau

        else:
            if mov_processo_incorreto_ou_sem_grau[-1][0] > mov_processo_correto_ou_com_grau[-1][0]:
                if not vinculado:
                    self.cria_merge_processos(processo_correto=processo_incorreto_ou_sem_grau, processo_incorreto=processo_correto_ou_com_grau)
                return processo_incorreto_ou_sem_grau, processo_correto_ou_com_grau

            elif mov_processo_correto_ou_com_grau[-1][0] > mov_processo_incorreto_ou_sem_grau[-1][0]:
                if not vinculado:
                    self.cria_merge_processos(processo_correto=processo_correto_ou_com_grau, processo_incorreto=processo_incorreto_ou_sem_grau)
                return processo_correto_ou_com_grau, processo_incorreto_ou_sem_grau

            elif len(mov_processo_incorreto_ou_sem_grau) > len(mov_processo_correto_ou_com_grau):
                if not vinculado:
                    self.cria_merge_processos(processo_correto=processo_incorreto_ou_sem_grau, processo_incorreto=processo_correto_ou_com_grau)
                #self.lista_id_proc_correto_incorreto.append((f'Processo correto: {processo_incorreto_ou_sem_grau.id}', processo_correto_ou_com_grau.id, processo_correto_ou_com_grau.npu_ou_num_processo))
                return processo_incorreto_ou_sem_grau, processo_correto_ou_com_grau

            elif len(mov_processo_correto_ou_com_grau) > len(mov_processo_incorreto_ou_sem_grau):
                if not vinculado:
                    self.cria_merge_processos(processo_correto=processo_correto_ou_com_grau, processo_incorreto=processo_incorreto_ou_sem_grau)
                #self.lista_id_proc_correto_incorreto.append((f'Processo correto: {processo_correto_ou_com_grau.id}', processo_incorreto_ou_sem_grau.id, processo_correto_ou_com_grau.npu_ou_num_processo))
                return processo_correto_ou_com_grau, processo_incorreto_ou_sem_grau

            else:
                if not vinculado:
                    self.cria_merge_processos(processo_correto=processo_correto_ou_com_grau, processo_incorreto=processo_incorreto_ou_sem_grau)
                return processo_correto_ou_com_grau, processo_incorreto_ou_sem_grau


    def cria_merge_processos(self, processo_correto, processo_incorreto):

        vinculados_processo_correto = list(processo_correto.processos_vinculados)
        vinculados_processo_incorreto = list(processo_incorreto.processos_vinculados)
        lista_processos_para_vincular = set()
        lista_processos_para_exclusao = set()

        if len(vinculados_processo_incorreto) > 0:
            for vinc_incorreto in vinculados_processo_incorreto:
                for vinc_correto in vinculados_processo_correto:
                    if vinc_incorreto.npu_ou_num_processo == vinc_correto.npu_ou_num_processo:
                        if vinc_incorreto.id == vinc_correto.id:
                            lista_processos_para_vincular.add(vinc_incorreto)
                        else:
                            proc_correto, proc_incorreto = self.verifica_movimentos(processo_incorreto_ou_sem_grau=vinc_incorreto, processo_correto_ou_com_grau=vinc_correto, vinculado=True)
                            lista_processos_para_vincular.add(proc_correto)
                            lista_processos_para_exclusao.add(proc_incorreto)
                    else:
                        lista_processos_para_vincular.add(vinc_incorreto)

            for proc_exclusao in lista_processos_para_exclusao:
                proc_exclusao.grau = 99
                proc_exclusao.processo_principal = None
                try:
                    self.processoservice.salvar(proc_exclusao, tag='CORRECAO_FALEN')
                except:
                    print('id do processo principal, grau, id processo vinculado, grau')
                    self.arquivo.write(f'{processo_correto.id};{processo_correto.grau};{proc_exclusao.id};{proc_exclusao.grau}\n')
                    self.arquivo.flush()
                print(f'Excluindo o processo vinculado de NPU {proc_exclusao.npu_ou_num_processo} e setando o grau 99')

            for proc in lista_processos_para_vincular:
                proc.grau = 1
                proc.processo_principal = processo_correto
                try:
                    self.processoservice.salvar(proc, tag='CORRECAO_FALEN')
                except:
                    print('id do processo principal, grau, id processo vinculado, grau')
                    self.arquivo.write(f'{processo_correto.id};{processo_correto.grau};{proc.id};{proc.grau}\n')
                    self.arquivo.flush()
                print(f'Salvando o processo vinculado de NPU {proc.npu_ou_num_processo}')


        processo_incorreto.grau = 99
        try:
            self.processoservice.salvar(processo_incorreto, tag='CORRECAO_FALEN')
        except:
            print()
        print(f'Salvando o processo incorreto de NPU {processo_incorreto.npu_ou_num_processo} com o grau 99')

        processo_correto.grau = 1
        try:
            self.processoservice.salvar(processo_correto, tag='CORRECAO_FALEN')
        except:
            print()
        print(f'Salvando o processo correto de NPU {processo_correto.npu_ou_num_processo} com o grau 1')



if __name__ == '__main__':
    c = AcertaBancoProducao()

    rank = 2
    fatia = 3

    print(f'RANK: {rank}   FATIA: {fatia}')

    print(f'\n[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] - INICIANDO A CORREÇÃO DO BANCO DE PRODUCAO')

    processos = c.proctempdao.listar_nao_processados(tag='AGORA_VAI', rank=rank, fatia=fatia, limit=1000)
    # processos = [125013]

    while len(processos) > 0:

        for id, processo in enumerate(processos, 1):
            processo.processado = True
            print(f'[ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ] - {id}/{len(processos)} - Verificando processo correto e incorreto através do processo: {processo.numero}')
            c.corrige_banco(int(processo.numero))
            processo.encontrado = True
            c.proctempdao.salvar(processo)

        processos = c.proctempdao.listar_nao_processados(tag='AGORA_VAI', rank=rank, fatia=fatia, limit=1000)

    # [print(i) for i in c.lista_id_proc_correto_incorreto]
    # print(len(c.lista_id_proc_correto_incorreto))

    print(f'\n[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] - PROCESSAMENTO DE CORREÇÃO FOI FINALIZADO')