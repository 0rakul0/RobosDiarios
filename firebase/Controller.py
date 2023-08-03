from firebase.Service import BackendFirebase, SistemaFirebase
from datetime import datetime
from firebase.Model import dados_user
import pandas as pd


def info_user(nome_task=None, status=None, homologacao=None, update=None, complete=None, user=None):
    bf = BackendFirebase()
    _dados_user = dados_user(nome_task=nome_task, status=status, homologacao=homologacao, update=update, complete=complete, user=user)

    # get_tudo = bf.get_all()
    # print(get_tudo)
    # get_i = bf.get_by_id('-NamPek9Zu_np2EQ9Bof')
    # print(get_i)
    # up_i = bf.update(_dados_user, '-NawkgLb_jehWenbjN6q')
    # post_i = bf.post(_dados_user)
    # print(post_i)
    # del_i = bf.delete("-NaweYHEF2vT85Fj9fZ8")
    # print(del_i)

def dados_sis():
    sf = SistemaFirebase()
    df = pd.read_csv('../csv/dadosPastas.csv')
    for item in df.itertuples():
        estado = item.Estado
        ano = item.Ano
        mes = item.Mes
        tipo = item.Tipo_de_arquivo
        estado = str(estado).split('/')[-1]
        tipo = str(tipo).split('/')[-1]

        _dados = {"estado":estado, "ano":ano, "mes":mes, "tipo":tipo}
        # sf.post(_dados)

    get_s = sf.get_all()
    print(get_s)

if __name__ == "__main__":
    # nome_task = "atualização do backend"
    # status = True
    # homologacao = "sistema"
    # update = True
    # complete = False
    # user = "0rakul0"
    #
    # info_user(nome_task, status, homologacao, update, complete, user)
    dados_sis()