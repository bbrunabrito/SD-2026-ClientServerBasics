import random

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
        return "ERROR: division by zero"

    return f"{op_name}={result}"


def process_request(request):
    """Uma requisição pode conter várias operações separadas por ';',
    permitindo que o cliente chame mais de uma funcionalidade de uma vez."""
    operations = request.split(';')
    results = [process_operation(op) for op in operations]
    return ';'.join(results)


def generate_random_request(num_ops=1):
    """Gera uma requisição aleatória com 'num_ops' operações válidas,
    usada para automatizar a geração de carga nos experimentos."""
    ops = []
    for _ in range(num_ops):
        name = random.choice(list(OPERATIONS.keys()))
        a = round(random.uniform(1, 100), 2)
        # evita divisor/módulo zero para que o experimento meça apenas
        # o custo de processamento de requisições bem-sucedidas
        b = round(random.uniform(1, 100), 2)
        ops.append(f"{name} {a} {b}")
    return ';'.join(ops)
