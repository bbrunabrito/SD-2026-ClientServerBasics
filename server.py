from socket  import *
from constCS import * #-

# Operações suportadas pela calculadora remota.
# Cada uma recebe exatamente dois números (float) e devolve um número.
OPERATIONS = {
    'add':      lambda a, b: a + b,
    'subtract': lambda a, b: a - b,
    'multiply': lambda a, b: a * b,
    'divide':   lambda a, b: a / b,
    'power':    lambda a, b: a ** b,
    'mod':      lambda a, b: a % b,
}


def process_operation(op_str):
    """Processa uma única operação no formato 'nome valor1 valor2' e
    devolve uma string com o resultado ou uma mensagem de erro."""
    parts = op_str.strip().split()
    if not parts:
        return "ERROR: empty operation"

    op_name = parts[0].lower()
    args = parts[1:]

    if op_name not in OPERATIONS:
        return f"ERROR: unknown operation '{op_name}'"

    if len(args) != 2:
        return f"ERROR: '{op_name}' requires exactly 2 numeric arguments"

    try:
        numbers = [float(a) for a in args]
    except ValueError:
        return f"ERROR: invalid numeric argument in '{op_str}'"

    try:
        result = OPERATIONS[op_name](*numbers)
    except ZeroDivisionError:
        return f"ERROR: division by zero"

    return f"{op_name}={result}"


def process_request(request):
    """Uma requisição pode conter várias operações separadas por ';',
    permitindo que o cliente chame mais de uma funcionalidade de uma vez."""
    operations = request.split(';')
    results = [process_operation(op) for op in operations]
    return ';'.join(results)


s = socket(AF_INET, SOCK_STREAM)
s.bind((HOST, PORT))  #-
s.listen(1)           #-
print(f"Servidor escutando em {HOST}:{PORT}")

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
