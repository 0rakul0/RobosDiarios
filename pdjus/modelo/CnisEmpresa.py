from peewee import PrimaryKeyField, CharField, IntegerField, BigIntegerField, DateField
from pdjus.modelo.BaseClass import BaseClass
from util.StringUtil import remove_varios_espacos, remove_acentos, corrige_nome, abrevia_nome


class CnisEmpresa(BaseClass):
    id = PrimaryKeyField(null=False)
    _nome = CharField(db_column='nome')
    _nome_corrigido = CharField(db_column="nome_corrigido")
    _nome_abreviado = CharField(db_column="nome_abreviado")
    natureza_juridica = IntegerField()
    opcao_simples = CharField()
    situacao_prev  = IntegerField()
    situacao_srf = IntegerField()
    _nome_fantasia = CharField(db_column="nome_fantasia")
    _nome_fantasia_corrigido = CharField(db_column="nome_fantasia_corrigido")
    _nome_fantasia_abreviado = CharField(db_column="nome_fantasia_abreviado")
    in_microempresa = IntegerField()
    data_inicio_atividade = DateField()
    in_mei = IntegerField()
    id_empresa_estab  = BigIntegerField()


    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(CnisEmpresa, self).__init__("nome",*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um CnisEmpresa sem nome!")
            return False

        return True


    def __repr__(self):
        return '{} - {} - {}'.format(self.nome,self.id_empresa_estab,self.data_inicio_atividade)

    @property
    def nome(self):
        self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))
        self.nome_corrigido = self._nome #assim que setar o nome, já vai corrigí-lo

    @property
    def nome_corrigido(self):
        self._nome_corrigido = remove_varios_espacos(remove_acentos(self._nome_corrigido.upper()))
        return self._nome_corrigido

    @nome_corrigido.setter
    def nome_corrigido(self, value):
        self._nome_corrigido = corrige_nome(remove_varios_espacos(remove_acentos(value.upper())))
        self.nome_abreviado = self._nome_corrigido #assim que corrigir o nome, já vai abreviá-lo

    @property
    def nome_abreviado(self):
        self._nome_abreviado = remove_varios_espacos(remove_acentos(self._nome_abreviado.upper()))
        return self._nome_abreviado

    @nome_abreviado.setter
    def nome_abreviado(self, value):
        self._nome_abreviado = abrevia_nome(remove_varios_espacos(remove_acentos(value.upper())))

    @property
    def nome_fantasia(self):
        self._nome_fantasia = remove_varios_espacos(remove_acentos(self._nome_fantasia.upper()))
        return self._nome_fantasia

    @nome_fantasia.setter
    def nome_fantasia(self, value):
        self._nome_fantasia = remove_varios_espacos(remove_acentos(value.upper()))
        self.nome_fantasia_corrigido = self._nome_fantasia #assim que setar o nome_fantasia, já vai corrigí-lo

    @property
    def nome_fantasia_corrigido(self):
        self._nome_fantasia_corrigido = remove_varios_espacos(remove_acentos(self._nome_fantasia_corrigido.upper()))
        return self._nome_fantasia_corrigido

    @nome_fantasia_corrigido.setter
    def nome_fantasia_corrigido(self, value):
        self._nome_fantasia_corrigido = corrige_nome(remove_varios_espacos(remove_acentos(value.upper())))
        self.nome_fantasia_abreviado = self._nome_fantasia_corrigido #assim que corrigir o nome_fantasia, já vai abreviá-lo

    @property
    def nome_fantasia_abreviado(self):
        self._nome_fantasia_abreviado = remove_varios_espacos(remove_acentos(self._nome_fantasia_abreviado.upper()))
        return self._nome_fantasia_abreviado

    @nome_fantasia_abreviado.setter
    def nome_fantasia_abreviado(self, value):
        self._nome_fantasia_abreviado = abrevia_nome(remove_varios_espacos(remove_acentos(value.upper())))



    class Meta:
        db_table = "cnis_empresa"