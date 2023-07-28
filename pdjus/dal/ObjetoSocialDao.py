from util.StringUtil import remove_varios_espacos, remove_acentos,remove_links
from pdjus.dal.GenericoDao import *
from pdjus.modelo.ObjetoSocial import ObjetoSocial
from pdjus.modelo.Cnae import CnaeObjetoSocial


class ObjetoSocialDao(GenericoDao,metaclass=Singleton):

    def __init__(self):
        super(ObjetoSocialDao, self).__init__(ObjetoSocial)


    def get_por_nome(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome)).upper()
            obj = self._classe.get(self._classe._nome == nome)
            return obj
        except self._classe.DoesNotExist as e:
            return None

    def listar_objetos_nao_classificados_para_teste(self, fatia=1, rank=0):
        try:
            return self.listar(fatia=fatia, rank=rank).select().where(self._classe.classificado == True)
        except self._classe.DoesNotExist as e:
            return None

    def listar_objetos_nao_classificados(self,fatia=1,rank=0):
        try:
            return self.listar(fatia=fatia, rank=rank).select().join(CnaeObjetoSocial,join_type=JOIN.LEFT_OUTER).where(CnaeObjetoSocial.objeto_social == None,self._classe.classificado == False)
        except self._classe.DoesNotExist as e:
            return None

