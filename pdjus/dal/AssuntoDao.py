from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Assunto import Assunto
from util.StringUtil import remove_acentos,remove_varios_espacos


class AssuntoDao(GenericoDao, metaclass=Singleton):
    def __init__(self):
        super(AssuntoDao, self).__init__(Assunto)

    def get_por_nome(self,nome,cache=False):
        try:
            nome = remove_varios_espacos(remove_acentos(nome)).upper()

            if cache:
                obj = self.get_cached_object(nome)
                if not obj:
                    obj = self._classe.get(self._classe._nome == nome)
                    if obj:
                        self.add_to_cache(obj)
                return obj
            else:
                obj = self._classe.get(self._classe._nome == nome)

                if not obj:
                    print('Novo assunto: ' + nome)
                return obj
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_nome(self, nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome)).upper()
            return self._classe.get(Assunto._nome.contains(nome))
        except self._classe.DoesNotExist as e:
            return None