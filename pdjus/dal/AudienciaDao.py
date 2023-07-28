from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Audiencia import Audiencia
from util.StringUtil import remove_acentos, remove_varios_espacos



class AudienciaDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(AudienciaDao, self).__init__(Audiencia)

    def get_por_processo_data_descricao(self, processo, data, descricao):
        try:
            descricao = remove_acentos(remove_varios_espacos(descricao.upper()))
            return self._classe.get((self._classe.processo == processo),
                                                        (self._classe.data == data.date()),
                                                        (self._classe._descricao == descricao))
        except self._classe.DoesNotExist as e:
            return None

    def get_por_processo_data_descricao_status_qtd_pessoas(self, processo, data, descricao, status, qtd_pessoas):
        try:
            descricao = remove_acentos(remove_varios_espacos(descricao.upper()))
            if status:
                status= remove_acentos(remove_varios_espacos(status.upper()))
            if qtd_pessoas:
                qtd_pessoas = remove_acentos(remove_varios_espacos(qtd_pessoas.upper()))
            return self._classe.get((self._classe.processo == processo),
                                                        (self._classe.data == data),
                                                        (self._classe._descricao == descricao),
                                                        (self._classe._status == status),
                                                        (self._classe._quantidade_pessoas == qtd_pessoas))
        except self._classe.DoesNotExist as e:
            return None

    def get_por_processo_data_descricao_status(self, processo, data, descricao, status):
        try:
            descricao = remove_acentos(remove_varios_espacos(descricao.upper()))
            if status:
                status= remove_acentos(remove_varios_espacos(status.upper()))
            return self._classe.get((self._classe.processo == processo),
                                                        (self._classe.data == data),
                                                        (self._classe._descricao == descricao),
                                                        (self._classe._status == status))
        except self._classe.DoesNotExist as e:
            return None

    def get_por_processo(self, processo):
        try:
            return self._classe.get((self._classe.processo == processo))
        except self._classe.DoesNotExist as e:
            return None
