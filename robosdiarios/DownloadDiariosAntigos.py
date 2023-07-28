# -*- coding: utf-8 -*-




from datetime import datetime

from util.ConfigManager import ConfigManager


def baixa_antigos():
    #pwd = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__))))
    log = "log_servico.txt"
    diretorio = "RAIZ"

    ConfigManager().escreve_log("Iniciando download...", log, diretorio)

    st = datetime.now()
    #robo_mg = RoboDiarioMG(cfg.le_config("DJMG"))
    #robo_mg.download_antigos()



    '''v_ms = AcompanhamentoProcessualMS(cfg.le_config("DJMS"))
    v_ms.atualiza_processos_baixados_ms() #atualiza_processos_csv(os.path.join(v_ms.caminho_arquivos('*.csv', False), 'processos.csv'))
    v_ms.exporta_processos_csv()'''

    ConfigManager().escreve_log("Execução em {}.".format(str(datetime.now() - st)), log, diretorio)
    ConfigManager().escreve_log("Diários antigos baixados.", log, diretorio)



if __name__ == '__main__':
    baixa_antigos()
