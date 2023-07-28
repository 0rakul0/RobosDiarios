from pdjus.modelo.BaseClass import *
from pdjus.modelo.DadoExtraido import DadoExtraido
from pdjus.modelo.Processo import Processo
from pdjus.modelo.ClasseProcessual import ClasseProcessual
from pdjus.modelo.Assunto import Assunto
from pdjus.modelo.Reparticao import Reparticao
from util.StringUtil import remove_acentos,remove_varios_espacos

MapaProcessoAssuntoThroughDeferred = DeferredThroughModel()


class MapaProcesso(BaseClass):
    id = PrimaryKeyField(null=False)
    _numero_processo = CharField(db_column="numero_processo")
    _npu = CharField(db_column="npu")
    assuntos = ManyToMany(Assunto, through_model=MapaProcessoAssuntoThroughDeferred)
    data_atualizacao = DateTimeField()
    grau = IntegerField()
    classe_processual = ForeignKeyField(ClasseProcessual, null=True)
    dado_extraido = ForeignKeyField(DadoExtraido, null=True)
    data_distribuicao = DateTimeField(db_column="data_distribuicao")
    reparticao = ForeignKeyField(Reparticao, null=True)
    processo_principal = ForeignKeyField(Processo, null=True, related_name="mapa_processos_vinculados")


    def __init__(self,*args, **kwargs):
       self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(MapaProcesso, self).__init__(["npu", "numero_processo"],*args, **kwargs)



    def is_valido(self):
        if (self.numero_processo and self.numero_processo.strip()) == "" or (self.npu and self.npu.strip() == ""):
            self.numero_processo = self.numero_processo.strip()
            self.npu = self.npu.strip()

        if not self.numero_processo and not self.npu:
            print("Não pode existir um processo sem npu ou numero processo!")
            return False

        return True


    def is_processo_da_classe_ou_assunto(self, nome):
        if len(self.assuntos) > 0 or self.classe_processual:
            if len(self.assuntos) > 0:
                for assunto in self.assuntos:
                    if nome in remove_acentos(assunto.nome.lower()):
                        return True
            if self.classe_processual:
                if nome in remove_acentos(self.classe_processual.nome.lower()):
                    return True
        return False

    @property
    def npu(self):
        if self._npu:
            self._npu = self.formata_npu(self._npu)
        return self._npu

    @classmethod
    def formata_npu(self, value):
        return Processo.formata_npu(value)

    @classmethod
    def formata_numero_processo(self, value):
        return Processo.formata_numero_processo(value)

    @npu.setter
    def npu(self, value):
        if value:
            self._npu = self.formata_npu(value)
        else:
            self._npu = None

    @property
    def numero_processo(self):
        if self._numero_processo:
            self._numero_processo = self.formata_numero_processo(self._numero_processo)
        return self._numero_processo

    @numero_processo.setter
    def numero_processo(self, value):
        if value:
            self._numero_processo = self.formata_numero_processo(value)
        else:
            self._numero_processo = None

    @property
    def npu_ou_num_processo(self):
        return self.npu or self.numero_processo

    @classmethod
    def is_npu(self, npu):
        return Processo.is_npu(npu)

    @classmethod
    def is_numero_processo(self, numero_processo):
        return Processo.is_numero_processo(numero_processo)

    @classmethod
    def transforma_numero_processo_em_npu(self, numero_processo, jTR=None):
        return Processo.transforma_numero_processo_em_npu(numero_processo,jTR)

    class Meta:
        db_table = "mapa_processo"


class MapaProcessoAssunto(BaseClass):
    mapa_processo = ForeignKeyField(MapaProcesso, null=True)
    assunto = ForeignKeyField(Assunto, null=True)

    class Meta:
        primary_key = CompositeKey('mapa_processo', 'assunto')
        db_table = "mapa_processo_assunto"


MapaProcessoAssuntoThroughDeferred.set_model(MapaProcessoAssunto)