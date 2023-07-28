from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ParteProcessoDao import ParteProcessoDao
from pdjus.modelo.Parte import Parte
from pdjus.modelo.ParteProcesso import ParteProcesso
from pdjus.modelo.TipoParte import TipoParte
from pdjus.service.AdvogadoService import AdvogadoService
from pdjus.service.BaseService import BaseService
from pdjus.service.ParteService import ParteService
from pdjus.service.PessoaFisicaService import PessoaFisicaService
from pdjus.service.ProcessoService import ProcessoService
from pdjus.service.TipoParteService import TipoParteService
from util.StringUtil import remove_varios_espacos, remove_acentos

class ParteProcessoService(BaseService,metaclass=Singleton):

    def __init__(self):
        super(ParteProcessoService, self).__init__(ParteProcessoDao())

    def preenche_parte_processo(self, processo, tipo, parte, advogados=[], search_parte=True, tag=None,is_processos_com_mesmo_npu = False):

        self.preenche_parte_processo_pessoa( processo, tipo, parte, advogados=advogados, search_parte=search_parte, tag=tag,is_processos_com_mesmo_npu=is_processos_com_mesmo_npu)


    def preenche_parte_processo_pessoa(self, processo, tipo_parte, parte, advogados=[], nome_pessoa=None,cpf_pessoa=None, search_parte=True, tag=None,is_processos_com_mesmo_npu = False):
        pessoaService = PessoaFisicaService()
        parteService = ParteService()
        tipoParteService = TipoParteService()
        parteProcesso = None

        if type(parte) is Parte:
            nome_parte = parte.nome
        else:
            nome_parte = parte

        if type(tipo_parte) is TipoParte:
            tipo = tipo_parte
        else:
            tipo = tipoParteService.preenche_tipo_parte(tipo_parte)


        pessoa = None
        if search_parte:
            parteProcesso = self.dao.get_por_nome_e_processo_e_tipo(nome_parte, processo, tipo)
        if nome_pessoa or cpf_pessoa:
            pessoa = pessoaService.preenche_pessoa(nome_pessoa,cpf_pessoa)

        if not parteProcesso:
            parteProcesso = ParteProcesso()

        if not parteProcesso.parte:
            if not type(parte) is Parte:
                parteProcesso.parte = parteService.preenche_parte(nome_parte,pessoa)
            else:
                parteProcesso.parte = parte

        if not parteProcesso.tipo_parte:
            parteProcesso.tipo_parte = tipo

        if not parteProcesso.processo:
            parteProcesso.processo = processo
        self.salvar(parteProcesso, tag=tag, salvar_estrangeiras=False, commit=False,is_processos_com_mesmo_npu=is_processos_com_mesmo_npu)

        self.seta_advogados_na_parte_processo(advogados, parteProcesso)

        self.salvar(parteProcesso, tag=tag, salvar_estrangeiras=False, commit=False,is_processos_com_mesmo_npu=is_processos_com_mesmo_npu)

    def seta_advogados_na_parte_processo(self, advogados, parteProcesso):
        advogadoService = AdvogadoService()
        for adv in advogados:
            advogado = None
            if type(adv) is str:
                if (adv.strip() is not '' and remove_varios_espacos(remove_acentos(adv.upper())) is not '') and adv.strip() not in parteProcesso.nome_advogados():
                    advogado = advogadoService.preenche_advogado(adv.strip())
            else:  # senão, o tipo já é Advogado, não precisa fazer nada apenas dar append
                advogado = adv
            if advogado and advogado not in parteProcesso.advogados :
                parteProcesso.advogados.append(advogado)




    def salvar(self,obj, caderno=None, tag=None, commit=True, salvar_estrangeiras = True,salvar_many_to_many = True,is_processos_com_mesmo_npu = False):
        partes_processo = obj
        processoService = ProcessoService()
        parte_service = ParteService()
        advogado_service = AdvogadoService()
        tipo_parte_service = TipoParteService()
        partes_processo_salvar = {}
        if partes_processo:
            if not type(partes_processo) is list:
                partes_processo = [partes_processo]
            for chave,parte_processo in enumerate(partes_processo):
                if parte_processo.processo and not parte_processo.processo.id :
                    processo_bd = processoService.preenche_processo(npu=parte_processo.processo.npu,numero_processo=parte_processo.processo.numero_processo,grau=parte_processo.processo.grau,is_processos_com_mesmo_npu=is_processos_com_mesmo_npu)
                    if processo_bd and processo_bd.id:
                        parte_processo.processo.id = processo_bd.id
                    processoService.salvar(parte_processo.processo, caderno, tag,salvar_estrangeiras=salvar_estrangeiras,salvar_many_to_many=salvar_many_to_many ,commit=commit)

                if not parte_processo.parte.id:
                    try:
                        parte_processo.parte = parte_service.preenche_parte(parte_processo.parte.nome)
                        parte_service.salvar(parte_processo.parte, caderno, tag,salvar_estrangeiras=salvar_estrangeiras,salvar_many_to_many=salvar_many_to_many ,commit=commit)
                    except Exception as e:
                        break

                if not parte_processo.tipo_parte.id:
                    try:
                        parte_processo.tipo_parte = tipo_parte_service.preenche_tipo_parte(parte_processo.tipo_parte.nome)
                        tipo_parte_service.salvar(parte_processo.tipo_parte, caderno, tag,salvar_estrangeiras=salvar_estrangeiras,salvar_many_to_many=salvar_many_to_many ,commit=commit)
                    except Exception as e:
                        break

                if not parte_processo.id:
                    parte_processo_bd = self.dao.get_por_parte_e_processo_e_tipo(parte_processo.parte, parte_processo.processo, parte_processo.tipo_parte)
                    if parte_processo_bd:
                        partes_processo[chave].id = parte_processo_bd.id

                chave_salvar = str(parte_processo.processo.id) + str(parte_processo.tipo_parte.id) + str(parte_processo.parte.id)
                partes_processo_salvar[chave_salvar] = parte_processo

            for parte_processo in partes_processo_salvar.values():
                try:
                    for advogado in parte_processo.advogados.copy():
                        if not advogado.id:
                            advogado_bd = advogado_service.preenche_advogado(oab=advogado.numero_oab, nome=advogado.nome)
                            advogado.id = advogado_bd.id
                except self.dao._classe.DoesNotExist as e:
                     print("erro")

            self.dao.salvar_lote(partes_processo_salvar.values(), caderno, tag,salvar_estrangeiras=salvar_estrangeiras,salvar_many_to_many=salvar_many_to_many ,commit=commit)
