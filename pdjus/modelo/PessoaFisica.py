
from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos, remove_varios_espacos
from pdjus.modelo.Empresa import Empresa
from pdjus.modelo.Processo import Processo
from pdjus.modelo.Rais import Rais
from util.StringUtil import corrige_nome, abrevia_nome

PessoaProcessoThroughDeferred = DeferredThroughModel()

class PessoaFisica(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome =  CharField(db_column="nome")
    _cpf =  CharField(db_column="cpf")
    processado = BooleanField(db_column="processado")
    encontrado = BooleanField(db_column="encontrado")
    processos = ManyToMany(Processo, through_model=PessoaProcessoThroughDeferred)
    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(PessoaFisica, self).__init__(["cpf", "nome"], *args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um PessoaFisica sem nome!")
            return False
        return True

    @property
    def nome(self):
        self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))
        self.nome_corrigido = self._nome

    @property
    def cpf(self):
        self._cpf = remove_varios_espacos(remove_acentos(self._cpf.upper().zfill(11)))
        return self._cpf

    @cpf.setter
    def cpf(self, value):
        self._cpf = remove_varios_espacos(remove_acentos(value.upper().zfill(11)))
        self._cpf = self._cpf

    class Meta:
        db_table = "pessoa_fisica"

class PessoaProcesso(BaseClass):
    pessoa = ForeignKeyField(PessoaFisica, null=True)
    processo = ForeignKeyField(Processo, null=True)
    class Meta:
        primary_key = CompositeKey('pessoa', 'processo')
        db_table = "pessoa_processo"


PessoaProcessoThroughDeferred.set_model(PessoaProcesso)