from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Advogado import Advogado
from util.StringUtil import remove_acentos,remove_varios_espacos


class AdvogadoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(AdvogadoDao, self).__init__(Advogado)

    def get_por_numero_oab(self,numero,cache=True):
        try:
            if numero:
                numero = remove_varios_espacos(remove_acentos(str(numero).upper().replace(' ','')))
                if cache:
                    obj = self.get_cached_object(numero)
                    if not obj:
                        obj = self._classe.get(self._classe._numero_oab == numero)
                        if obj:
                            self.add_to_cache(obj)
                    return obj
                else:
                    return self._classe.get(self._classe._numero_oab == numero)
            return None
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.get(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None