from pdjus.conexao.Conexao import Singleton
from pdjus.dal.EstadoDao import EstadoDao
from pdjus.modelo.Estado import Estado
from pdjus.service.BaseService import BaseService


class EstadoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(EstadoService, self).__init__(EstadoDao())

    def preenche_estado(self,sigla):
        estado = self.dao.get_por_sigla(sigla,cache=True)

        if estado is None:
            estado = Estado()
            estado.sigla = sigla
            estado.nome = Estado.estados_por_sigla[sigla]
            self.salvar(estado)
            self.dao.add_to_cache(estado)

        return estado