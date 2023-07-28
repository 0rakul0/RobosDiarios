
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Processo import Processo
from pdjus.modelo.Situacao import Situacao
from pdjus.modelo.Parte import Parte

class SituacaoProcesso(BaseClass):
    id = PrimaryKeyField(null=False)

    processo = ForeignKeyField(Processo,null=True,related_name="situacoes_processo")

    situacao = ForeignKeyField(Situacao,null=True)

    parte = ForeignKeyField(Parte,null=True,related_name="situacoes_processo")

    data = DateTimeField()

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(SituacaoProcesso, self).__init__(*args, **kwargs)

    def is_valido(self):
        if not self.processo:
            print("Não pode existir um SituacaoProcesso sem processo!")
            return False
        if not self.situacao:
            print("Não pode existir um SituacaoProcesso sem situacao!")
            return False
        return True

    class Meta:
        db_table = "situacao_processo"