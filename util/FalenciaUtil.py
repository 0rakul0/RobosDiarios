from datetime import datetime

import sys

from pdjus.modelo.HistoricoDado import HistoricoDado
from pdjus.modelo.ParteDistribuicao import ParteDistribuicao
from pdjus.service.ProcessoService import ProcessoService
from pdjus.modelo.DadoExtraido import DadoExtraido

__author__ = 'B249025230'

import re

def is_falencia_recjud(texto):
   if 'falencia' in texto or 'recuperacao' in texto or 'concordata' in texto or 'devedor' in texto or\
                   'falimentar' in texto or 'declaracao' in texto or 'habilitacao' in texto or 'insolvencia' in texto:
       return True
   return False
def verifica_texto_decretacao_falencia(texto):
    if not texto:
        return False,None
    expressao_processo = re.compile('(\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})|(\d{3}\.\d{2}\.\d{4}\.\d{6}(\-\d\/\d{6}\-\d{3})?)|(\d{3}\.\d{2}\.\d{6}\-\d)')
    expressao_decretacao_falencia = re.compile('D *E *C *R *E *T *A *[CÇç] *[AÃã] *O *D *[AE] *F *A *L *[EÊê] *N *C *I *A *D *[EAO].*',re.IGNORECASE)
    expressão_edital_decretacao = re.compile('E *D *I *T *A *L *-?(D *E)? *D *E *C *R *E *T *A *[CÇç] *[ãÃA] *O *D *[EA] *F *A *L *[EÊê] *N *C *I *A.*',re.IGNORECASE)
    expressao_edital_sentenca = re.compile('E *D *I *T *A *L *D *[AE] *S *E *N *T *E *N *[CÇç] *A *(D *E *C *L *A *R *A *T *[OÓó] *R *I *A)? *D[AE] *F *A *L *[EÊê] *N *C *I *A *D *[EAO].*',re.IGNORECASE)
    decretacao_falencia_match = expressao_decretacao_falencia.search(texto)
    encontrou = False
    if not decretacao_falencia_match:
        edital_decretacao_match = expressão_edital_decretacao.search(texto)
        if not edital_decretacao_match:
            edital_sentenca_match = expressao_edital_sentenca.search(texto)
            if edital_sentenca_match:
                encontrou = True
        else:
            encontrou = True
    else:
        encontrou = True
    if encontrou:
        processo_match = expressao_processo.search(texto)
        if processo_match:
            num_processo = processo_match.group(0).replace('.','').replace('-','').replace(' ','')
            return encontrou,num_processo
    return False,None

def conserta_dado_extraido(rank=0,fatia=1):
    processoService = ProcessoService()
    for tag in ["INDICE_VALOR_AGREGADO"]:
        processos = processoService.dao.listar(tag=tag,rank=rank,fatia=fatia)
        for processo in processos:
            historicos_corretos = []
            print("PROCESSO: " + str(processo.id))
            print("TAG: " + tag)
            dado_extraido_antigo = processo.dado_extraido
            for historico in dado_extraido_antigo.historicos:
                if historico.marcador == "FALENCIAS" and (processo.is_processo_falencia_recuperacao_convolacao() or (processo.processo_principal and processo.processo_principal.is_processo_falencia_recuperacao_convolacao())):
                    historicos_corretos.append(historico)
                    print("FALENCIAS")
                if processo.classe_processual and \
                        re.search(
                            "TITULO *(EXECUTIVO)? *EXTR?A\-?JUDICIAL|MONITORIA|DESPEJ|BUSC.*APREE?N.*ALIEN|ALUG|LOCAC|ALIMENTO",
                            processo.classe_processual.nome):
                    if historico.marcador == "INDICE_VALOR_AGREGADO" and processo.distribuicao and historico not in historicos_corretos:
                        historicos_corretos.append(historico)
                        print("INDICE_VALOR_AGREGADO")

                    if historico.marcador == "INDICE_ME" and processo.distribuicao:
                        for parte in processo.distribuicao.partes_distribuicoes:
                            if parte.pequena_empresa and parte.is_reu() and historico not in historicos_corretos:
                                historicos_corretos.append(historico)
                                print("INDICE_ME")

                    if historico.marcador == "INDICE_BANCO" and processo.distribuicao:
                        for parte in processo.distribuicao.partes_distribuicoes:
                            if (parte.banco or (not parte.banco and parte.pessoa_juridica)) and parte.is_autor() and historico not in historicos_corretos:
                                historicos_corretos.append(historico)
                                print("INDICE_BANCO")

                    if historico.marcador == "INDICE_PJ" and processo.distribuicao:
                        for parte in processo.distribuicao.partes_distribuicoes:
                            if parte.is_reu() and historico not in historicos_corretos:
                                historicos_corretos.append(historico)
                                print("INDICE_PJ")

            if processo.classe_processual and \
                    re.search("TITULO *(EXECUTIVO)? *EXTR?A\-?JUDICIAL|MONITORIA|DESPEJ|BUSC.*APREE?N.*ALIEN|ALUG|LOCAC|ALIMENTO",processo.classe_processual.nome):
                if len(historicos_corretos) == 0:
                    historico = HistoricoDado()
                    historico.marcador = "INDICE_VALOR_AGREGADO"
                    historico.data_extracao = datetime.today()
                    historicos_corretos.append(historico)
                    print("INDICE_VALOR_AGREGADO")

            dado_extraido_novo = DadoExtraido()
            dado_extraido_novo.data_entrada = datetime.today()
            dado_extraido_novo.save()
            for historico in historicos_corretos:
                historico_novo = HistoricoDado()
                historico_novo.marcador = historico.marcador
                historico_novo.data_extracao = historico.data_extracao
                historico_novo.dado_extraido = dado_extraido_novo
                historico_novo.save()

            processo.dado_extraido = dado_extraido_novo
            processo.save()

if __name__ == "__main__":
    conserta_dado_extraido(sys.argv[1],sys.argv[2])
