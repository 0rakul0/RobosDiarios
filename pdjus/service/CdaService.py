from pdjus.conexao.Conexao import Singleton
from pdjus.dal.CdaDao import CdaDao
from pdjus.modelo.Cda import Cda
from pdjus.service.BaseService import BaseService
from pdjus.modelo.Cda import Cda

class CdaService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(CdaService, self).__init__(CdaDao())

    def preenche_cda(self,processo,texto):
        cda = self.dao.get_por_processo_texto(processo,texto)
        if not cda:
            cda = Cda()
        cda.processo = processo
        cda._texto = texto
        self.salvar(cda)

        return cda