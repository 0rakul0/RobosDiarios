import datetime

from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Peticao import Peticao
from pdjus.modelo.Processo import Processo
from util.StringUtil import remove_acentos, remove_varios_espacos



class PeticaoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(PeticaoDao, self).__init__(Peticao)

    def get_por_processo_data_descricao_tipo(self, processo, data, descricao, tipo):
        try:
            data_buscar = data if type(data) is datetime.date else data.date()
            if descricao:
                descricao = remove_acentos(remove_varios_espacos(descricao.upper()))
            if tipo:
                tipo = remove_acentos(remove_varios_espacos(tipo.upper()))
            return self._classe.select().join(Processo).where(Processo.id == processo, self._classe.data == data_buscar,
                                                       self._classe._descricao == descricao).get()
                                                       #s,elf._classe._tipo == tipo)

        except self._classe.DoesNotExist as e:
            return None

    def get_por_processo(self, processo):
        try:
            return self._classe.get((self._classe.processo == processo))
        except self._classe.DoesNotExist as e:
            return None
