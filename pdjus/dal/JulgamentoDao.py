from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Julgamento import Julgamento
from pdjus.modelo.Juiz import Juiz
from util.StringUtil import remove_acentos,remove_varios_espacos

class JulgamentoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(JulgamentoDao, self).__init__(Julgamento)

    def get_por_tipo_participante_e_processo_e_juiz(self, tipo_participante, processo, juiz):
        try:
            return self._classe.select().join(Juiz).where(self._classe.processo == processo,Juiz.id == juiz,
                                                                                                self._classe._tipo_participante == remove_acentos(remove_varios_espacos(tipo_participante.upper()))).get()
        except self._classe.DoesNotExist as e:
            return None


