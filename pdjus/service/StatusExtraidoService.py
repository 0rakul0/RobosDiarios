import datetime

from pdjus.conexao.Conexao import Singleton
from pdjus.dal.StatusExtraidoDao import StatusExtraidoDao
from pdjus.modelo.StatusExtraido import StatusExtraido
from pdjus.service.BaseService import BaseService


class StatusExtraidoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(StatusExtraidoService, self).__init__(StatusExtraidoDao())

    def preenche_status_extraido(self, arquivo, extrator, data=datetime.datetime.now(), tag=None):
        status_extraido = StatusExtraido()
        status_extraido.arquivo = arquivo
        status_extraido.extrator = extrator
        status_extraido.data = data
        self.salvar(status_extraido,tag=tag)

    def is_arquivo_extraido(self, arquivo, extrator):
        return self.dao.get_status_extraido(arquivo, extrator)