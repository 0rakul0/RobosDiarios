from pdjus.conexao.Conexao import Singleton
from pdjus.dal.GenericoDao import GenericoDao
from pdjus.modelo.MovimentoMarcador import MovimentoMarcador

class MovimentoMarcadorDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(MovimentoMarcadorDao, self).__init__(MovimentoMarcador)

    def get_por_movimento_marcador(self, movimento, marcador):
        try:
            return self._classe.select().where(self._classe.movimento==movimento,self._classe.marcador==marcador).get()
        except self._classe.DoesNotExist as e:
            return None

