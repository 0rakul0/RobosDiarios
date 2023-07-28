from pdjus.conexao.Conexao import Singleton
from pdjus.dal.MapaProcessoDao import MapaProcessoDao
from pdjus.modelo.MapaProcesso import MapaProcesso
from pdjus.service.AssuntoService import AssuntoService
from pdjus.service.ProcessoService import ProcessoService
from pdjus.service.ReparticaoService import ReparticaoService
from pdjus.service.BaseService import BaseService
from pdjus.service.ClasseProcessualService import ClasseProcessualService
from util.StringUtil import remove_tracos_pontos_barras_espacos
from pdjus.service.AreaService import AreaService
from datetime import datetime

class MapaProcessoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(MapaProcessoService, self).__init__(MapaProcessoDao())


    def seta_numero_processo(self, processo, numero_processo):
        numero_processo = remove_tracos_pontos_barras_espacos(numero_processo)
        if not processo:
            processo = MapaProcesso()
        processo.numero_processo = numero_processo


    def preenche_processo(self,npu=None,numero_processo=None,tribunal=None):
        processo = None
        if npu:
            processo = self.dao.get_por_numero_processo_ou_npu_e_tribunal(npu,tribunal)
        if not processo and numero_processo:
            processo = self.dao.get_por_numero_processo_ou_npu_e_tribunal(numero_processo,tribunal)
        if not processo:
            processo = MapaProcesso()
            if npu:
                self.seta_npu(processo,npu)
            if numero_processo:
                self.seta_numero_processo(processo,numero_processo)
        return processo


    def seta_npu(self, processo, npu):
        npu = remove_tracos_pontos_barras_espacos(npu)
        if not processo:
            processo = MapaProcesso()
        processo.npu = npu

    def seta_reparticao(self, processo, nome_reparticao, comarca = None,tribunal = None):
        if nome_reparticao:
            reparticaoService = ReparticaoService()
            processo.reparticao = reparticaoService.preenche_reparticao(nome_reparticao, comarca=comarca,tribunal=tribunal)

    def seta_classe_processual(self, processo, classe, codigo_classe=None):
        if classe:
            classe_processualService = ClasseProcessualService()

            if not processo.classe_processual or processo.classe_processual.nome != classe:

                classe_processual = classe_processualService.preenche_classe_processual(classe)

                processo.classe_processual = classe_processual

    def seta_data_distribuicao(self, processo, data_distribuicao):
        if not processo.data_distribuicao and data_distribuicao:
            processo.data_distribuicao = datetime.strptime(data_distribuicao, "%d/%m/%Y").date()


    def seta_processo_principal(self, processo, num_processo_principal,grau, tribunal=None):
        # Rio grande do sul utiliza vazio como 0 e não como string vazia.
        processo_service = ProcessoService()
        vazio = ""
        zero = "0"

        if not processo.processo_principal and num_processo_principal.strip() != vazio and num_processo_principal.strip() != zero:
            if tribunal:
                processo_principal = processo_service.dao.get_por_numero_processo_ou_npu_e_tribunal(num_processo_principal,tribunal)
            else:
                processo_principal = processo_service.dao.get_por_numero_processo_ou_npu(num_processo_principal,grau)
            if processo_principal:
                processo.processo_principal = processo_principal

    def seta_processo_principal_sem_buscar_no_banco(self,processo_principal,processo_filho):
        if not processo_filho.processo_principal:
            processo_filho.processo_principal = processo_principal
        elif processo_principal.npu_ou_num_processo != processo_filho.processo_principal.npu_ou_num_processo:
            print('PROBLEMA COM PROCESSO PRINCIPAL E VINCULADO, JÁ EXISTE UM PRINCIPAL CADASTRADO E NÃO É ESTE PROCESSO!')

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

    def seta_area(self, processo, nome_area):
        if not processo.area or processo.area.nome != nome_area:
            areaService = AreaService()
            area = areaService.preenche_area(nome_area)
            processo.area = area
    # def seta_area(self, processo, nome_area):
    #     if not processo.area or processo.area.nome != nome_area:
    #         areaService = AreaService()
    #         area = areaService.preenche_area(nome_area)
    #         processo.area = area



