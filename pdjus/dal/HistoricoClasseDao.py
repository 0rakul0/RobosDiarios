from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.HistoricoClasse import HistoricoClasse
from pdjus.modelo.Processo import Processo
from pdjus.modelo.Area import Area
from pdjus.modelo.ClasseProcessual import ClasseProcessual
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links

class HistoricoClasseDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(HistoricoClasseDao, self).__init__(HistoricoClasse)

    def get_por_processo_data_tipo_classe_area_motivo(self,processo,data,tipo,classe_processual,area,motivo):
        try:
            if tipo:
                tipo = remove_links(remove_varios_espacos(remove_acentos(tipo.upper())))
            if motivo:
                motivo = remove_links(remove_varios_espacos(remove_acentos(motivo.upper())))
            # alias_processo = aliased(Processo)
            # alias_classe = aliased(ClasseProcessual)
            # alias_area = aliased(Area)
            #return self._classe.join(self._classe.processo).join(self._classe.classe_processual).join(self._classe.area).get((Processo.id == processo.id), (self._classe.data == data),(self._classe._tipo == tipo),(ClasseProcessual.id == classe_processual.id), (Area.id == area.id),(self._classe._motivo == motivo))
            return self._classe.select().join(Processo).join(ClasseProcessual).where(Processo.id == processo.id, self._classe.data == data, self._classe._tipo == tipo, ClasseProcessual.id == classe_processual.id, self._classe._motivo == motivo, Processo.area == area)
        except self._classe.DoesNotExist as e:
            return None