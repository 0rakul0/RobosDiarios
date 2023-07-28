from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ProcessoServidorDao import ProcessoServidorDao
from pdjus.service.BaseService import BaseService


class ProcessoServidorService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ProcessoServidorService, self).__init__(ProcessoServidorDao())
