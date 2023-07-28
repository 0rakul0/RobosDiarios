
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Municipio import Municipio
from util.StringUtil import remove_acentos, remove_varios_espacos


class MunicipioDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(MunicipioDao, self).__init__(Municipio)

    def get_por_nome(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.get(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome_e_estado(self, nome, estado):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.get(self._classe._nome == nome, self._classe.estado == estado)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome_e_estado_e_numero_ibge(self, nome, estado, numero_ibge):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.get(self._classe._nome == nome, self._classe.estado == estado, self._classe.numero_ibge == numero_ibge)
        except self._classe.DoesNotExist as e:
            return None




