from socket  import *
from constCS import * #-

s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, PORT)) # connect to server (block until accepted)

print("Calculadora remota")
print("Operações disponíveis: add, subtract, multiply, divide, power, mod")
print("Formato de cada operação: <operacao> <valor1> <valor2>")
print("É possível pedir mais de uma operação na mesma requisição, separando-as com ';'")
print("Exemplo: add 2 3;multiply 4 5;divide 10 0")
print("Digite 'sair' para encerrar.\n")

while True:
    msg = input("> ").strip()
    if not msg or msg.lower() in ('sair', 'quit', 'exit'):
        break
    s.send(msg.encode())    # send the request (uma ou mais operações)
    data = s.recv(1024)     # receive the response
    print(data.decode())    # print the result(s)

s.close()               # close the connection
