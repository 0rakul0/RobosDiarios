# from pdjus.dal.GenericoDao import GenericoDao,Singleton
# from pdjus.modelo.CnisBPC import CnisBPC
# from util.StringUtil import remove_acentos,remove_varios_espacos,remove_tracos_pontos_barras_espacos
#
#
# class CnisBPCDao(GenericoDao,metaclass=Singleton):
#     def __init__(self):
#         super(CnisBPCDao, self).__init__(CnisBPC)
#
#     def list_processados(self, flag):
#         try:
#              return self._classe.select().where(self._classe.processado == flag).limit(10)
#         except self._classe.DoesNotExist as e:
#             return None
#
#     def list_encontrados(self, flag):
#         try:
#             return self._classe.select().where(self._classe.encontrado == flag)
#         except self._classe.DoesNotExist as e:
#             return None
#
#     def get_by_cpf(self, cpf):
#         try:
#             return self._classe.get(self._classe._cpf == cpf)
#         except self._classe.DoesNotExist as e:
#             return None
