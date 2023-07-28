from datetime import datetime

from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ProcessoDao import ProcessoDao
from pdjus.modelo.Processo import Processo
from pdjus.service.AreaService import AreaService
from pdjus.service.AssuntoService import AssuntoService
from pdjus.service.BaseService import BaseService
from pdjus.service.ClasseProcessualService import ClasseProcessualService
from pdjus.service.JuizService import JuizService
from pdjus.service.ReparticaoService import ReparticaoService
from util.StringUtil import remove_tracos_pontos_barras_espacos, remove_caracteres_especiais, remove_acentos, \
    remove_varios_espacos


class ProcessoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ProcessoService, self).__init__(ProcessoDao())




    def seta_numero_themis(self, processo, numero_themis):
        numero_themis = remove_tracos_pontos_barras_espacos(numero_themis)
        if not processo:
            processo = Processo()
        processo.numero_themis = numero_themis

    def seta_numero_processo(self, processo, numero_processo):
        numero_processo = remove_tracos_pontos_barras_espacos(numero_processo)
        if not processo:
            processo = Processo()
        processo.numero_processo = numero_processo

    def seta_data_distribuicao(self, processo, data_distribuicao, tipo_distibuicao=None):
        if not processo.data_distribuicao and data_distribuicao:
            processo.data_distribuicao = datetime.strptime(data_distribuicao, "%d/%m/%Y").date()
        if tipo_distibuicao:
            processo.tipo_distribuicao = remove_varios_espacos(remove_caracteres_especiais(remove_acentos(tipo_distibuicao)))


    def seta_valor_acao(self, valor, tipo_moeda, processo):
        # if not processo.valor_da_acao:
        processo.valor_da_acao = valor
        processo.tipo_moeda = tipo_moeda

    def seta_relator(self, processo, relator):
        if not processo.relator and relator:
            processo.relator = remove_caracteres_especiais(remove_acentos(remove_varios_espacos(relator.upper())))


    def preenche_processo(self,npu=None,numero_processo=None,grau=None,tribunal=None,tag=None,is_processos_com_mesmo_npu = False):
        processo = None
        if npu:
            processo = self.dao.get_por_numero_processo_ou_npu_e_tribunal(npu,grau,tribunal,is_processos_com_mesmo_npu=is_processos_com_mesmo_npu)
        if not processo and numero_processo:
            processo = self.dao.get_por_numero_processo_ou_npu_e_tribunal(numero_processo,grau,tribunal,is_processos_com_mesmo_npu=is_processos_com_mesmo_npu)
        if not processo:
            processo = Processo()
            if npu:
                self.seta_npu(processo,npu)
            if numero_processo:
                self.seta_numero_processo(processo,numero_processo)
            if grau:
                processo.grau = grau
                self.salvar(processo,tag=tag)
        return processo


    def seta_npu(self, processo, npu):
        npu = remove_tracos_pontos_barras_espacos(npu)
        if not processo:
            processo = Processo()
        processo.npu = npu

    def seta_reparticao(self, processo, nome_reparticao, comarca = None, tribunal = None):
        if nome_reparticao:
            reparticaoService = ReparticaoService()
            processo.reparticao = reparticaoService.preenche_reparticao(nome_reparticao, comarca, tribunal)

    def seta_juiz(self, processo, nome_juiz):
        if nome_juiz:
            juizService = JuizService()
            processo.juiz = juizService.preenche_juiz(nome_juiz)

    def seta_classe_processual(self, processo, classe, codigo_classe=None):
        if classe:
            classe_processualService = ClasseProcessualService()

            if not processo.classe_processual or processo.classe_processual.nome != classe:

                classe_processual = classe_processualService.preenche_classe_processual(classe)

                processo.classe_processual = classe_processual

    def seta_assunto(self, processo, nome_assunto, cod_assunto=None):
        assuntoService = AssuntoService()

        if processo:
            assunto = assuntoService.preenche_assunto(nome_assunto,cod_assunto)
            if not assunto in processo.assuntos:
                processo.assuntos.append(assunto)

    def seta_lista_assuntos(self,processo,lista_assuntos):
        for item_assunto in lista_assuntos:
            if item_assunto:
                self.seta_assunto(processo, item_assunto)

    def seta_processo_principal(self, processo, num_processo_principal,grau = 1, tribunal=None):
        # Rio grande do sul utiliza vazio como 0 e não como string vazia.
        vazio = ""
        zero = "0"

        if not processo.processo_principal and num_processo_principal.strip() != vazio and num_processo_principal.strip() != zero:
            if tribunal:
                processo_principal = self.dao.get_por_numero_processo_ou_npu_e_tribunal(num_processo_principal,tribunal)
            else:
                processo_principal = self.dao.get_por_numero_processo_ou_npu(num_processo_principal,grau)
            if processo_principal:
                processo.processo_principal = processo_principal

    def seta_processo_principal_sem_buscar_no_banco(self,processo_principal,processo_filho):
        if not processo_filho.processo_principal:
            processo_filho.processo_principal = processo_principal
        elif processo_principal.npu_ou_num_processo != processo_filho.processo_principal.npu_ou_num_processo:
            print('PROBLEMA COM PROCESSO PRINCIPAL E VINCULADO, JÁ EXISTE UM PRINCIPAL CADASTRADO E NÃO É ESTE PROCESSO!')

    def seta_area(self, processo, nome_area):
        if not processo.area or processo.area.nome != nome_area:
            areaService = AreaService()
            area = areaService.preenche_area(nome_area)
            processo.area = area



