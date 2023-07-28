from pdjus.conexao.Conexao import Singleton
from pdjus.dal.AudienciaDao import AudienciaDao
from pdjus.modelo.Audiencia import Audiencia
from pdjus.service.BaseService import BaseService


class AudienciaService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(AudienciaService, self).__init__(AudienciaDao())

    def preenche_audiencia(self, processo, data, texto, status, quantidade_pessoas):
        audiencia = None
        if processo.id is not None:
            audiencia = self.dao.get_por_processo_data_descricao_status(processo, data, texto,status)
        if audiencia is None:
            audiencia = Audiencia()
            audiencia.data = data
            audiencia.descricao = texto
            audiencia.status = status
            audiencia.quantidade_pessoas = quantidade_pessoas
            audiencia.processo = processo
            self.salvar(audiencia)
        return audiencia