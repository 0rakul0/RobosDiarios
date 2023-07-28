from peewee import PrimaryKeyField, CharField, IntegerField, BigIntegerField, DateField, ForeignKeyField
from pdjus.modelo.BaseClass import BaseClass
from util.StringUtil import remove_varios_espacos, remove_acentos, corrige_nome, abrevia_nome
from pdjus.modelo.CnisEmpresa import CnisEmpresa

class CnisEstabelecimento(BaseClass):
    id = PrimaryKeyField(null=False)
    id_empresa_estab  = BigIntegerField()
    cnis_empresa = ForeignKeyField(CnisEmpresa,null=True, related_name="estabelecimentos")
    id_muni_prev = IntegerField()
    nu_cep = IntegerField()
    id_uf_prev= IntegerField()
    cd_situacao_prev = IntegerField()
    cd_situacao_srf = IntegerField()
    cnpj = CharField()
    cd_matriz_filial = IntegerField()
    data_inicio_atividade = DateField()
    _nome = CharField(db_column='nome')
    _nome_corrigido = CharField(db_column="nome_corrigido")
    _nome_abreviado = CharField(db_column="nome_abreviado")
    cs_cnae_2_0 = IntegerField()
    nu_cnae_2_0 = IntegerField()
    nu_cnae_cmpl_2_0 = IntegerField()


    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(CnisEstabelecimento, self).__init__("cnpj",*args, **kwargs)

    def is_valido(self):
        if not self.cnpj:
            print("Não pode existir um CnisEstabelecimento sem cnpj!")
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


    class Meta:
        db_table = "cnis_estabelecimento"