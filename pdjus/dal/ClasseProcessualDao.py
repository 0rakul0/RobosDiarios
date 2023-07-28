from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.ClasseProcessual import ClasseProcessual
from util.StringUtil import remove_acentos,remove_varios_espacos


class ClasseProcessualDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(ClasseProcessualDao, self).__init__(ClasseProcessual)

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
                return self._classe.get(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_nome(self, nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome)).upper()
            return self._classe.get(ClasseProcessual._nome.contains(nome))
        except self._classe.DoesNotExist as e:
            return None

    def get_por_codigo_classe(self, codigo_classe):
        try:
            return self._classe.get(self._classe.codigo_classe_processual == codigo_classe)
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_codigo_classe(self, codigo_classe):
        try:
            with self.auto_session() as session:
                return self._classe.select().where(ClasseProcessual.codigo_classe_processual == codigo_classe)
        except self._classe.DoesNotExist as e:
            return None