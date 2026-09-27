from socket  import *
from constCS import * #-
from calculator import process_request

s = socket(AF_INET, SOCK_STREAM)
try:
    s.bind((HOST, PORT))  #-
except OSError:
    print(f"ERRO: não foi possível abrir {HOST}:{PORT} — a porta já está em uso "
          f"(verifique se não há outro server.py/server_mt.py rodando).")
    raise SystemExit(1)
s.listen(1)           #-
print(f"[single-thread] Servidor escutando em {HOST}:{PORT}")

while True:  # aceita clientes sequencialmente, um de cada vez
    (conn, addr) = s.accept()  # returns new socket and addr. client
    print(f"Cliente conectado: {addr}")
    while True:                    # forever, enquanto o cliente estiver conectado
        data = conn.recv(1024)     # receive data from client
        if not data: break         # stop if client stopped
        request = data.decode()
        print(f"Requisição recebida: {request}")
        response = process_request(request)  # processa a(s) operação(ões) pedida(s)
        print(f"Resposta enviada: {response}")
        conn.send(response.encode())  # return the response
    conn.close()               # close the connection
    print(f"Cliente desconectado: {addr}")
