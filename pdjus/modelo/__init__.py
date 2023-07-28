#

from pathlib import Path
import sys
import inspect
import pkgutil
from importlib import import_module

# from pdjus.modelo.BaseClass import BaseClass
#
# modelos_siape = ["ProcessoServidor","Servidor","FilaProcessamento"]
#
# for (_, name, _) in pkgutil.iter_modules([Path(__file__).parent]):
#
#     if name not in modelos_siape:
#         imported_module = import_module('.' + name, package=__name__)
#
#         for i in dir(imported_module):
#             attribute = getattr(imported_module, i)
#
#             if inspect.isclass(attribute) and issubclass(attribute, BaseClass):
#                 setattr(sys.modules[__name__], name, attribute)


#del modules

#
#
# from .Advogado import Advogado
# from .Area import Area
# from .Arquivo import Arquivo
# from .Assunto import Assunto
# from .Audiencia import Audiencia
# from .BaseClass import BaseClass
# from .BlocoQuadro import BlocoQuadro
# from .Caderno import Caderno
# from .Cda import Cda
# from .ClasseCredor import ClasseCredor
# from .ClasseProcessual import ClasseProcessual
# # from .CnisBPC import CnisBPC
# from .CnisEmpresa import CnisEmpresa
# from .CnisEstabelecimento import CnisEstabelecimento
# from .Comarca import Comarca
# from .DadoExtraido import DadoExtraido
# from .Diario import Diario
# from .DispositivoLegal import DispositivoLegal
# from .Distribuicao import Distribuicao
# from .Empresa import Empresa
# from .Endereco import Endereco
# from .Estado import Estado
# from .Extrator import Extrator
# from .Guia import Guia
# from .HistoricoClasse import HistoricoClasse
# from .HistoricoDado import HistoricoDado
# from .Incidente import Incidente
# from .ItemGuia import ItemGuia
# from .Juiz import Juiz
# from .MarcoProcessual import MarcoProcessual
# from .MarcoProcessualDispositivoLegal import MarcoProcessualDispositivoLegal
# # from .Motivo import Motivo
# from .Movimento import Movimento
# from .Municipio import Municipio
# from .NotaExpediente import NotaExpediente
# from .Parte import Parte
# from .ParteDistribuicao import ParteDistribuicao
# from .ParteProcesso import ParteProcesso
# from .PessoaFisica import PessoaFisica
# from .Peticao import Peticao
# from .Processo import Processo
# from .ProcTemp import ProcTemp
# from .Prova import Prova
# from .Publicacao import Publicacao
# from .QuadroCredor import QuadroCredor
# from .Rais import Rais
# from .Reparticao import Reparticao
# from .ReparticaoSegundoGrau import ReparticaoSegundoGrau
# from .Sentenca import Sentenca
# from .Situacao import Situacao
# from .SituacaoProcesso import SituacaoProcesso
# from .StatusExtraido import StatusExtraido
# from .TipoMarcoProcessual import TipoMarcoProcessual
# from .TipoMovimento import TipoMovimento
# from .TipoParte import TipoParte
# from .Tribunal import Tribunal
# # from .ValorDiario import ValorDiario
