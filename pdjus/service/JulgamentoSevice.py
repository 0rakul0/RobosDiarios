from pdjus.conexao.Conexao import Singleton
from pdjus.dal.JulgamentoDao import JulgamentoDao
from pdjus.service.BaseService import BaseService
from pdjus.dal.JuizDao import JuizDao
from pdjus.modelo.Julgamento import  Julgamento
from pdjus.modelo.Juiz import Juiz
from pdjus.service.JuizService import JuizService
from pdjus.service.ProcessoService import ProcessoService


class JulgamentoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(JulgamentoService, self).__init__(JulgamentoDao())

    def preenche_tipo_participantes(self,tipo_participante,processo,juiz):
        if processo.id and juiz.id is not None:
            julgamento = self.dao.get_por_tipo_participante_e_processo_e_juiz(tipo_participante,processo,juiz)

        if julgamento is None:
                julgamento = Julgamento()
                julgamento.tipo_participante = tipo_participante
                julgamento.juiz = juiz
                julgamento.processo = processo
                self.salvar(julgamento)
        return julgamento
