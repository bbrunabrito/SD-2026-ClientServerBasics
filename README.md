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

- [constCS.py](constCS.py) — constantes compartilhadas (`HOST`, `PORT`, `SERVERS`,
  parâmetros do experimento).
- [calculator.py](calculator.py) — lógica da calculadora (operações, parsing de
  requisições, geração de requisições aleatórias), compartilhada por todas as
  versões do servidor/cliente.
- [server.py](server.py) — servidor **single-threaded** original: aceita um cliente
  por vez e atende suas requisições sequencialmente.
- [client.py](client.py) — cliente TCP interativo (uso manual): lê comandos do
  usuário, envia ao servidor e exibe a resposta.
- [server_mt.py](server_mt.py) — servidor **multithread**: dispara uma nova thread
  para cada requisição recebida.
- [client_auto_single.py](client_auto_single.py) — cliente automatizado
  **sequencial**: gera N requisições aleatórias e as envia uma de cada vez (usado
  como baseline e para testar "multithread só no servidor").
- [client_mt.py](client_mt.py) — cliente automatizado **multithread**: gera N
  requisições aleatórias e dispara uma nova thread para enviar cada uma,
  podendo distribuí-las entre vários servidores (round-robin sobre `SERVERS`).
- [experiment.py](experiment.py) — orquestra os três cenários do experimento de
  desempenho, sobe/derruba os servidores automaticamente e mede o tempo total.

---

## Parte 2 — Servidor e cliente multithread

Além da versão single-threaded acima, o projeto inclui uma versão em que **cada
requisição é tratada em sua própria thread**, tanto no servidor quanto no cliente:

- **Servidor multithread** ([server_mt.py](server_mt.py)): a cada conexão aceita
  (`accept()`), uma nova `threading.Thread` é criada para ler a requisição,
  processá-la e responder, permitindo que múltiplos clientes/requisições sejam
  atendidos concorrentemente.
- **Cliente multithread** ([client_mt.py](client_mt.py)): dispara uma nova thread
  para cada requisição, cada uma abrindo sua própria conexão (`connect` → `send`
  → `recv` → `close`). As requisições são distribuídas em round-robin pela lista
  `SERVERS` em [constCS.py](constCS.py), permitindo enviar carga simultaneamente
  para mais de um servidor. Um semáforo (`MAX_CONCURRENCY`) limita quantas
  threads/conexões ficam abertas ao mesmo tempo, evitando esgotar portas/recursos
  do sistema.
- **Geração automática de requisições**: `calculator.generate_random_request()`
  sorteia uma operação e dois operandos aleatórios, usado tanto pelo cliente
  multithread quanto pelo cliente sequencial automatizado, para gerar carga sem
  depender de digitação manual.

Cada arquivo pode ser executado isoladamente:

```bash
# servidor multithread
python server_mt.py

# em outro terminal: 500 requisições sequenciais automáticas
python client_auto_single.py 500

# ou: 500 requisições em paralelo (uma thread por requisição)
python client_mt.py 500
```

## Experimento de desempenho

[experiment.py](experiment.py) automatiza a comparação entre três arquiteturas,
usando exatamente a mesma carga de trabalho (mesmo número de requisições,
mesmas operações aleatórias) em cada uma:

| Cenário | Servidor | Cliente | Arquivo do experimento |
|---|---|---|---|
| **A** | single-thread ([server.py](server.py)) | sequencial ([client_auto_single.py](client_auto_single.py)) | baseline (tarefa anterior) |
| **B** | multithread ([server_mt.py](server_mt.py)) | sequencial ([client_auto_single.py](client_auto_single.py)) | multithread só no servidor |
| **C** | multithread ([server_mt.py](server_mt.py)) | multithread ([client_mt.py](client_mt.py)) | multithread nos dois lados |

Para rodar:

```bash
python experiment.py <num_requisicoes> <concorrencia_maxima_cliente>
# exemplo:
python experiment.py 300 200
```

O script sobe o servidor correspondente como subprocesso, executa o cliente,
mede o tempo total de envio+processamento+resposta de todas as requisições, e
derruba o servidor antes de passar ao próximo cenário.

### Resultados obtidos

Testado localmente (Windows, `127.0.0.1`, sem tráfego de rede real), com
**300 requisições** por cenário e concorrência máxima de 200 threads no
cliente multithread. Os números abaixo são a média de 4 execuções
consecutivas (após descartar a primeira execução, afetada por
"aquecimento" do processo/SO):

| Cenário | Tempo médio | Vazão (req/s) |
|---|---|---|
| A — single-thread (servidor+cliente) | ~0,110 s | ~2 720 req/s |
| B — multithread só no servidor | ~0,160 s | ~1 880 req/s |
| C — multithread nos dois lados | ~0,090 s | ~3 350 req/s |

Speedups relativos ao baseline (A): **B ≈ 0,69×** (mais lento que A),
**C ≈ 1,23×** mais rápido que A, e **C ≈ 1,78×** mais rápido que B.

### Interpretação

- **B é mais lento que A**, mesmo sendo multithread no servidor. Isso acontece
  porque, nesse cenário, o *cliente* continua enviando as requisições uma de
  cada vez (sequencialmente): nunca há mais de uma conexão realmente
  concorrente chegando ao servidor. O servidor multithread paga o custo de
  criar e destruir uma thread por requisição sem nenhum ganho de paralelismo
  para compensar — overhead puro.
- **C é o mais rápido**: como o cliente também é multithread, várias
  requisições ficam "em voo" ao mesmo tempo, então as threads do servidor
  realmente se sobrepõem (enquanto uma thread espera E/S de rede, outra pode
  ser atendida). Mesmo com o GIL do Python, isso funciona bem porque
  `socket.recv`/`send` liberam o GIL durante a espera de E/S.
- Em execuções com carga maior (ex.: 1000 requisições), observamos mais
  variância entre execuções — provavelmente por causa do grande número de
  conexões TCP curtas abertas/fechadas em sequência no loopback (acúmulo de
  sockets em `TIME_WAIT`) e do agendamento de threads pelo Windows, e não por
  uma mudança na arquitetura em si.
- **Conclusão geral**: multithreading no servidor só compensa quando há
  paralelismo real do lado de quem gera a carga (múltiplos clientes ou um
  cliente que também envia em paralelo). Multithreading "só por multithreading"
  em um dos lados pode até piorar o desempenho.

