from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.MarcoProcessual import MarcoProcessual
from pdjus.modelo.MarcoProcessualDispositivoLegal import MarcoProcessualDispositivoLegal
from pdjus.modelo.DispositivoLegal import DispositivoLegal
from util.StringUtil import remove_acentos,remove_varios_espacos


class MarcoProcessualDispositivoLegalDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(MarcoProcessualDispositivoLegalDao, self).__init__(MarcoProcessualDispositivoLegal)

    def get_por_marco_processual_e_dispositivo_legal(self,marco_processual,dispositivo_legal):
        if not marco_processual or not dispositivo_legal:
            return None
        try:
            return self._classe.join(self._classe.dispositivo_legal).join(self._classe.marco_processual).\
                get(DispositivoLegal.id == dispositivo_legal.id,
                       MarcoProcessual.id == marco_processual.id)
        except self._classe.DoesNotExist as e:
            return None

        