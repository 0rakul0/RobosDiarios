from pdjus.conexao.Conexao import Singleton
from pdjus.dal.GenericoDao import GenericoDao


from pdjus.modelo.EmpresaEnquadramento import EmpresaEnquadramento

class EmpresaEnquadramentoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(EmpresaEnquadramentoDao, self).__init__(EmpresaEnquadramento)

    def get_por_empresa_enquadramento(self, empresa, enquadramento):
        try:
            return self._classe.select().where(self._classe.empresa==empresa,self._classe.enquadramento==enquadramento).get()
        except self._classe.DoesNotExist as e:
            return None