# ClientServerBasics (2.0) — Calculadora Remota

Este projeto parte do exemplo da Fig. 2.3 do livro (comunicação básica cliente-servidor
via sockets TCP) e acrescenta funcionalidade real ao servidor: uma **calculadora remota**.

## Como funciona

- O cliente ([client.py](client.py)) conecta-se ao servidor ([server.py](server.py)) via
  TCP, usando o host e a porta definidos em [constCS.py](constCS.py).
- O usuário digita, no cliente, uma ou mais operações que deseja que o servidor execute.
- O servidor recebe a requisição, interpreta cada operação pedida, calcula o resultado
  (ou identifica o erro) e devolve tudo em uma única resposta.
- Após responder, o servidor continua esperando novas requisições do mesmo cliente
  (loop original do template) e, quando o cliente se desconecta, volta a aceitar novas
  conexões de outros clientes (um de cada vez).

## Protocolo de mensagens

Cada operação enviada pelo cliente segue o formato:

```
<operacao> <valor1> <valor2>
```

Para chamar **mais de uma funcionalidade na mesma requisição**, as operações são
separadas por `;`:

```
add 2 3;multiply 4 5;divide 10 0
```

O servidor responde com um resultado por operação, na mesma ordem, também separados
por `;`, no formato `<operacao>=<resultado>` (ou `ERROR: <motivo>` quando a operação
falha):

```
add=5.0;multiply=20.0;ERROR: division by zero
```

Isso satisfaz o requisito de o cliente poder acionar múltiplas funcionalidades
diferentes do servidor em uma única requisição, e não apenas uma por vez.

## Operações disponíveis

O servidor ([server.py](server.py)) implementa seis operações (mínimo exigido: três),
todas recebendo exatamente dois números:

| Operação   | Descrição                  | Exemplo          |
|------------|-----------------------------|------------------|
| `add`      | Soma                        | `add 2 3`        |
| `subtract` | Subtração                   | `subtract 5 2`   |
| `multiply` | Multiplicação                | `multiply 4 5`   |
| `divide`   | Divisão                      | `divide 10 4`    |
| `power`    | Potenciação (base ^ expoente)| `power 2 8`      |
| `mod`      | Resto da divisão (módulo)    | `mod 10 3`       |

### Processamento e tratamento de erros

O servidor não apenas ecoa os dados recebidos: ele interpreta a requisição, valida os
argumentos e executa o cálculo correspondente. Casos tratados:

- Operação desconhecida → `ERROR: unknown operation '<nome>'`
- Quantidade errada de argumentos → `ERROR: '<operacao>' requires exactly 2 numeric arguments`
- Argumento não numérico → `ERROR: invalid numeric argument in '<op>'`
- Divisão por zero → `ERROR: division by zero`

## Como executar

1. Ajuste `HOST` e `PORT` em [constCS.py](constCS.py) conforme o ambiente de rede
   (mesma máquina, rede local, etc.).
2. Em um terminal, inicie o servidor:

```bash
python server.py
```

3. Em outro terminal (ou outra máquina, se `HOST` for um IP acessível na rede), inicie
   o cliente:

```bash
python client.py
```

4. No cliente, digite as operações desejadas, por exemplo:

```
> add 2 3
add=5.0
> add 2 3;multiply 4 5;divide 10 0
add=5.0;multiply=20.0;ERROR: division by zero
> sair
```

Digite `sair` (ou `quit`/`exit`) no cliente para encerrar a conexão.

## Estrutura do projeto

- [constCS.py](constCS.py) — constantes compartilhadas (`HOST`, `PORT`).
- [server.py](server.py) — servidor TCP: aceita conexões, interpreta requisições e
  executa as operações da calculadora.
- [client.py](client.py) — cliente TCP interativo: lê comandos do usuário, envia ao
  servidor e exibe a resposta.

Tarefa individual.
