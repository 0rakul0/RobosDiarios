
from pdjus.dal.GenericoDao import GenericoDao
from pdjus.modelo.ParteDistribuicao import *
from pdjus.modelo.Distribuicao import Distribuicao
from pdjus.modelo.TipoParte import TipoParte
from util.StringUtil import remove_acentos,remove_varios_espacos

class ParteDistribuicaoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(ParteDistribuicaoDao, self).__init__(ParteDistribuicao)



    def get_por_parte_e_distribuicao_e_tipo_e_oab(self,parte,distribuicao,tipo,oab):
        if not parte or not distribuicao or not tipo or not oab:
            return None
        try:
            return self._classe.select().join(Distribuicao).switch(self._classe).join(TipoParte).switch(self._classe).\
                where(Distribuicao.id == distribuicao.id, TipoParte.id == tipo.id,
                       self._classe.parte == remove_acentos(remove_varios_espacos(parte.upper())), self._classe.numero_oab == oab).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome(self,nome,cache=True):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            if cache:
                    obj = self.get_cached_object(nome)
                    if not obj:
                        obj = self._classe.get(self._classe.parte == nome)
                        if obj:
                            self.add_to_cache(obj)

                    return obj
            else:
                return self._classe.get(self._classe.parte == nome)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome_e_distribuicao_e_tipo(self, nome, distribuicao, tipo):
        try:
            if not distribuicao:
                return None
            return self._classe.select().join(Distribuicao).switch(self._classe).join(TipoParte).switch(self._classe). \
                where(Distribuicao.id == distribuicao.id, TipoParte.id == tipo.id,
                       self._classe.parte == remove_acentos(remove_varios_espacos(nome.upper()))).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_pessoas_juridicas(self):
        try:
            return self._classe.select().\
                where(self._classe.pessoa_juridica == True)
        except self._classe.DoesNotExist as e:
            return None

    def listar_partes_nao_classificadas_rais(self,rank=0,fatia=1,start=None,limit=None):
        try:
            return self.listar(rank=rank,fatia=fatia,limit=limit,start=start).select().join(ParteDistribuicaoRais).where(self._classe.pessoa_juridica == False)
        except self._classe.DoesNotExist as e:
            return None


