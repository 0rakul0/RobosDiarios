# import pyarrow
import pandas as pd
import spark
import sys

filename = sys.argv[1]

# df = pd.read_csv('example.csv')
# df.to_parquet('output.parquet')
idx = 0

mydtypes = {
    'npu': 'str',
    'numero_processo': 'str',
    'tag': 'str',
    'dado_entrada': 'str'
}

for chunk in pd.read_csv(filename, sep='\t', chunksize=10 ** 7, dtype=mydtypes, warn_bad_lines=True, engine='pyarrow'):
    print(idx)
    chunk.to_parquet('teste.parquet')
    idx += 1