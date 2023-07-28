from pdjus.conexao.Conexao import Singleton
from pdjus.dal.GenericoDao import GenericoDao
from pdjus.modelo.CnaeObjetoSocial import CnaeObjetoSocial

class CnaeObjetoSocialDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(CnaeObjetoSocialDao, self).__init__(CnaeObjetoSocial)

    def get_por_cnae_objeto_social(self, cnae, objeto_social):
        try:
            return self._classe.select().where(self._classe.cnae==cnae,self._classe.objeto_social==objeto_social).get()
        except self._classe.DoesNotExist as e:
            return None
