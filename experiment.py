"""Orquestra os 3 cenários de desempenho pedidos no experimento:

  A) servidor single-thread  + cliente sequencial   (baseline da tarefa anterior)
  B) servidor multithread    + cliente sequencial   (multithread só no servidor)
  C) servidor multithread    + cliente multithread  (multithread nos dois lados)

Cada cenário sobe o servidor correspondente como subprocesso, roda o
cliente automatizado contra ele, mede o tempo e derruba o servidor antes do
próximo cenário.
"""
import subprocess
import sys
import time

from constCS import HOST, PORT, SERVERS, NUM_REQUESTS, MAX_CONCURRENCY
import client_auto_single
import client_mt


def start_server(script):
    proc = subprocess.Popen([sys.executable, script],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)  # tempo para o servidor abrir o listen()
    return proc


def stop_server(proc):
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def scenario_A(n):
    proc = start_server('server.py')
    try:
        return client_auto_single.run(n)
    finally:
        stop_server(proc)


def scenario_B(n):
    proc = start_server('server_mt.py')
    try:
        return client_auto_single.run(n)
    finally:
        stop_server(proc)


def scenario_C(n, max_concurrency):
    proc = start_server('server_mt.py')
    try:
        elapsed, _, _ = client_mt.run(n, SERVERS, max_concurrency=max_concurrency)
        return elapsed
    finally:
        stop_server(proc)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else NUM_REQUESTS
    max_concurrency = int(sys.argv[2]) if len(sys.argv) > 2 else MAX_CONCURRENCY

    print(f"Experimento com {n} requisições (concorrência máx. no cliente MT: {max_concurrency})\n")

    t_a = scenario_A(n)
    print(f"[A] single-thread (servidor+cliente sequenciais): {t_a:8.4f}s  ({n / t_a:.1f} req/s)")

    t_b = scenario_B(n)
    print(f"[B] multithread só no servidor:                    {t_b:8.4f}s  ({n / t_b:.1f} req/s)")

    t_c = scenario_C(n, max_concurrency)
    print(f"[C] multithread no servidor e no cliente:          {t_c:8.4f}s  ({n / t_c:.1f} req/s)")

    print("\nSpeedup relativo ao baseline (A):")
    print(f"  A -> B: {t_a / t_b:.2f}x")
    print(f"  A -> C: {t_a / t_c:.2f}x")
    print(f"  B -> C: {t_b / t_c:.2f}x")
