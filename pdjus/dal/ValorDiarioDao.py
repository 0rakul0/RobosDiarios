#
# from pdjus.dal.GenericoDao import GenericoDao,Singleton
# from pdjus.modelo.ValorDiario import ValorDiario
# from util.StringUtil import remove_varios_espacos, remove_acentos
#
#
# class ValorDiarioDao(GenericoDao,metaclass=Singleton):
#     def __init__(self):
#         super(ValorDiarioDao, self).__init__(ValorDiario)
#
#     def get_data_mais_recente(self):
#         try:
#             return self._classe.order_by(self._classe.data.desc()).get().data
#         except self._classe.DoesNotExist as e:
#             return None