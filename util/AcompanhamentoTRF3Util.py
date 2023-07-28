def ControleDeNumero(numero_processo):

    if len(numero_processo) < 15:
        return 1

    if len(numero_processo) == 20:
        cod_estado = numero_processo[-4:-2]
        if cod_estado == '62' or cod_estado == '63':
            return 1
        return 0

    elif len(numero_processo) == 15:
        cod_estado = numero_processo[4:6]
        if cod_estado == '62' or cod_estado == '63':
            return 1
        return 0

    else:
        return 1