from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.MarcoProcessual import MarcoProcessual
from pdjus.modelo.TipoMarcoProcessual import TipoMarcoProcessual
from pdjus.modelo.Movimento import Movimento
# from pdjus.modelo.NotaExpediente import NotaExpediente
from util.StringUtil import remove_acentos,remove_varios_espacos


class MarcoProcessualDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(MarcoProcessualDao, self).__init__(MarcoProcessual)

    def get_por_movimento_e_tipo(self,movimento,tipo_marco_processual):
        if not movimento or not tipo_marco_processual:
            return None
        try:
            return self._classe.join(self._classe.movimento).join(self._classe.tipo_marco_processual).\
                get(Movimento.id == movimento.id,
                       TipoMarcoProcessual.id == tipo_marco_processual.id)
        except self._classe.DoesNotExist as e:
            return None

    # def get_por_nota_expediente_e_tipo(self,nota_expediente,tipo_marco_processual):
    #     if not nota_expediente or not tipo_marco_processual:
    #         return None
    #     try:
    #         return self._self._classe.join(self._classe.nota_expediente).join(self._classe.tipo_marco_processual).\
    #             filter(NotaExpediente.id == nota_expediente.id,
    #                    TipoMarcoProcessual.id == tipo_marco_processual.id).first()
    #     except self._classe.DoesNotExist as e:
    #         return None


