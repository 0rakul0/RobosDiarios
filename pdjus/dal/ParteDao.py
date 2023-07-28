from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Parte import Parte
from util.StringUtil import remove_acentos,remove_varios_espacos



class ParteDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(ParteDao, self).__init__(Parte)

    def get_por_nome(self,nome,cache=True):
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

    def list_por_nome_like(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.get(self._classe._nome.contains('{}'.format(nome)))
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome_corrigido(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.select().where(self._classe._nome_corrigido == nome)
        except self._classe.DoesNotExist as e:
            return None

    def lista_por_nome(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.select().where(self._classe._nome_abreviado == nome)
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_nome_com_regex_match(self,regex):
        try:
            return self._classe.select().where(self._classe._nome.regexp(regex))
        except self._classe.DoesNotExist as e:
            return None

    def lista_parte_sem_genero(self, inclui_unknown=False):
        if inclui_unknown:
            return self._classe.select().where((self._classe.genero.is_null()) | (self._classe.genero == 'U'))
        else:
            return self._classe.select().where(self._classe.genero.is_null())