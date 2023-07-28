# # -*- coding: utf-8 -*-
# from util.StringUtil import remove_acentos, remove_varios_espacos, remove_tracos_pontos_barras_espacos
# from pdjus.modelo.BaseClass import *
# from util.StringUtil import corrige_nome, abrevia_nome
#
#
# # para popular a partir do CSV
# # psql -h postgresql10-rj -U diario-mining -d diario_mining
# # \copy desenv_bpc.cnis_bpc(nome,cpf,dt_nasc,despacho,aojudicial,municpio,espcie,espcie1,codibge,UF,municipio) FROM 'base.csv' DELIMITER ';' CSV HEADER;
#
# class CnisBPC(BaseClass):
#     id = PrimaryKeyField(null=False)
#     nome =  CharField()
#     _cpf =  CharField(db_column="cpf")
#     dt_nasc =  CharField()
#     despacho =  CharField()
#     aojudicial =  CharField()
#     municpio =  CharField()
#     espcie =  CharField()
#     espcie1 =  CharField()
#     codibge =  CharField()
#     uf =  CharField()
#     municipio =  CharField()
#     encontrado =  CharField()
#     processado =  CharField()
#
#     def __init__(self,*args, **kwargs):
#       self.init_on_load(*args, **kwargs)
#
#     def init_on_load(self,*args, **kwargs):
#         super(CnisBPC, self).__init__("cpf",*args, **kwargs)
#
#     def is_valido(self):
#         if not self.cpf:
#             print("Não pode existir um CnisBPC sem cpf!")
#             return False
#
#         return True
#
#     @property
#     def cpf(self):
#         if self._cpf:
#             self._cpf = "{:011d}".format(int(self._cpf))
#         else:
#             self._cpf = "{:011d}".format(0)
#
#         return self._cpf
#
#     class Meta:
#         db_table = "cnis_bpc"