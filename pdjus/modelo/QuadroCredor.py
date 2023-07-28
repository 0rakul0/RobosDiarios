from util.StringUtil import remove_acentos,remove_varios_espacos,remove_caracteres_especiais
from pdjus.modelo.BaseClass import *
from pdjus.modelo.ClasseCredor import ClasseCredor
from pdjus.modelo.Processo import Processo
from pdjus.modelo.BlocoQuadro import BlocoQuadro
from pdjus.modelo.DadoExtraido import DadoExtraido


class QuadroCredor(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column='nome')
    tipo_moeda = TextField(null=True)
    valor = DecimalField(null=True)
    data = DateTimeField()
    classe_credor = ForeignKeyField(ClasseCredor,null=True,related_name="quadros_credores")
    processo = ForeignKeyField(Processo,null=True,related_name="quadro_credores")
    bloco_quadro = ForeignKeyField (BlocoQuadro, null=True,related_name='quadro_credores')
    dado_extraido = ForeignKeyField(DadoExtraido,null=True,related_name="quadro_credores")

    fonte_dado = TextField()

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(QuadroCredor, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        if not self.processo:
            print("Não pode existir um QuadroCredor sem processo!")
            return False
        return True

    @property
    def nome(self):
        self._nome = remove_varios_espacos(remove_acentos(remove_caracteres_especiais(self._nome.strip().upper())))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(remove_caracteres_especiais(value.strip().upper())))

    class Meta:
        db_table = "quadro_credor"