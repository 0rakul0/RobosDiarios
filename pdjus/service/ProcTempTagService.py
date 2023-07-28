from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ProcTempTagDao import ProcTempTagDao
from pdjus.service.BaseService import BaseService


class ProcTempTagService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ProcTempTagService, self).__init__(ProcTempTagDao())