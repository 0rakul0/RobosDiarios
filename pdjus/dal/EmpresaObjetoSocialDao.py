from pdjus.conexao.Conexao import Singleton
from pdjus.dal.GenericoDao import GenericoDao


from pdjus.modelo.EmpresaObjetoSocial import EmpresaObjetoSocial
from pdjus.modelo.ObjetoSocial import ObjetoSocial

class EmpresaObjetoSocialDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(EmpresaObjetoSocialDao, self).__init__(EmpresaObjetoSocial)

    def get_por_empresa_objeto_social(self, empresa, objeto_social):
        try:
            return self._classe.select().where(self._classe.empresa==empresa,self._classe.objeto_social==objeto_social).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_empresa_por_objeto_social(self,objeto_social):
        try:
            return self.listar().select().where(self._classe.objeto_social==objeto_social)
        except self._classe.DoesNotExist as e:
            return None

    def listar_objetos_da_empresa(self,empresa):
        try:
            return self.listar().select().where(self._classe.empresa==empresa)
        except self._classe.DoesNotExist as e:
            return None

    def listar_objetos_da_empresa_que_sao_constituicoes(self):
        try:
            return self.listar().select().where(self._classe.fonte_dado=='1')
        except self._classe.DoesNotExist as e:
            return None

    def listar_objetos_que_sao_constituicoes(self):

        indice = self.execute_sql(
            '''
            select distinct(obj.id) from homologacao_jucesp.empresa e 
          join homologacao_jucesp.empresa_objeto_social eobj on eobj.empresa_id = e.id
          join homologacao_jucesp.objeto_social obj on obj.id = eobj.objeto_social_id 
          where eobj.fonte_dado = '1' ''' )

        return indice