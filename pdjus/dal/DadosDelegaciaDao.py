
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.DadosDelegacia import DadosDelegacia
# from util.StringUtil import remove_acentos, remove_varios_espacos


class DadosDelegaciaDao(GenericoDao, metaclass = Singleton):
    def __init__(self):
        super(DadosDelegaciaDao, self).__init__(DadosDelegacia)

    def get_por_numero(self, numero):
        try:
            return self._classe.get(self._classe._numero == numero)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_numero_e_municipio(self, numero, municipio):
        try:
            return self._classe.get(
                self._classe._numero == numero,
                self._classe.municipio == municipio)

        except self._classe.DoesNotExist as e:
            return None





