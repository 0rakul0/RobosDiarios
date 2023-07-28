from pdjus.conexao.Conexao import Singleton
from pdjus.dal.TribunalDao import TribunalDao
from pdjus.modelo.Tribunal import Tribunal
from pdjus.service.BaseService import BaseService
from pdjus.service.EstadoService import EstadoService


class TribunalService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(TribunalService, self).__init__(TribunalDao())

    def preenche_tribunal(self, nome_tribunal, estado=None):
        tribunal = self.dao.get_por_nome(nome_tribunal)
        alterou = False

        if isinstance(estado, str):
            estado_service = EstadoService()
            estado = estado_service.preenche_estado(estado)

        if tribunal is None:
            tribunal = Tribunal()
            tribunal.nome = nome_tribunal
            alterou = True
        if estado and not estado in tribunal.estados:
            tribunal.estados.append(estado)
            alterou = True
        if alterou:
            self.salvar(tribunal)
        return tribunal