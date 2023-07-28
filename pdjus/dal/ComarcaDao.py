
from pdjus.modelo.Estado import Estado
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Comarca import Comarca
from pdjus.modelo.Tribunal import Tribunal
from util.StringUtil import remove_acentos, remove_varios_espacos


class ComarcaDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(ComarcaDao, self).__init__(Comarca)

    def get_por_codigo_comarca(self,codigo,cache=False):
        try:
            if cache:
                obj = self.get_cached_object(codigo)
                if not obj:
                    obj = self._classe.get(self._classe.codigo_comarca == codigo)
                    if obj:
                        self.add_to_cache(obj)

                return obj
            else:
                return self._classe.get(self._classe.codigo_comarca == codigo)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_codigo_comarca_e_tribunal(self,codigo,tribunal):
        try:
            return self._classe.get(self._classe.codigo_comarca == codigo, self._classe.tribunal == tribunal)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome_comarca(self, nome,cache=False):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            if cache:
                obj = self.get_cached_object(nome)
                if not obj:
                    obj = self._classe.get(self._classe._nome == nome)
                    if obj:
                        self.add_to_cache(obj)

                return obj
            else:
                return self._classe.get(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome_comarca_e_tribunal(self, nome, tribunal):
        try:
            nome = nome.upper()
            return self._classe.select().join(Tribunal).where((self._classe._nome == nome) | (self._classe.codigo_comarca == nome), Tribunal.id == tribunal).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome_formatado(self, nome_formatado):
        try:
            return self._classe.get(self._classe.nome_formatado == nome_formatado)
        except self._classe.DoesNotExist as e:
            return None


