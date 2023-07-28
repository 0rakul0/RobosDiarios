from pdjus.conexao.Conexao import Singleton
from pdjus.dal.EnderecoDao import EnderecoDao
from pdjus.service.BaseService import BaseService


class EnderecoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(EnderecoService, self).__init__(EnderecoDao())