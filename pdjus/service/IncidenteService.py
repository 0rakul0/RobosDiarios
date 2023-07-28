from pdjus.conexao.Conexao import Singleton
from pdjus.dal.IncidenteDao import IncidenteDao
from pdjus.modelo.Incidente import Incidente
from pdjus.service.BaseService import BaseService


class IncidenteService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(IncidenteService, self).__init__(IncidenteDao())

    def preenche_incidente(self, processo,data,texto):
        incidente = None
        if processo and processo.id is not None:
            incidente = self.dao.get_por_processo_data_descricao(processo, data, texto)
        if incidente is None:
            incidente = Incidente()
            incidente.data = data
            incidente.descricao = texto
            incidente.processo = processo
            self.salvar(incidente, salvar_estrangeiras=False, salvar_many_to_many=False)
        return incidente