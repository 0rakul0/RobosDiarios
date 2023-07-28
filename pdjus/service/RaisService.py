from pdjus.conexao.Conexao import Singleton
from pdjus.dal.RaisDao import RaisDao
from pdjus.service.BaseService import BaseService


class RaisService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(RaisService, self).__init__(RaisDao())

