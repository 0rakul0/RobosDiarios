# -*- coding: utf-8 -*-

from util.StringUtil import remove_acentos,remove_varios_espacos,remove_tracos_pontos_barras_espacos
from pdjus.modelo.BaseClass import *



from util.StringUtil import corrige_nome, abrevia_nome



class Empresa(BaseClass):
    id = PrimaryKeyField(null=False)
    _cnpj =  CharField(db_column="cnpj")
    nire = CharField() # comentar para rodar DJSP
    #endereco = CharField() # comentar para rodar DJSP
    #cep = CharField() # comentar para rodar DJSP
    _nome = CharField(db_column='nome')
    _nome_corrigido =  CharField(db_column="nome_corrigido")
    _nome_abreviado =  CharField(db_column="nome_abreviado")
    quantidade_ocorrencias = IntegerField()

    #objetos_sociais = ManyToMany(ObjetoSocial, through_model=EmpresaObjetoSocial) # comentar para rodar DJSP
    #enquadramentos = EmpresaEnquadramentoThroughDeferred

    def __init__(self,*args, **kwargs):
      self.init_on_load(*args, **kwargs)


    def init_on_load(self,*args, **kwargs):
        super(Empresa, self).__init__(["cnpj","nome"],*args, **kwargs)

    def is_valido(self):
        if not self.nome:
            print("Não pode existir um Empresa sem nome!")
            return False
        if not self.cnpj:
            if not self.nire:
                print("Não pode existir um Empresa sem cnpj ou nire!")
                return False

        return True

    @property
    def nome(self):
        if self._nome:
            self._nome = remove_varios_espacos(remove_acentos(self._nome.upper()))
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = remove_varios_espacos(remove_acentos(value.upper()))
        self.nome_corrigido = self._nome #assim que setar o nome, já vai corrigí-lo

    @property
    def cnpj(self):
        return self._cnpj

    @cnpj.setter
    def cnpj(self, value):
        self._cnpj = Empresa.formata_cnpj(value)

    @classmethod
    def formata_cnpj(self,cnpj):
        return remove_tracos_pontos_barras_espacos(cnpj.rjust(14, '0'))

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





