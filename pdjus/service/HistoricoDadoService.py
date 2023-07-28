# import datetime
from pdjus.conexao.Conexao import Singleton
from pdjus.dal.HistoricoDadoDao import HistoricoDadoDao
from pdjus.service.BaseService import BaseService
# from pdjus.modelo.HistoricoDado import HistoricoDado
# from pdjus.service.DadoExtraidoService import DadoExtraidoService


class HistoricoDadoService(BaseService, metaclass=Singleton):

    def __init__(self):
        super(HistoricoDadoService, self).__init__(HistoricoDadoDao())

    # def preenche_historico_dado(self, tag):
    #
    #     historico_dado_dao = HistoricoDadoDao()
    #     dado_extraido_service = DadoExtraidoService()
    #     historico_dado = historico_dado_dao.get_por_marcador(tag)
    #
    #     if historico_dado is None:
    #         historico_dado = HistoricoDado()
    #         dado_extraido = dado_extraido_service.preenche_dado_extraido()
    #
    #         historico_dado.marcador = tag.upper()
    #         historico_dado.dado_extraido = dado_extraido
    #         historico_dado.data_extracao = datetime.datetime.now().date()
    #         historico_dado.local_extracao = 'SISTEMA'
    #
    #         historico_dado_dao.salvar(historico_dado)
    #
    #     return historico_dado