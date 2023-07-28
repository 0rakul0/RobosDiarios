from pdjus.conexao.Conexao import Singleton
from pdjus.dal.AdvogadoDao import AdvogadoDao
from pdjus.modelo.Advogado import Advogado
from pdjus.service.BaseService import BaseService


class AdvogadoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(AdvogadoService, self).__init__(AdvogadoDao())

    def preenche_advogado(self, nome=None, oab=None):
        advogado = None
        if oab:
            advogado = self.dao.get_por_numero_oab(oab)

        if not oab or not advogado:
            advogado = Advogado()
            advogado.nome = nome
            advogado.numero_oab = oab
            self.salvar(advogado)

        return advogado