from pdjus.modelo.Advogado import Advogado
from pdjus.modelo.BaseClass import *
from util.StringUtil import remove_acentos, remove_varios_espacos
from pdjus.modelo.Processo import Processo
from pdjus.modelo.Parte import Parte
from pdjus.modelo.TipoParte import TipoParte



AdvogadoParteProcessoThroughDeferred = DeferredThroughModel()

class ParteProcesso(BaseClass):
    id = PrimaryKeyField(null=False)
    parte = ForeignKeyField(Parte, null=True)

    processo = ForeignKeyField(Processo, null=True, related_name="partes_processo")

    tipo_parte = ForeignKeyField(TipoParte, null=True)

    advogados = ManyToMany(Advogado, through_model=AdvogadoParteProcessoThroughDeferred)
    recuperanda = BooleanField(db_column="recuperanda")

    # @property
    # def advogados(self):
    #     if len(self.__advogados) == 0:
    #         for advogado_parte_processo in self.advogado_partes_processo:
    #             self.__advogados.append(advogado_parte_processo.advogado)
    #     return self.__advogados

    def __init__(self,*args, **kwargs):
       self.init_on_load(*args, **kwargs)

    def init_on_load(self,*args, **kwargs):
        super(ParteProcesso, self).__init__(["parte", "processo", "tipo_parte"],*args, **kwargs)

    def is_valido(self):
        if not self.parte:
            print("Não pode existir um ParteProcesso sem parte!")
            return False
        if not self.tipo_parte:
            print("Não pode existir um ParteProcesso sem tipo parte!")
            return False
        if not self.processo:
            print("Não pode existir um ParteProcesso sem processo!")
            return False
        return True

    def nome_advogados(self):
        return [adv.nome for adv in self.advogados]
    class Meta:
        db_table = "parte_processo"


class AdvogadoParteProcesso(BaseClass):
    advogado = ForeignKeyField(Advogado, null=True)
    parte_processo = ForeignKeyField(ParteProcesso, null=True)
    class Meta:
        primary_key = CompositeKey('advogado', 'parte_processo')
        db_table = "advogado_parte_processo"


AdvogadoParteProcessoThroughDeferred.set_model(AdvogadoParteProcesso)
