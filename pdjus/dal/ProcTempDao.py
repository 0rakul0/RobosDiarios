
from pdjus.dal.GenericoDao import *
from pdjus.modelo.ProcTemp import ProcTemp
from pdjus.modelo.ProcTempTag import ProcTempTag
from util.StringUtil import remove_varios_espacos, remove_acentos


class ProcTempDao(GenericoDao, metaclass=Singleton):
    def __init__(self):
        super(ProcTempDao, self).__init__(ProcTemp)

    def get_npus(self):
        try:
            return self._classe.select().where(self._classe._npu != None)
        except self._classe.DoesNotExist as e:
            return None

    def get_npus_por_tag(self, tag, fatia=1, rank=0):
        try:
            # return self._classe.select().where(self._classe.tag == tag, self.mod(self._classe.id, fatia) == rank, self._classe._numero == '22280278472')
            return self._classe.select().where(self._classe.tag == tag, self.mod(self._classe.id, fatia) == rank)
        except self._classe.DoesNotExist as e:
            return None
    def get_npus_nao_processados_por_tag(self, tag, fatia=1, rank=0):
        try:
            # return self._classe.select().where(self._classe.tag == tag, self.mod(self._classe.id, fatia) == rank, self._classe._numero == '22280278472')
            return self._classe.select().where(self._classe.tag == tag, self.mod(self._classe.id, fatia) == rank, self._classe.processado == False)
        except self._classe.DoesNotExist as e:
            return None

    # def get_por_npu(self, npu):
    #     try:
    #         if npu.strip() == '' or len(npu)<16:
    #             return None
    #         else:
    #             return self._classe.select().where(self._classe._npu == remove_varios_espacos(remove_acentos(npu.replace(' ', '').replace('/', '').replace('.', '').replace('-', '')))).get()
    #     except self._classe.DoesNotExist as e:
    #         return None

    def get_por_numero(self,numero):
        try:
            if numero.strip() == '':
                return None
            else:
                return self._classe.select().where(self._classe._numero == remove_varios_espacos(remove_acentos(numero.replace(
                ' ', '').replace('/', '').replace('.', '').replace('-', '')))).get()
        except self._classe.DoesNotExist as e:
            return None
    # def get_por_numero_processo(self, numero):
    #     try:
    #         if numero.strip() == '':
    #             return None
    #         else:
    #             return self._classe.select().where(self._classe._numero_processo == remove_varios_espacos(remove_acentos(numero.replace(
    #             ' ', '').replace('/', '').replace('.', '').replace('-', '')))).get()
    #     except self._classe.DoesNotExist as e:
    #         return None


    # def get_por_numero_processo_ou_npu(self, numero):
    #     if numero:
    #         numero = remove_varios_espacos(
    #             remove_acentos(numero.replace(' ', '').replace('/', '').replace('.', '').replace('-', '')))
    #
    #         p = self.get_por_npu(numero[:16])
    #         if p is None:
    #             p = self.get_por_numero_processo(numero)
    #         return p
    #     return None

    def get_por_numero(self, numero):
        try:
            if numero.strip() == '':
                return None
            else:
                return self._classe.select().where(self._classe._numero == remove_varios_espacos(remove_acentos(numero.replace(
                ' ', '').replace('/', '').replace('.', '').replace('-', '')))).get()
        except self._classe.DoesNotExist as e:
            return None


    def listar_por_ano(self, ano):
        try:
            return self._classe.select().where(self._classe.ano == ano)
        except self._classe.DoesNotExist as e:
            return None

    def listar_nao_processados(self, tag=None, fatia=1, rank=0, limit = None, random = False):
        try:
            if tag:
                return self.listar(fatia=fatia,rank=rank,limit=limit, random=random).select().join(ProcTempTag).where(self._classe.processado == False, ProcTempTag.tag == tag)
            else:
                return self.listar(fatia=fatia, rank=rank, limit=limit, random=random).select().where(
                    self._classe.processado == False)
        except self._classe.DoesNotExist as e:
            return None

    def listar_processados_e_nao_encontrados(self, tag,fatia=1, rank=0,limit = None):
        try:
            return self.listar(fatia=fatia,rank=rank,limit=limit,tag=tag).select().where(self._classe.processado == True, self._classe.encontrado == False )
        except self._classe.DoesNotExist as e:
            return None

    def listar_com_numero_padrao_final(self, tag, fatia=1, rank=0, limit = None, numero_padrao_final='0000'):
        try:
            return self.listar(fatia=fatia,rank=rank,limit=limit,tag=tag).select().where( self._classe._numero.endswith(numero_padrao_final), self._classe.encontrado == False)
        except self._classe.DoesNotExist as e:
            return None