# from sqlalchemy import Column, Integer, String, Date,ForeignKey
# from sqlalchemy.orm import relationship
# from pdjus.conexao.Conexao import Base
# from util.StringUtil import remove_acentos,remove_varios_espacos,remove_links
# from pdjus.modelo.Processo import Processo
# from pdjus.modelo.Situacao import Situacao
# from pdjus.modelo.ClasseProcessual import ClasseProcessual
# from pdjus.modelo.Natureza import Natureza
# from pdjus.modelo.NotaExpediente import NotaExpediente
# from pdjus.modelo.Reparticao import Reparticao
# from pdjus.modelo.TipoMovimento import TipoMovimento
# from pdjus.modelo.Motivo import Motivo
#
#
# class DocumentoMovimento(Base):
#     __tablename__ = 'documento_movimento'
#     id = Column(Integer, primary_key=True)
#     data_pub = Column(Date)
#
#     _texto = Column("texto", String)
#
#     descricao = Column("descricao", String)
#
#     @property
#     def texto(self):
#         if self._texto:
#             self._texto = remove_links(remove_varios_espacos(remove_acentos(self._texto.upper())))
#         return self._texto
#
#     @texto.setter
#     def texto(self, value):
#         self._texto = remove_links(remove_varios_espacos(remove_acentos(value.upper())))