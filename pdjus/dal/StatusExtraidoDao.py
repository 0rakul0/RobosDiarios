from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.StatusExtraido import StatusExtraido


class StatusExtraidoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(StatusExtraidoDao, self).__init__(StatusExtraido)

    def get_status_extraido(self, arquivo, extrator):
        try:
            return self._classe.select().where(self._classe.arquivo_id == arquivo.id).filter(self._classe.extrator_id == extrator.id).get()
        except self._classe.DoesNotExist as e:
            return None