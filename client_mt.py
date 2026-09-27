"""Cliente automatizado e multithread.

Gera N requisições aleatórias e dispara uma nova thread para enviar cada
uma delas, permitindo que várias requisições estejam em voo ao mesmo tempo
(inclusive para servidores diferentes, escolhidos em round-robin a partir
de SERVERS em constCS.py).
"""
import sys
import time
import threading
from socket import *

from constCS import SERVERS, NUM_REQUESTS, MAX_CONCURRENCY
from calculator import generate_random_request


def _send_request(server, request, results, idx, sem):
    host, port = server
    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((host, port))
        s.send(request.encode())
        data = s.recv(1024)
        s.close()
        results[idx] = data.decode()
    except OSError as e:
        # guarda o erro em vez de deixar a thread propagar o traceback
        # (com centenas de threads, tracebacks soltos ficam ilegíveis)
        results[idx] = f"ERROR: {e}"
    finally:
        sem.release()  # libera vaga para outra thread iniciar


def run(num_requests, servers=None, max_concurrency=MAX_CONCURRENCY):
    servers = servers or SERVERS
    requests = [generate_random_request() for _ in range(num_requests)]
    results = [None] * num_requests
    sem = threading.Semaphore(max_concurrency)  # limita threads simultâneas
    threads = []

    start = time.time()
    for i, req in enumerate(requests):
        sem.acquire()
        server = servers[i % len(servers)]
        t = threading.Thread(target=_send_request, args=(server, req, results, i, sem))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start

    return elapsed, requests, results


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else NUM_REQUESTS
    elapsed, requests, results = run(n)
    failures = [r for r in results if r is None or r.startswith("ERROR")]
    print(f"{n} requisições paralelas (até {MAX_CONCURRENCY} simultâneas) "
          f"para {len(SERVERS)} servidor(es) em {elapsed:.4f}s "
          f"({n / elapsed:.1f} req/s)")
    if failures:
        print(f"{len(failures)} requisição(ões) falharam. Exemplo: {failures[0]}")
        print("Verifique se o servidor (server_mt.py) está rodando e escutando "
              "no host/porta corretos antes de rodar o cliente.")
