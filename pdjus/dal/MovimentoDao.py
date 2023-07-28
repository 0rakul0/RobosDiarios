from pdjus.dal.GenericoDao import *
from pdjus.modelo.BlocoQuadro import BlocoQuadro
from pdjus.modelo.Movimento import Movimento
from pdjus.modelo.ClasseProcessual import ClasseProcessual
from pdjus.modelo.NotaExpediente import NotaExpediente
from pdjus.modelo.Processo import Processo
from pdjus.modelo.MovimentoMarcador import MovimentoMarcador
from pdjus.modelo.Marcador import Marcador
from pdjus.dal.MarcadorDao import MarcadorDao
from pdjus.modelo.Situacao import Situacao
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links
from pdjus.modelo.TipoMovimento import TipoMovimento
from datetime import datetime
import hashlib
from util.RegexUtil import RegexUtil

class MovimentoDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(MovimentoDao, self).__init__(Movimento)

        # self.__regex_quadro_artigo = '((ART(\.|IGO))\s(52|7|96|102)\D|(QUADRO|RELACAO|EDITAL(\sDE\sCONVOCACAO)?)\s(GERAL)?\s?DE\sCREDOR(ES)?).*?(CLASSE|QUIROGRA\w*|TRABALH\w*|TRIBUT\w*|GARANTIA\sREAL|CR[ÉE]DITO)'
        # self.__regex_quadro_simples = 'EDITAL.*?(\sD[OE]S?\sCREDORES)'
        # self.__regex_quadro_excluir_encerramento = '(ENCERRAMENTO|DECRETA[ÇC][AÃ]O)\s+D[AE]\s+FAL[ÊE]NCIA'
        # self.__regex_quadro_indicacao_relacao = '(RELA[ÇC][ÃA]O|ROL|LISTA|QUADRO)\s\w*\sCREDOR(ES)?\sAPRESENTAD'
        self.__regex_cnpj = '(\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2})'
        # self.__regex_moedas = 'BRL|USD|R\$|US\$|U\$|EUR|£|GBP|€|¥|JPY'

    def get_por_processo_data_tipo_movimento_texto(self, processo, data, tipo_movimento, texto, hash_search=False):
        try:
            if texto:
                texto = remove_links(remove_varios_espacos(remove_acentos(texto.upper())))
            if not hash_search or not texto:
                return self._classe.select().join(Processo).switch(self._classe).join(TipoMovimento).where((Processo.id == processo), (self._classe.data == data.date()), (TipoMovimento.id == tipo_movimento), (self._classe._texto == texto)).get()
            elif data:
                hash_texto = hashlib.md5(texto.encode('utf-8')).hexdigest()
                return self._classe.select().join(Processo).switch(self._classe).join(TipoMovimento).where((Processo.id == processo), (self._classe.data == data.date()), (TipoMovimento.id == tipo_movimento), (self._classe._hash_texto == hash_texto)).get()
            else:
                hash_texto = hashlib.md5 (texto.encode ('utf-8')).hexdigest ()
                return self._classe.select ().join (Processo).switch (self._classe).join (TipoMovimento).where (
                    (Processo.id == processo), (self._classe.data == data),
                    (TipoMovimento.id == tipo_movimento), (self._classe._hash_texto == hash_texto)).get ()
        except self._classe.DoesNotExist as e:
            return None

    def listar_movimentos_por_marcador(self, nome_marcador):
        try:
            marcadordao = MarcadorDao()
            marcador = marcadordao.get_por_nome(nome_marcador)
            if marcador:
                return self.listar().select().join(MovimentoMarcador, on=self._classe.id == MovimentoMarcador.movimento).join(Marcador, on=MovimentoMarcador.marcador == Marcador.id).where(Marcador._nome == nome_marcador)
            else:
                return None
        except self._classe.DoesNotExist:
            return None

    def listar_movimentos_por_processo_e_marcador(self, processo, nome_marcador):
        try:
            marcadordao = MarcadorDao()
            marcador = marcadordao.get_por_nome(nome_marcador)
            if marcador:
                return self.listar().select().join(MovimentoMarcador, on=self._classe.id == MovimentoMarcador.movimento).join(Marcador, on=MovimentoMarcador.marcador == marcador.id).where(self._classe.processo == processo.id)
            else:
                return None
        except self._classe.DoesNotExist:
            return None

    def get_por_processo_data_tipo_movimento(self,processo,data,tipo_movimento):
        try:
            return self._classe.select().join(Processo).where((Processo.id == processo.id),(self._classe.data == data.date()), (self._classe.tipo_movimento == tipo_movimento)).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_por_texto(self, texto):
        try:
            if texto:
                texto = remove_links(remove_varios_espacos(remove_acentos(texto.upper())))

                return self._classe.get(self._classe._texto.contains(texto))
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_lista_de_id(self,rank=0,fatia=1,limit=None,lista_ids=[]):
        try:
            return self.listar(rank=rank, fatia=fatia, limit=limit).select().join(Processo).join(DadoExtraido).join(HistoricoDado).\
                where((self._classe.id << lista_ids))
        except self._classe.DoesNotExist as e:
            return None
    def listar_possiveis_quadro_credores(self,rank=0,fatia=1,limit=None,tag='FALENCIAS'):
         try:
            if tag:
                tag = self._normalizar_marcador(tag)
            return self.listar(rank=rank,fatia=fatia,limit=limit).select().join(BlocoQuadro,JOIN.LEFT_OUTER).switch(self._classe).join(Processo).join(DadoExtraido).join(HistoricoDado). \
                where(
                (   (HistoricoDado.marcador == tag) &
                    # (Processo.id << ['4762',
                    #                 '164019',
                    #                 '182276',
                    #                 '210325',
                    #                 '217236',
                    #                 '421937',
                    #                 '424711',
                    #                 '442857',
                    #                 '444486',
                    #                 '14658432',
                    #                 '15130297',
                    #                 '15436822',
                    #                 '16258912',
                    #                 '16557209',
                    #                 '18024679',
                    #                 '18026390',
                    #                 '18028360',
                    #                 '18028420',
                    #                 '18028872',
                    #                 '18032084',
                    #                 '18032090']) &
                    (Processo.processo_principal.is_null(True)) &
                    (Processo.data_atualizacao.is_null(False)) &
                    (self._classe._texto.regexp(RegexUtil.regex_moedas)) &
                    (self._classe._texto.contains('CREDOR')) &
                    # (
                        (self._classe._texto.regexp(RegexUtil.regex_quadro_artigo_para_sql)) &
                        (BlocoQuadro.id == None)
                        #& (neg_regexp(self._classe._texto,RegexUtil.regex_anti_quadro_para_sql))#TIREI PRA SIMPLIFICAR

                        #|
                        # (
                        #     (self._classe._texto.regexp(RegexUtil.regex_quadro_simples)) &
                        #     # (
                        #     #         (neg_regexp(self._classe._texto, RegexUtil.regex_quadro_excluir_encerramento)) |
                        #     #         (self._classe._texto.regexp(RegexUtil.regex_quadro_indicacao_relacao))
                        #     # )
                        # )
                    # )
                )
            )
         except self._classe.DoesNotExist as e:
             return None

    def listar_movimentos_com_cnpj(self):
        try:
            return self._classe.join(self._classe.processo).get(Processo.processo_principal_id == None,self._classe._texto.regexp(self.__regex_cnpj))
        except self._classe.DoesNotExist as e:
            return None

    def listar_possiveis_sentencas_habilitacao_credito_deferidas(self,rank=0,fatia=1,limit=None,tag='FALENCIAS'):
        try:
            if tag:
                tag = self._normalizar_marcador(tag)
            return self.listar(rank=rank, fatia=fatia, limit=limit).select().join(TipoMovimento).switch(
                self._classe).join(Processo).join(DadoExtraido).join(HistoricoDado).switch(Processo).join(ClasseProcessual).where(
                (HistoricoDado.marcador == tag) &
                (Processo.data_atualizacao.is_null(False)) &
                (ClasseProcessual._nome.contains('CREDITO')) &
                (#verificações no tipo_movimento
                    TipoMovimento._nome.contains('DECISAO') |
                    TipoMovimento._nome.contains('JULG') |
                    TipoMovimento._nome.contains('SENTENCA') |
                    TipoMovimento._nome.contains('PROFERID') |
                    TipoMovimento._nome.contains('DESPACHO')
                ) &

                (#Verificações no texto do movimento

                    (self._classe._texto.regexp(RegexUtil.regex_habilitacao_deferidos_padrao1)) |
                    (self._classe._texto.regexp(RegexUtil.regex_habilitacao_deferidos_padrao2)) |
                    (self._classe._texto.regexp(RegexUtil.regex_habilitacao_deferidos_padrao3))
                )
            )
        except self._classe.DoesNotExist as e:
            return None

    def listar_possiveis_sentencas_habilitacao_credito_indeferidas(self,rank=0,fatia=1,limit=None,tag='FALENCIAS'):
        try:
            if tag:
                tag = self._normalizar_marcador(tag)
            return self.listar(rank=rank, fatia=fatia, limit=limit).select().join(TipoMovimento).switch(
                self._classe).join(Processo).join(DadoExtraido).join(HistoricoDado).switch(Processo).join(ClasseProcessual).where(
                (HistoricoDado.marcador == tag) &
                (Processo.data_atualizacao.is_null(False)) &
                (ClasseProcessual._nome.contains('CREDITO')) &
                (  # verificações no tipo_movimento
                        TipoMovimento._nome.contains('DECISAO') |
                        TipoMovimento._nome.contains('JULG') |
                        TipoMovimento._nome.contains('SENTENCA') |
                        TipoMovimento._nome.contains('PROFERID') |
                        TipoMovimento._nome.contains('DESPACHO')
                ) &

                (  # Verificações no texto do movimento
                    (self._classe._texto.regexp(RegexUtil.regex_habilitacao_indeferidos_padrao1)) |
                    (self._classe._texto.regexp(RegexUtil.regex_habilitacao_indeferidos_padrao2)) |
                    (self._classe._texto.regexp(RegexUtil.regex_habilitacao_indeferidos_padrao3)) |
                    (self._classe._texto.regexp(RegexUtil.regex_habilitacao_indeferidos_padrao4)) |
                    (self._classe._texto.regexp(RegexUtil.regex_habilitacao_indeferidos_padrao5))
                )
            )
        except self._classe.DoesNotExist as e:
            return None
