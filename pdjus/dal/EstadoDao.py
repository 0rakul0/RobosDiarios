from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Estado import Estado

class EstadoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(EstadoDao, self).__init__(Estado)

    def get_por_sigla(self, sigla,cache=False):
        try:
            if cache:
                    obj = self.get_cached_object(sigla)
                    if not obj:
                        obj = self._classe.get(self._classe.sigla == sigla)
                        if obj:
                            self.add_to_cache(obj)
                    return obj
            else:
                return self._classe.get(self._classe.sigla == sigla)
        except self._classe.DoesNotExist as e:
            return None
