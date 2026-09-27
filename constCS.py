HOST = '127.0.0.1'  # use '0.0.0.0' no servidor (ou o IP da máquina) para aceitar conexões de outras máquinas na rede
PORT = 5678

# Lista de servidores que o cliente multithread pode usar (round-robin).
# Acrescente mais tuplas (host, port) para distribuir requisições entre
# várias instâncias de server_mt.py.
SERVERS = [(HOST, PORT)]

# Parâmetros padrão para os experimentos de desempenho.
NUM_REQUESTS = 300
MAX_CONCURRENCY = 200
