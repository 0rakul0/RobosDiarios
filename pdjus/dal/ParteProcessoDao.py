
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Parte import Parte
from pdjus.modelo.ParteProcesso import ParteProcesso
from pdjus.modelo.TipoParte import TipoParte
from pdjus.modelo.Processo import Processo
from util.StringUtil import remove_acentos,remove_varios_espacos


class ParteProcessoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(ParteProcessoDao, self).__init__(ParteProcesso)

    def get_por_parte_e_processo_e_tipo(self,parte,processo,tipo):
        if not parte or not processo or not tipo:
            return None
        try:
            return self.get_por_nome_e_processo_e_tipo(parte.nome,processo,tipo)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome_e_processo_e_tipo(self, nome, processo, tipo):
        try:
            return self._classe.select().join(Parte).switch(self._classe).join(TipoParte).where(self._classe.processo == processo,
                                                                                                TipoParte.id == tipo,
                                                                                                Parte._nome == remove_acentos(remove_varios_espacos(nome.upper()))).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_por_parte_parte_processo(self, processo, parte):
        try:
            return self._classe.select().where(self._classe.processo==processo,self._classe.parte==parte).get()
        except self._classe.DoesNotExist as e:
            return None
