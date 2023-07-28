from pdjus.conexao.Conexao import Singleton
from pdjus.dal.MarcadorDao import MarcadorDao
from pdjus.modelo.Marcador import Marcador
from pdjus.service.BaseService import BaseService

class MarcadorService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(MarcadorService, self).__init__(MarcadorDao())

    def preenche_marcador(self, nome):
        marcador = None
        if nome != '':
            marcador = self.dao.get_por_nome(nome)
            if not marcador:
                marcador = Marcador()
                marcador._nome = nome.upper()
                self.salvar(marcador)

        return marcador