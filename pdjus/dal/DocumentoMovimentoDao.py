# from pdjus.dal.GenericoDao import GenericoDao,Singleton
# from pdjus.modelo.Movimento import Movimento
# from pdjus.modelo.NotaExpediente import NotaExpediente
# from pdjus.modelo.Processo import Processo
# from pdjus.modelo.Situacao import Situacao
# from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links
# from pdjus.modelo.TipoMovimento import TipoMovimento
# from pdjus.modelo.DocumentoMovimento import DocumentoMovimento
#
# class DocumentoMovimentoDao(GenericoDao,metaclass=Singleton):
#
#     def __init__(self):
#         super(DocumentoMovimentoDao, self).__init__(DocumentoMovimento)
#
#     def get_por_processo_data_tipo_movimento_texto(self,processo,data,tipo_movimento,texto):
#         if texto:
#             texto = remove_links(remove_varios_espacos(remove_acentos(texto.upper())))
#         # a_alias = aliased(Processo)
#         return self._session.query(self._classe).join(self._classe.processo).filter((self._classe.processo == processo), (self._classe.data == data), (self._classe.tipo_movimento == tipo_movimento),(self._classe._texto == texto)).first()
#
#     def get_por_processo_data_tipo_movimento(self,processo,data,tipo_movimento):
#         a_alias = aliased(Processo)
#         return self._session.query(self._classe).join(a_alias, self._classe.processo).filter((a_alias.id == processo.id), (self._classe.data == data), (self._classe.tipo_movimento == tipo_movimento)).first()
#
#     def get_all(self):
#         return self._session.query(self._classe).all()
#
#     def get_por_texto(self, texto):
#         if texto:
#             texto = remove_links(remove_varios_espacos(remove_acentos(texto.upper())))
#         return self._session.query(self._classe).filter(self._classe._texto.like(texto)).first()
#
