import os
from datetime import date


def verificar_data_modificacao(caminho_pasta):
    try:
        data_modificacao = date.fromtimestamp(os.path.getmtime(caminho_pasta))
        # print(f"O arquivo em \033[91m{caminho_pasta}\033[0m foi modificado em: \033[96m{data_modificacao}\033[0m",
              # end="\n\n")
        return data_modificacao
    except OSError:
        return None
