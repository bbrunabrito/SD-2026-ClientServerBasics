"""Cliente automatizado e sequencial (single-threaded).

Gera N requisições aleatórias e as envia uma de cada vez, esperando a
resposta antes de enviar a próxima. Serve tanto como baseline single-thread
quanto para testar um servidor multithread sendo usado sem paralelismo do
lado do cliente (item B do experimento).
"""
import sys
import time
from socket import *

from constCS import HOST, PORT, NUM_REQUESTS
from calculator import generate_random_request


def run(num_requests, server=None):
    host, port = server or (HOST, PORT)
    start = time.time()
    for _ in range(num_requests):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((host, port))
        s.send(generate_random_request().encode())
        s.recv(1024)
        s.close()
    return time.time() - start


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else NUM_REQUESTS
    elapsed = run(n)
    print(f"{n} requisições sequenciais processadas em {elapsed:.4f}s "
          f"({n / elapsed:.1f} req/s)")
