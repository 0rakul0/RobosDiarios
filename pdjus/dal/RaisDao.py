from peewee import JOIN
from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.Empresa import Empresa
from pdjus.modelo.Rais import Rais
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_tracos_pontos_barras_espacos


class RaisDao(GenericoDao, metaclass=Singleton):
    def __init__(self):
        super(RaisDao, self).__init__(Rais)

    def get_por_nome(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))

            return self._classe.get(self._classe._nome == nome)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_razao_social(self,razao_social):
        try:
            razao_social = remove_varios_espacos(remove_acentos(razao_social.upper()))

            return self._classe.get(self._classe.razao_social == razao_social)
        except self._classe.DoesNotExist as e:
            return None

    def list_por_estado(self,uf):
        try:
            return self._classe.select().where(self._classe.uf == uf)
        except self._classe.DoesNotExist as e:
            return None

    def list_por_estado_que_nao_estao_na_tabela_empresa(self,uf):
        try:
            return self._classe.select(self._classe._cnpj).join(Empresa,JOIN.LEFT_OUTER, self._classe._cnpj == Empresa._cnpj).where(self._classe.uf == uf, self._classe._cnpj != None, Empresa._cnpj == None)
        except self._classe.DoesNotExist as e:
            return None


    def get_por_cnpj(self,cnpj):
        try:
            cnpj = remove_tracos_pontos_barras_espacos(cnpj)

            return self._classe.select().where()(self._classe._cnpj == cnpj)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome_corrigido(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))

            return self._classe.select().where(self._classe._nome_corrigido == nome)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_nome_abreviado(self,nome):
        try:
            nome = remove_varios_espacos(remove_acentos(nome.upper()))

            return self._classe.select().where(self._classe._nome_abreviado == nome)
        except self._classe.DoesNotExist as e:
            return None

    def listar_por_cnpj(self,cnpj):
        try:
            cnpj = remove_tracos_pontos_barras_espacos(cnpj)

            return self._classe.select().where(self._classe._cnpj == cnpj)
        except self._classe.DoesNotExist as e:
            return None

    def saveMany(self, raisArray):
        Rais.insert_many(raisArray).execute()
