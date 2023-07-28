
from pdjus.dal.GenericoDao import *
from pdjus.modelo.Caderno import Caderno
from pdjus.modelo.Distribuicao import Distribuicao
from pdjus.modelo.ClasseProcessual import ClasseProcessual
from pdjus.modelo.Diario import Diario
from pdjus.modelo.Processo import Processo
from util.StringUtil import remove_acentos, remove_varios_espacos


class DiarioDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(DiarioDao, self).__init__(Diario)

    def ultima_data_distribuicao_atualizada(self, tag):
        try:
            tag = self._normalizar_marcador(tag)
            lista = list(self._classe.select(fn.MAX(self._classe.data).alias("data")).join(Caderno).join(Distribuicao).join(DadoExtraido).join(HistoricoDado).switch(Distribuicao).join(Processo).where(HistoricoDado.marcador == tag,self._classe.data <= datetime.today().date()))
            if len(lista) > 0 and lista[0].data:
                return lista[0].data
            return datetime(year=2005, month=1, day=1).date()
        except self._classe.DoesNotExist as e:
            return None

    def ultima_data_diario_atualizada(self, tag,classe_processual=None):
        try:
            tag = self._normalizar_marcador(tag)
            if not classe_processual:
                lista = list(self._classe.select(fn.MAX(self._classe.data).alias("data")).join(Caderno).join(Distribuicao).join(Processo).join(DadoExtraido).join(HistoricoDado)
                         .where(HistoricoDado.marcador == tag,self._classe.data <= datetime.today().date(),self._classe.data >= Distribuicao.data_distribuicao))
            else:
                neg_classe_processual = None
                if classe_processual and "!" in classe_processual:
                    neg_classe_processual = classe_processual.split("!")[1]

                    classe_processual = classe_processual.split("!")[0]

                consulta = self._classe.select(fn.MAX(self._classe.data).alias("data")).join(Caderno).join(Distribuicao).join(ClasseProcessual).switch(Distribuicao).join(Processo).join(DadoExtraido).join(HistoricoDado).where(HistoricoDado.marcador == tag,ClasseProcessual._nome.regexp(classe_processual), self._classe.data <= datetime.today().date())
                if neg_classe_processual:
                    consulta = consulta.select().where(neg_regexp(ClasseProcessual._nome,neg_classe_processual))
                lista = list(consulta)
            if len(lista) > 0 and lista[0].data:
                return lista[0].data
            return datetime(year=2005, month=10, day=1).date()
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome_e_data(self, nome, data,cache=False):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            if cache:
                obj = self.get_cached_object(nome+str(data))
                if not obj:
                    if data:
                        obj = self._classe.get(self._classe._nome == nome, self._classe.data == data.date())
                    else:
                        obj = self._classe.get(self._classe._nome == nome, self._classe.data == None)

                    if obj:
                        self.add_to_cache(obj)
                return obj
            else:
                return self._classe.get(self._classe._nome == nome, self._classe.data == data.date())
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome_ano_mes(self, nome, ano, mes):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.select().where(self._classe._nome == nome, self._classe.data.year == ano, self._classe.data.month == mes)
        except self._classe.DoesNotExist as e:
            return None

    def get_mais_recente(self, nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.get(self._classe._nome == nome).\
                order_by(self._classe.data.desc())
        except self._classe.DoesNotExist as e:
            return None


    def get_por_nome(self, nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))
            return self._classe.get(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None


    def listar_tipos(self):
        try:
            return self._classe.get(fn.distinct(self._classe._nome))
        except self._classe.DoesNotExist as e:
            return None
