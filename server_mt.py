import threading
from socket import *
from constCS import *
from calculator import process_request


def handle_request(conn, addr):
    """Trata uma conexão/requisição inteira em sua própria thread:
    lê a requisição, processa e devolve a resposta."""
    try:
        data = conn.recv(1024)
        if data:
            request = data.decode()
            response = process_request(request)
            conn.send(response.encode())
    finally:
        conn.close()


def main():
    s = socket(AF_INET, SOCK_STREAM)
    try:
        s.bind((HOST, PORT))
    except OSError:
        print(f"ERRO: não foi possível abrir {HOST}:{PORT} — a porta já está em uso "
              f"(verifique se não há outro server.py/server_mt.py rodando).")
        raise SystemExit(1)
    s.listen(128)
    print(f"[multithread] Servidor escutando em {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        # uma nova thread é disparada para cada requisição recebida
        t = threading.Thread(target=handle_request, args=(conn, addr), daemon=True)
        t.start()


if __name__ == "__main__":
    main()
