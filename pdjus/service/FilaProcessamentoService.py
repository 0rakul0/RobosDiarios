from pdjus.conexao.Conexao import Singleton
from pdjus.dal.FilaProcessamentoDao import FilaProcessamentoDao
from pdjus.service.BaseService import BaseService

class FilaProcessamentoService(BaseService, metaclass=Singleton):

    def __init__(self):
        super(FilaProcessamentoService, self).__init__(FilaProcessamentoDao())
