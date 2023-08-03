from datetime import datetime


data_hoje = datetime.today()
data_created = data_hoje.strftime("%d/%m/%y")
data_update = data_hoje.strftime("%d/%m/%y")
data_concluido = data_hoje.strftime("%d/%m/%y")

def dados_user(nome_task=None, status=None, homologacao=None, update=None, complete=None, user=None):
    _nome_task = nome_task
    _status = status
    _homologacao = homologacao
    _created = data_created
    if update:
        _update = data_update
    else:
        _update = None
    if complete:
        _complete = complete
    else:
        _complete = False
    _user = user

    dados = {"nome_task":_nome_task,"status":_status, "homologacao":_homologacao,
             "created":_created,"update":_update, "complete":_complete, "user":_user}
    return dados
