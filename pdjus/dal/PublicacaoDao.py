from pdjus.modelo.ClasseProcessual import ClasseProcessual
from pdjus.modelo.Diario import Diario
from pdjus.modelo.HistoricoDado import HistoricoDado
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Publicacao import Publicacao

class PublicacaoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(PublicacaoDao, self).__init__(Publicacao)


    def listar_tag(self, tag):
        try:
            tag = self._normalizar_marcador(tag)

            return self._classe.select().join(self._classe.dado_extraido).join(HistoricoDado).join(
                self._classe.caderno).join(Diario).join(self._classe.classe_processual).where(
                HistoricoDado.marcador == tag).order_by(Diario.data, ClasseProcessual._nome)
        except self._classe.DoesNotExist as e:
            return None

    def listar_tag_limite(self, tag, start, stop):
        try:
            tag = self._normalizar_marcador(tag)

            return self._classe.select().join(self._classe.dado_extraido).join(HistoricoDado).join(
                self._classe.caderno).join(Diario).join(self._classe.classe_processual).where(
                HistoricoDado.marcador == tag).slice(start, stop)
        except self._classe.DoesNotExist as e:
            return None