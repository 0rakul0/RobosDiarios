from classificadores.ClassificaParteDistribuicao import ClassificaParteDistribuicao
# from classificadores.ClassificaParteDistribuicaoML import ClassificaParteDistribuicaoML
from pdjus.conexao.Conexao import Singleton
from pdjus.dal.ParteDistribuicaoDao import ParteDistribuicaoDao
from pdjus.service.BaseService import BaseService
from pdjus.service.TipoParteService import TipoParteService


class ParteDistribuicaoService(BaseService ,metaclass=Singleton):

    def __init__(self):
        # self.classificador_parte_ml = ClassificaParteDistribuicaoML()
        self.classificador_parte = ClassificaParteDistribuicao()
        super(ParteDistribuicaoService, self).__init__(ParteDistribuicaoDao())

    def preenche_parte_distribuicao(self, partes_distribuicoes, distribuicao, caderno, tag):
        if partes_distribuicoes:
            for parte_distribuicao in partes_distribuicoes:
                if parte_distribuicao and parte_distribuicao.parte:
                    parte_distribuicao.distribuicao = distribuicao
                    # self.classificador_parte_ml.valida_setor_parte(parte_distribuicao)
                    self.classificador_parte.valida(parte_distribuicao)
                    try:
                        self.salvar(parte_distribuicao, caderno, tag, commit=False, salvar_estrangeiras = False,salvar_many_to_many = False)
                    except Exception as e:
                        print(e)


    def salvar(self,obj, caderno=None, tag=None, commit=True, salvar_estrangeiras = True,salvar_many_to_many = True):
        partes_distribuicao = obj
        tipo_parte_service = TipoParteService()
        partes_distribuicao_salvar = {}
        if partes_distribuicao:
            if not type(partes_distribuicao) is list:
                partes_distribuicao = [partes_distribuicao]
            for chave, parte_distribuicao in enumerate(partes_distribuicao):
                try:
                    parte_distribuicao.tipo_parte = tipo_parte_service.preenche_tipo_parte(parte_distribuicao.tipo_parte.nome)
                except Exception as e:
                    print("deu merda nesse tipo parte " + parte_distribuicao.tipo_parte.nome)
                    break

                if parte_distribuicao and not parte_distribuicao.id:
                    parte_distribuicao_bd = self.dao.get_por_nome_e_distribuicao_e_tipo(parte_distribuicao.parte,
                                                                                    parte_distribuicao.distribuicao,
                                                                                    parte_distribuicao.tipo_parte)
                    if parte_distribuicao_bd:
                        partes_distribuicao[chave].id = parte_distribuicao_bd.id

                    self.classificador_parte_ml.valida_setor_parte(parte_distribuicao)
                    self.classificador_parte.valida(parte_distribuicao)
                    chave_salvar = str(parte_distribuicao.distribuicao.id) + str(
                        parte_distribuicao.tipo_parte.id) + str(parte_distribuicao.parte)
                    partes_distribuicao_salvar[chave_salvar] = parte_distribuicao

            self.dao.salvar_lote(partes_distribuicao_salvar.values(), caderno, tag, commit=commit,
                             salvar_estrangeiras=False, salvar_many_to_many=False)