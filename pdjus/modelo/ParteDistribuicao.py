from pdjus.modelo.Rais import Rais
from pdjus.modelo.Distribuicao import Distribuicao
from pdjus.modelo.BaseClass import *
from util.RegexUtil import RegexUtil
from pdjus.modelo.TipoParte import TipoParte
from util.StringUtil import remove_varios_espacos, remove_acentos, corrige_nome, abrevia_nome

ParteDistribuicaoRaisThroughDeferred = DeferredThroughModel()

class ParteDistribuicao(BaseClass):
    id = PrimaryKeyField(null=False)
    _parte = CharField(db_column="parte")

    distribuicao = ForeignKeyField(Distribuicao,null=True,related_name="partes_distribuicoes")

    tipo_parte = ForeignKeyField(TipoParte,null=True)

    advogado = CharField()

    numero_oab = CharField()

    pessoa_juridica = BooleanField()

    banco = BooleanField()

    pequena_empresa = BooleanField()

    governo = BooleanField()

    cobranca = BooleanField()

    setor = CharField()

    _nome_corrigido = CharField(db_column="nome_corrigido")

    _nome_abreviado = CharField(db_column="nome_abreviado")

    rais = ManyToMany(Rais, through_model=ParteDistribuicaoRaisThroughDeferred)

    def is_valido(self):
        if self.parte.strip() == "" or self.parte.strip() == "''":
            self.parte = None
        if not self.parte:
            print("Não pode existir um ParteDistribuicao sem parte!")
            return False
        if not self.tipo_parte:
            print("Não pode existir um ParteDistribuicao sem tipo parte!")
            return False
        return True

    def is_reu(self):
        if self.tipo_parte:
            if RegexUtil().reu.search(self.tipo_parte.nome):
                return True
        return False

    def is_autor(self):
        if self.tipo_parte:
            if RegexUtil().autor.search(self.tipo_parte.nome):
                return True
        return False

    @property
    def parte(self):
        self._parte = remove_varios_espacos(remove_acentos(self._parte.upper()))
        return self._parte

    @parte.setter
    def parte(self, value):
        self._parte = remove_varios_espacos(remove_acentos(value.upper()))
        self.nome_corrigido = self._parte  # assim que setar o nome, já vai corrigí-lo

    @property
    def nome_corrigido(self):
        self._nome_corrigido = remove_varios_espacos(remove_acentos(self._nome_corrigido.upper()))
        return self._nome_corrigido

    @nome_corrigido.setter
    def nome_corrigido(self, value):
        self._nome_corrigido = corrige_nome(remove_varios_espacos(remove_acentos(value.upper())))
        self.nome_abreviado = self._nome_corrigido  # assim que corrigir o nome, já vai abreviá-lo

    @property
    def nome_abreviado(self):
        self._nome_abreviado = remove_varios_espacos(remove_acentos(self._nome_abreviado.upper()))
        return self._nome_abreviado

    @nome_abreviado.setter
    def nome_abreviado(self, value):
        self._nome_abreviado = abrevia_nome(remove_varios_espacos(remove_acentos(value.upper())))


    def __init__(self,*args, **kwargs):
       self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(ParteDistribuicao, self).__init__(["parte","distribuicao","tipo_parte"],*args, **kwargs)

    class Meta:
        db_table = "parte_distribuicao"

class ParteDistribuicaoRais(BaseClass):
    id = PrimaryKeyField(null=False)
    rais = ForeignKeyField(Rais,null=True)
    parte_distribuicao = ForeignKeyField(ParteDistribuicao,null=True)
    class Meta:
        db_table = "parte_distribuicao_rais"

ParteDistribuicaoRaisThroughDeferred.set_model(ParteDistribuicaoRais)





