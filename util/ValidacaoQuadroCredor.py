import csv, re
from pdjus.service.BlocoQuadroService import BlocoQuadroService
from pdjus.service.ProcessoService import ProcessoService
from util.StringUtil import remove_varios_espacos, remove_acentos, remove_parenteses_e_pontuacao

def verifica_nome_parte_no_bloco_quadro(arquivo):
    processoService = ProcessoService()
    bloco_quadroService = BlocoQuadroService()
    with open(arquivo, 'r', encoding= 'latin1') as arq_csv:
        csv_processos = csv.DictReader(arq_csv, delimiter=';')
        for linha in csv_processos:
            nome = remove_varios_espacos(re.sub('\\b(MASSA\s*FALIDA\s*(D[AOE])?|(EM\s*)?RECUPERACAO\s*JUDICIAL\s*(DE)?|EPP|MEI?|LTDA(\s*SOC)?|SA|EIRELLI|EM\s*RECUPERACAO)\\b','',remove_parenteses_e_pontuacao(remove_acentos( linha['nome_parte'].upper()))))
            id_processo = linha['id_processo']
            processo = processoService.dao.get_por_id(id_processo)
            print('LINHA LIDA: {};{}'.format(nome,id_processo))
            # if not processo.blocos_quadro:
            #     print('Processo {} de id {} não possui nenhum quadro associado!'.format(processo.npu_ou_num_processo,processo.id))
            for bloco_quadro in processo.blocos_quadro(bloco_quadroService):
                if ((bloco_quadro.validacao_nome_falida and bloco_quadro.validacao_nome_falida < 0) or not bloco_quadro.validacao_nome_falida) and (nome in remove_varios_espacos(remove_parenteses_e_pontuacao(remove_acentos(bloco_quadro.texto_limpo.upper()))) or nome in remove_varios_espacos(remove_parenteses_e_pontuacao(remove_acentos(bloco_quadro.texto.upper())))):
                    print('ENCONTROU A EMPRESA EM RECUPERACAO: {} no processo {} de id {}'.format(nome,processo.npu_ou_num_processo, processo.id))
                    if bloco_quadro.validacao_nome_falida:
                        bloco_quadro.validacao_nome_falida+=1
                    else:
                        bloco_quadro.validacao_nome_falida = 1
                    processoService.salvar(bloco_quadro)
                else:
                    print('NAO FOI POSSIVEL ENCONTRAR O CREDOR {}'.format(nome))
                    # print('Bloco pesquisado : {}'.format(bloco_quadro.texto_limpo))
                    if not bloco_quadro.validacao_nome_falida:
                        bloco_quadro.validacao_nome_falida = 0
                        processoService.salvar(bloco_quadro)

#CRIEI 2 csvs um de nome id_nome_falidas e outro de nome id_nome_falidas2
#Se tiver que rodar mais uma vez, pegar todos os nomes que foram lidos, copiar para o csv já processado e deixar a partir do último que leu, para evitar retrabalho
verifica_nome_parte_no_bloco_quadro('C:\\Users\\b249025230\\Downloads\\id_nome_falidas2.csv')
# processoService = ProcessoService()
# proc = processoService.dao.get_por_id(171407)
# print(proc.id)