from pdjus.conexao.Conexao import Singleton
from pdjus.dal.AreaDao import AreaDao
from pdjus.modelo.Area import Area
from pdjus.service.BaseService import BaseService
from util.StringUtil import remove_varios_espacos, remove_acentos


class AreaService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(AreaService, self).__init__(AreaDao())

    def preenche_area(self, nome_area):
        nome_area = remove_varios_espacos(remove_acentos(nome_area.strip()))
        area = self.dao.get_por_nome(nome_area)
        if area is None:
            area = Area()
            area.nome = nome_area
            self.salvar(area)
        return area