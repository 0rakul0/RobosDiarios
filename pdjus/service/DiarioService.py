import datetime

from pdjus.conexao.Conexao import Singleton
from pdjus.dal.DiarioDao import DiarioDao
from pdjus.modelo.Diario import Diario
from pdjus.service.BaseService import BaseService
from util.StringUtil import remove_acentos, remove_varios_espacos


class DiarioService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(DiarioService, self).__init__(DiarioDao())

    def preenche_diario(self, nome, data):
        if type(data) is str:
            data = datetime.datetime.strptime(data,"%Y_%m_%d")
        nome = remove_varios_espacos(remove_acentos(nome))

        diario = self.dao.get_por_nome_e_data(nome, data,cache=True)

        if not diario:
            diario = Diario()
            diario.nome = nome
            diario.data = data
            self.salvar(diario)

        return diario