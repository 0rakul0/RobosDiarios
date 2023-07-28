#
# from pdjus.modelo.BaseClass import *
# from util.StringUtil import remove_acentos,remove_varios_espacos
#
# class Motivo(BaseClass):
#     ARTIGO_73 = 1
#     ARTIGO_52 = 2
#     ARTIGO_53 = 3
#     ARTIGO_56 = 4
#     ARTIGO_59 = 5
#     ARTIGO_48 = 6
#     ARTIGO_95 = 7
#     ARTIGO_265 = 8
#     ARTIGO_94 = 9
#     ARTIGO_98 = 10
#     ARTIGO_22 = 11
#     ARTIGO_99 = 12
#     #ARTIGO_83 = 13
#     ARTIGO_140 = 14
#     ARTIGO_142 = 15
#     ARTIGO_108 = 16
#     ARTIGO_149 = 17
#     ARTIGO_83 = 18
#
#     id = PrimaryKeyField(null=False)
#     _nome = CharField(db_column="nome")
#
#
#     def __init__(self,*args, **kwargs):
#       self.init_on_load(*args, **kwargs)
#
#     def init_on_load(self,*args, **kwargs):
#         super(Motivo, self).__init__("nome",*args, **kwargs)
#
#     def is_valido(self):
#         if not self.nome:
#             print("Não pode existir um Motivo sem nome!")
#             return False
#         return True
#
#     @property
#     def nome(self):
#         self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
#         return self._nome
#
#     @nome.setter
#     def nome(self, value):
#         self._nome = remove_varios_espacos(remove_acentos(value.upper()))
