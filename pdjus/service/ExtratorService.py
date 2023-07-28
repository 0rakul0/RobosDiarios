from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ExtratorDao import ExtratorDao
from pdjus.modelo.Extrator import Extrator
from pdjus.service.BaseService import BaseService


class ExtratorService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ExtratorService, self).__init__(ExtratorDao())

    def preenche_extrator(self,nome):
        extrator = self.dao.get_por_nome(nome)
        if not extrator:
            extrator = Extrator()
            extrator.nome = nome
            self.salvar(extrator)
        return extrator