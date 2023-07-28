from pdjus.conexao.Conexao import Singleton
from pdjus.dal.NotaExpedienteDao import NotaExpedienteDao
from pdjus.modelo.NotaExpediente import NotaExpediente
from pdjus.service.BaseService import BaseService
from pdjus.service.MovimentoService import MovimentoService


class NotaExpedienteService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(NotaExpedienteService, self).__init__(NotaExpedienteDao())

    def preenche_nota_expediente(self, processo, cod_ano, data, texto, movimento=None):
        movimentoService = MovimentoService()

        nota = self.dao.get_por_movimento_cod_ano_data(movimento,cod_ano, data)
        if not nota:
            nota = NotaExpediente()
            nota.cod_ano = cod_ano
            nota.data = data
            nota.texto = texto
            if not movimento:
                movimento = movimentoService.preenche_movimento(processo,nota.data,nota_expediente=nota)
            nota.movimento = movimento
            self.salvar(nota)