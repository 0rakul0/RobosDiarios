__author__ = 'B249025230'

from pdjus.dal.GenericoDao import GenericoDao, Singleton, JOIN
from pdjus.modelo.Sentenca import Sentenca
from util.StringUtil import remove_acentos,remove_varios_espacos
from pdjus.modelo.Movimento import Movimento


class SentencaDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(SentencaDao, self).__init__(Sentenca)

    def get_por_processo_data_descricao(self,processo,data, descricao):
        try:
            descricao = remove_varios_espacos(remove_acentos(descricao.upper()))

            return self._classe.get((self._classe.processo == processo), (self._classe.data == data), (self._classe._descricao == descricao))
        except self._classe.DoesNotExist as e:
            return None

    def get_por_movimento_vazio(self, rank, fatia):
        return self.listar(rank=rank, fatia=fatia).select().join(Movimento,JOIN.LEFT_OUTER).where(Movimento.id.is_null())


    def listar_provas_regex(self, start, stop, regex):
        query = "SELECT s.descricao as descricao, substring(s.descricao from \'" + regex + "\') as qtd FROM traficodrogas_sp.SENTENCA s " \
                                                                 "LIMIT " + str(stop - start) + " OFFSET " + str(start)

        try:
            res = self.db.execute_sql(query)
            provas = []

            for r in res:
                if r is not None:
                    if r['qtd'] is not None:
                        if r['qtd'].strip() != "":
                            provas.append( (r['qtd'], r['descricao']) )

            return provas
        except self._classe.DoesNotExist as e:
            return None

    def get_por_movimento_situacao_descricao_valor_tipo_moeda(self,movimento,situacao,descricao,valor,tipo_moeda):
        try:
            self._classe.select().join(Movimento).where((Movimento.id == movimento.id),(self._classe._situacao == situacao),
                                                        (self._classe._descricao == descricao),
                                                        (self._classe.valor == valor), (self._classe.tipo_moeda == tipo_moeda))
        except self._classe.DoesNotExist as e:
            return None

    '''
    def listar_por_tag_processo(self, tag):
        try:
            return self._self._classe.join(self._classe.processo).join(His)
        except self._classe.DoesNotExist as e:
            return None
    '''