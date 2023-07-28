from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ClasseProcessualDao import ClasseProcessualDao
from pdjus.dal.TipoParteDao import TipoParteDao
from pdjus.service.BaseService import BaseService
from util.StringUtil import remove_acentos
from pdjus.modelo.TipoParte import TipoParte

class TipoParteService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(TipoParteService, self).__init__(TipoParteDao())

    def preenche_tipo_parte(self,nome):
        tipo = self.dao.get_por_nome(remove_acentos(nome))
        if tipo is None:
            tipo = TipoParte()
            tipo.nome = nome
            self.salvar(tipo)
        return tipo