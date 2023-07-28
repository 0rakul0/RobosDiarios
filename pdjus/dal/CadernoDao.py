from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Diario import Diario
from pdjus.modelo.Caderno import Caderno
from util.StringUtil import remove_acentos, remove_varios_espacos


class CadernoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(CadernoDao, self).__init__(Caderno)

    def get_por_diario_e_nome(self, diario, nome,cache=False):
        try:
            if not nome:
                return None
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            if cache:
                obj = self.get_cached_object(str(diario.id)+nome)
                if not obj:
                    obj = self._classe.select().join(Diario).where(self._classe._nome == nome,
                                                                              Diario._nome == diario.nome,
                                                                              Diario.data == diario.data).get()
                    if obj:
                        self.add_to_cache(obj)
                return obj
            else:
                return self._classe.select().join(Diario).where(self._classe._nome == nome,
                                                                          Diario._nome == diario.nome,
                                                                          Diario.data == diario.data).get()
        except self._classe.DoesNotExist as e:
            return None

