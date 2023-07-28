from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Juiz import Juiz
from util.StringUtil import remove_acentos,remove_varios_espacos



class JuizDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(JuizDao, self).__init__(Juiz)

    def get_por_nome(self,nome):
        try:
            if nome:
                nome = remove_varios_espacos(remove_acentos(nome.upper()))
                return self._classe.select().where(self._classe._nome == nome).get()
            else:
                return None
        except self._classe.DoesNotExist as e:
            return None