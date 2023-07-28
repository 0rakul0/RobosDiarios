from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Parte import Parte
from pdjus.modelo.SituacaoProcesso import SituacaoProcesso
from pdjus.modelo.Processo import Processo
from pdjus.modelo.Situacao import Situacao

class SituacaoProcessoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(SituacaoProcessoDao, self).__init__(SituacaoProcesso)


    def get_por_situacao_e_processo(self,situacao,processo):
        try:
            if not situacao or not processo:
                return None

            return self._classe.select().join(Processo).switch(self._classe).join(Situacao).where(self._classe.processo == processo).where(self._classe.situacao == situacao).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_por_situacao_e_processo_e_data(self,situacao,processo,data):
        try:
            if not situacao or not processo:
                return None

            return self._classe.join(Processo).switch(self._classe).join(Situacao).\
                get(Processo.id == processo, Situacao.id == situacao, self._classe.data == data )
        except self._classe.DoesNotExist as e:
            return None

    def get_por_situacao_e_processo_e_parte_e_data(self, situacao, processo, parte, data):
        try:
            if not situacao or not processo or not data:
                return None
            else:
                if not parte:
                    return self.get_por_situacao_e_processo(situacao,processo)

                return self._classe.join(Processo).switch(self._classe).join(Situacao).switch(self._classe).\
                    join(Parte).\
                    get(Processo.id == processo, Situacao.id == situacao,
                           Parte.id == parte, self._classe.data == data)
        except self._classe.DoesNotExist as e:
            return None