#
# from pdjus.modelo.BaseClass import *
# from pdjus.modelo.Empresa import Empresa
# from pdjus.modelo.Endereco import Endereco
# from pdjus.modelo.Estado import Estado
# from pdjus.modelo.Reparticao import Reparticao
# from pdjus.modelo.ReparticaoSegundoGrau import ReparticaoSegundoGrau
#
#
# class ValorDiario(BaseClass):
#     id = PrimaryKeyField(null=False)
#
#     estado = ForeignKeyField(Estado,null=True)
#
#     requerido = ForeignKeyField(Empresa,null=True)
#
#     #requerente = ForeignKeyField(Empresa,null=True)
#
#     endereco = ForeignKeyField(Endereco,null=True)
#
#     reparticao = ForeignKeyField(Reparticao,null=True)
#
#     reparticao_segundo_grau = ForeignKeyField(ReparticaoSegundoGrau,null=True)
#
#     data = DateTimeField()
#
#     situacao = TextField()
#
#     def __init__(self,*args, **kwargs):
#        self.init_on_load(*args, **kwargs)
#
#     def init_on_load(self,*args, **kwargs):
#         super(ValorDiario, self).__init__(*args, **kwargs)
#
#     def is_valido(self):
#         return True
#
#     class Meta:
#         db_table = "valor_diario"