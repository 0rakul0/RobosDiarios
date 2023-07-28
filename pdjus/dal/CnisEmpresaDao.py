from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.CnisEmpresa import CnisEmpresa

class CnisEmpresaDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(CnisEmpresaDao, self).__init__(CnisEmpresa)


    def get_por_id_empresa_estab(self, id_empresa_estab):
        try:
            return self._classe.get(self._classe.id_empresa_estab == id_empresa_estab)
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_nome_com_regex_match(self,regex):
        try:
            return self._classe.select().where(self._classe._nome.regexp(regex))
        except self._classe.DoesNotExist as e:
            return None

