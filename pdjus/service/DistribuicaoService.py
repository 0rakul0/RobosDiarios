from pdjus.conexao.Conexao import Singleton
from pdjus.dal.DistribuicaoAssuntoDao import DistribuicaoAssuntoDao
from pdjus.dal.DistribuicaoDao import DistribuicaoDao
from pdjus.modelo.Distribuicao import Distribuicao
from pdjus.modelo.DistribuicaoAssunto import DistribuicaoAssunto
from pdjus.service.AssuntoService import AssuntoService
from pdjus.service.BaseService import BaseService
from pdjus.service.CadernoService import CadernoService
from pdjus.service.ClasseProcessualService import ClasseProcessualService
from pdjus.service.ComarcaService import ComarcaService
from pdjus.service.DiarioService import DiarioService
from pdjus.service.EstadoService import EstadoService
from pdjus.service.ParteDistribuicaoService import ParteDistribuicaoService
import datetime

class DistribuicaoService(BaseService ,metaclass=Singleton):

    def __init__(self):
        self.classes_populacao = ['RECUP.*JUD']
        self.classe_service = ClasseProcessualService()
        self.estado_service = EstadoService()
        self.caderno_service = CadernoService()
        self.diario_service = DiarioService()
        self.comarca_service = ComarcaService()
        self.parte_distribuicao_service = ParteDistribuicaoService()
        super(DistribuicaoService, self).__init__(DistribuicaoDao())
        #self.distribuicoes_com_rais = list(self.dao.get_distribuicao_com_rais())

    def seta_assunto(self, distribuicao, nome_assunto,data, cod_assunto=None):
        assuntoService = AssuntoService()
        if distribuicao:
            distribuicao_assuntodao = DistribuicaoAssuntoDao()
            assunto = assuntoService.preenche_assunto(nome_assunto,cod_assunto)
            distribuicao_assunto = distribuicao_assuntodao.get_por_distribuicao_assunto(distribuicao, assunto)
            if not distribuicao_assunto:
                distribuicao_assunto = DistribuicaoAssunto()
                distribuicao_assunto.distribuicao= distribuicao
                distribuicao_assunto.assunto = assunto
                distribuicao_assunto.data = data
                distribuicao_assuntodao.salvar(distribuicao_assunto)


    def seta_data(self, distribuicao, data):
        if not distribuicao.data_distribuicao and data:
            distribuicao.data_distribuicao = data

    def get_quantidade_por_percentual_classe_data(self, percentual, classe, data):
        return self.get_quantidade_por_percentual_classe_ano_mes(percentual, classe, data.year, data.month)

    def get_quantidade_por_percentual_classe_ano_mes(self, percentual, classe, ano, mes):
        quantidade_total = self.dao.get_quantidade_por_classe_ano_mes(classe,ano,mes)
        if classe in self.classes_populacao:
            percentual = 100
        if type(percentual) is int:
            percentual_valor_decimal = percentual/100
        else:
            percentual_valor_decimal = percentual

        return quantidade_total * percentual_valor_decimal


    def get_proporcao_pj(self,tipo_parte,classe,ano,mes):
        quantidade_total = self.dao.get_quantidade_por_classe_ano_mes(classe, ano, mes)
        quantidade_pj = self.dao.get_quantidade_pj_por_tipo_parte_classe_ano_mes(tipo_parte,classe,ano,mes)
        if quantidade_total == 0:
            return 0
        return quantidade_pj/quantidade_total



    def get_proporcao_banco(self,tipo_parte,classe, ano, mes):
        quantidade_total = self.dao.get_quantidade_por_classe_ano_mes(classe, ano, mes)
        quantidade_banco = self.dao.get_quantidade_banco_por_tipo_parte_classe_ano_mes(tipo_parte,classe, ano, mes)
        if quantidade_total == 0:
            return 0
        return quantidade_banco / quantidade_total

    def get_proporcao_setor(self,tipo_parte,classe, ano, mes):
        quantidade_setor = self.dao.get_quantidade_setor_por_tipo_parte_classe_ano_mes(tipo_parte,classe, ano, mes)

        return quantidade_setor


    def _preenche_distribuicao(self,numero_processo, dt_pub, classe, outros, caderno, tipo_dist, vara, comarca,
                    estado, tag):
        distribuicao = Distribuicao()
        # lista = list(self.dao.get_por_numero_processo_caderno(numero_processo,caderno))
        # if not lista and len(lista) == 0:
        #     distribuicao = Distribuicao()
        # else:
        #     if len(lista) == 1:
        #         distribuicao = lista[0]
        #     else:
        #
        #         for i,item in enumerate(lista):
        #             if i == 0:
        #                 distribuicao = item
        #             else:
        #                 try:
        #                     self.dao.excluir(item,commit=False)
        #                 except:
        #                     self.dao.rollback()
        #                     try:
        #                         self.dao.excluir(distribuicao,commit=False)
        #                     except:
        #                         pass
        #                     distribuicao = item

        distribuicao.numero_processo = numero_processo
        distribuicao.caderno = caderno
        distribuicao.classe_processual = classe
        distribuicao.data_distribuicao = dt_pub
        distribuicao.estado = estado
        distribuicao.tipo_distribuicao = tipo_dist
        distribuicao.comarca = comarca
        distribuicao.vara = vara
        if outros:
            distribuicao.outros = outros
        self.salvar(distribuicao, commit=False, caderno=caderno, tag=tag, salvar_estrangeiras=False,
                       salvar_many_to_many=False)
        return distribuicao

    def preenche_distribuicao(self, nome_classe, nome_diario, dt_diario, nome_caderno, uf,
                              dt_pub, numero_processo, tipo_dist, nome_comarca=None, tag=None, partes_distribuicoes=None,vara=None,outros=None,diario=None,caderno=None):



        comarca = self.comarca_service.preenche_comarca(nome_comarca)

        classe = self.classe_service.preenche_classe_processual(nome_classe)

        if not diario:
            diario = self.diario_service.preenche_diario(nome_diario, dt_diario)

        if not caderno:
            caderno = self.caderno_service.preenche_caderno(nome_caderno,diario)

        estado = self.estado_service.preenche_estado(uf)

        distribuicao = self._preenche_distribuicao(numero_processo, dt_pub, classe, outros, caderno, tipo_dist, vara, comarca, estado, tag)

        self.parte_distribuicao_service.preenche_parte_distribuicao(partes_distribuicoes, distribuicao, caderno, tag)

