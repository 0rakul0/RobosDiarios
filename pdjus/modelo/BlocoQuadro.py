from util.StringUtil import remove_acentos,remove_varios_espacos,remove_caracteres_especiais_para_quadro
from pdjus.modelo.BaseClass import *
from pdjus.modelo.Movimento import Movimento
from pdjus.modelo.Caderno import Caderno

class BlocoQuadro(BaseClass):
    id = PrimaryKeyField(null=False)
    _texto = TextField(db_column='texto')
    _texto_limpo = TextField(db_column='texto_limpo')
    movimento = ForeignKeyField(Movimento, null=True)
    caderno = ForeignKeyField(Caderno, null=True)
    validacao_nome_falida = IntegerField(db_column="validacao_nome_falida", null=True)
    validacao_nome_credor = FloatField(db_column='validacao_nome_credor', null=True)
    validacao_parte_credor = FloatField(db_column='validacao_parte_credor', null=True)
    validacao_credor_interno = FloatField(db_column='validacao_credor_interno', null=True)

    def is_valido(self):
        if not self.texto:
            print("Não pode existir um Bloco Quadro sem texto!")
            return False

        return True

    @property
    def texto(self):
        # self._texto = remove_varios_espacos(remove_acentos(remove_caracteres_especiais(self._texto.strip().upper())))
        return self._texto

    @texto.setter
    def texto(self, value):
        # self._texto = remove_varios_espacos(remove_acentos(value.strip().upper()))
        self._texto = value

    @property
    def texto_limpo(self):
        # self._texto_limpo = remove_varios_espacos(remove_acentos(remove_caracteres_especiais_para_quadro(self._texto_limpo.strip().upper())))
        return self._texto_limpo

    @texto_limpo.setter
    def texto_limpo(self, value):
        self._texto_limpo = remove_varios_espacos(remove_acentos(remove_caracteres_especiais_para_quadro(value.strip().upper())))


    class Meta:
        db_table = "bloco_quadro"