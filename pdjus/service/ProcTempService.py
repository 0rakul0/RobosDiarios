from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ProcTempDao import ProcTempDao
from pdjus.service.BaseService import BaseService


class ProcTempService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ProcTempService, self).__init__(ProcTempDao())