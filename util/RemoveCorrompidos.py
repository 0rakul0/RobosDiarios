import glob
from pathlib import Path
import os


def remove_arquivos_corrompidos():

    pasta = Path('/mnt/dmlocal/dados/TRF/TRF02/pdf')

    for f in pasta.glob('**/*'):
        if f.is_file() and f.stat().st_size == 0:
            print('Removendo o arquivo {} onde o mesmo posssui {} bytes'.format(f._str, f.stat().st_size))
            os.remove(f._str)


remove_arquivos_corrompidos()