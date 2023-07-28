from pdjus.conexao.Conexao import Singleton
from pdjus.dal.HistoricoClasseDao import HistoricoClasseDao
from pdjus.modelo.HistoricoClasse import HistoricoClasse
from pdjus.service.AreaService import AreaService
from pdjus.service.BaseService import BaseService
from pdjus.modelo.HistoricoClasse import HistoricoClasse
from pdjus.service.ClasseProcessualService import ClasseProcessualService
from util.StringUtil import remove_varios_espacos


class HistoricoClasseService(BaseService, metaclass=Singleton):

    def __init__(self):
        super(HistoricoClasseService, self).__init__(HistoricoClasseDao())

    def preenche_historico_classes(self, processo,data,tipo,classe_nome,area_nome,motivo):
        classeProcessualService = ClasseProcessualService()
        areaService = AreaService()
        if remove_varios_espacos(motivo).strip() == '-':
            motivo = None
        classe_processual = classeProcessualService.preenche_classe_processual(classe_nome)

        area = areaService.preenche_area(area_nome)

        historico_classe = self.dao.get_por_processo_data_tipo_classe_area_motivo(processo,data,tipo,classe_processual
                                                                                             ,area,motivo)
        if not historico_classe.model:
            historico_classe = HistoricoClasse()
            historico_classe.processo = processo
            historico_classe.data = data
            historico_classe.tipo = tipo
            historico_classe.classe_processual = classe_processual
            historico_classe.area = area
            historico_classe.motivo = motivo
            self.salvar(historico_classe)
        return historico_classe