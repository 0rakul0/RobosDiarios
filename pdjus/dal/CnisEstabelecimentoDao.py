from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.CnisEstabelecimento import CnisEstabelecimento


class CnisEstabelecimentoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(CnisEstabelecimentoDao, self).__init__(CnisEstabelecimento)


    def get_por_id_empresa_estab(self, id_empresa_estab):
        try:
            return self._classe.get(self._classe.id_empresa_estab == id_empresa_estab)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_id_empresa_estab_e_cnpj(self, id_empresa_estab,cnpj):
        try:
            return self._classe.get((self._classe.id_empresa_estab == id_empresa_estab),(self._classe.cnpj == cnpj))
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_nome_com_regex_match(self,regex):
        try:
            return self._classe.select().where(self._classe._nome.regexp(regex))
        except self._classe.DoesNotExist as e:
            return None