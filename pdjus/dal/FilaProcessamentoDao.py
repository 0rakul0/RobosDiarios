from pdjus.dal.GenericoDao import *
from pdjus.modelo.FilaProcessamento import FilaProcessamento

class FilaProcessamentoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(FilaProcessamentoDao, self).__init__(FilaProcessamento)

    def lista_nao_processados_por_tribunal(self, tribunal_id, fatia=1, rank=0, random=False, secao=None):
        # return self._classe.select().where(self._classe.tribunal_id == tribunal_id)
        if random:
            return self.listar(fatia=fatia, rank=rank).select().where(
                self._classe.processado == False, self._classe.tribunal_id == tribunal_id).order_by(fn.Random())
        elif secao:
            return self.listar(fatia=fatia, rank=rank).select().where(
                self._classe.processado == False, self._classe.tribunal_id == tribunal_id, self._classe.secao == secao)
        else:
            return self.listar(fatia=fatia, rank=rank).select().where(
                self._classe.processado == False, self._classe.tribunal_id == tribunal_id)