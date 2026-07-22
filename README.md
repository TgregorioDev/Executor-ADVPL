# Mini ADVPL - Executor ADVPL para Estudos

Este projeto e um interpretador didatico de um subconjunto de ADVPL escrito em Python puro. Ele foi criado para praticar logica, sintaxe basica e fluxo de execucao sem depender de Protheus, AppServer, SmartClient, RPO, licenciamento ou APIs TOTVS.

O objetivo nao e clonar o Protheus. O foco e aprender a linguagem por etapas.

## Requisitos

- Python 3.13 ou superior
- Nenhuma dependencia externa

## Como executar

```bash
python main.py examples/hello.prw
```

Saida esperada:

```text
Ola Mundo
```

Tambem e possivel executar outros exemplos:

```bash
python main.py examples/age_if.prw
python main.py examples/loops_arrays.prw
python main.py examples/functions.prw
python main.py examples/dates.prw
python main.py examples/case_hash.prw
```

## Como criar um programa

Crie um arquivo `.prw` com uma `User Function`:

```advpl
User Function Teste()

    Local nIdade := 21

    If nIdade >= 18
        ConOut("Maior de idade")
    Else
        ConOut("Menor de idade")
    EndIf

Return
```

Execute:

```bash
python main.py caminho/do/arquivo.prw
```

## Arquitetura

```text
src/
  lexer/
    lexer.py
    token.py
    token_type.py
  parser/
    parser.py
    ast_nodes.py
  runtime/
    runtime.py
    variables.py
    scope.py
  interpreter/
    interpreter.py
  functions/
    builtin.py
  errors/
    errors.py
  utils/
    helpers.py
examples/
tests/
  programs/          # programas .prw (001..015), um por recurso
  test_programs.py   # executa cada programa e valida a saida
main.py
README.md
```

## Fluxo interno

```text
Codigo ADVPL
  -> Lexer
  -> Lista de Tokens
  -> Parser
  -> AST
  -> Interpreter
  -> Runtime
  -> Resultado
```

## Recursos implementados

- `User Function`, `Static Function` e `Function`
- `Return` com ou sem valor
- variaveis `Local`, `Static`, `Public` e `Private`
- tipos simulados: character, numeric, logical, date, nil, arrays e hash (objeto simples)
- operadores aritmeticos (`+ - * / % ^`), relacionais (`== != < <= > >=`) e logicos (`AND OR NOT`, tambem `!`)
- atribuicao `:=`, atribuicoes compostas (`+= -= *= /=`) e incremento/decremento (`++ --`)
- literais logicos `.T.`/`.F.` e os apelidos `TRUE`/`FALSE`
- strings e concatenacao com `+`
- comentarios `//` e `/* ... */`; `;` funciona como separador de comandos
- `If`, `ElseIf`, `Else`, `EndIf`
- `Do Case`, `Case`, `Otherwise`, `EndCase`
- `For`, `Next` (com `Step`), `Do While`, `EndDo`, `Exit`, `Break`, `Loop`
- arrays com `{}`, indice 1-based (`aItens[1]`) e alteracao (`aItens[2] := 50`)
- hashes (objetos simples) com `{"chave" => valor}` e as funcoes `HB_H*`
- funcoes internas:
  - console/dialogo: `ConOut`, `MsgInfo`, `Alert`, `InputBox`
  - string: `Len`, `Upper`, `Lower`, `AllTrim`, `SubStr`, `Left`, `Right`, `Str`, `Val`, `Empty`
  - numerico: `Int`, `Round`, `Abs`
  - data/hora: `Date`, `Time`, `CToD`, `DToC`
  - array: `AAdd`, `ALen`, `ASize`
  - hash: `HB_HNew`, `HB_HHasKey`, `HB_HSet`, `HB_HGet`
- escopo local por chamada de funcao e recursao
- tabela de simbolos e pilha de execucao
- excecoes especificas para erros lexicos, sintaticos e de runtime, com mensagens
  que informam linha, coluna, token esperado e token encontrado

### Precedencia de operadores

Da maior para a menor prioridade:

```text
()            parenteses
NOT  !        negacao logica e unario -/+
^             potencia (associativa a direita)
* / %         multiplicacao, divisao, resto
+ -           soma e subtracao
== != < <= > >=  comparacoes
AND           e logico
OR            ou logico
```

## Conceitos representados

### User Function e Static Function

No ADVPL real, `User Function` expoe uma rotina que pode ser chamada externamente e `Static Function` restringe a visibilidade ao fonte. Nesta primeira versao, ambas sao registradas internamente e podem ser chamadas pelo programa; a primeira `User Function` do arquivo e usada como ponto de entrada.

### Variaveis e escopos

`Local` cria variaveis no escopo da funcao atual. `Static`, `Public` e `Private` existem como escopos separados no runtime, mas ainda de forma simplificada em relacao ao ADVPL real. Isso permite estudar visibilidade sem reproduzir todos os detalhes do AppServer.

### Condicionais e repeticoes

`If` e lacos sao convertidos para nos da AST. O interpreter visita cada no e decide quais blocos executar. `Exit` e `Loop` usam sinais internos para sair do laco ou avancar para a proxima iteracao.

### Funcoes internas

As funcoes nativas ficam em `src/functions/builtin.py`. Elas recebem valores Python, aplicam as regras simplificadas e escrevem no console simulado do runtime quando necessario.

### Datas

Datas sao simuladas com `datetime.date`, da biblioteca padrao do Python. `CToD("22/07/2026")` cria uma data e `DToC(dData)` converte a data de volta para texto. Tambem e aceito o formato `YYYY-MM-DD`.

## Recursos pendentes (nao implementados)

- `CLASS`, `METHOD`, `DATA`, `ENDCLASS` (orientacao a objetos completa com `Self`
  e `::`). As palavras-chave sao reconhecidas pelo lexer e o parser emite uma
  mensagem amigavel sugerindo o uso de hashes (`HB_H*`) como objetos simples.
- Blocos de codigo (`{|x| ... }`), `IIf()`, `Try/Catch`.
- Banco de dados, alias, areas, RDD, MVC, telas ou componentes TOTVS.
- API completa de arrays e de datas do ADVPL real.
- `Static`, `Public` e `Private` existem como escopos, mas de forma simplificada;
  `Static Function` ainda nao aplica restricao real de visibilidade por arquivo.

## Diferencas em relacao ao ADVPL real (decisoes didaticas)

- `;` e tratado como separador de comandos (e nao como continuacao de linha).
- `!` e aceito como negacao logica, alem da palavra-chave `NOT`.
- `TRUE`/`FALSE` sao aceitos como apelidos de `.T.`/`.F.`.

## Testes

Execute a suite com:

```bash
python -m unittest discover
```

Os testes cobrem lexer, parser, interpreter, funcoes internas, variaveis, `If`,
`For`, `Do While` e `Do Case`. Alem dos testes de unidade, a pasta
`tests/programs/` contem 15 programas `.prw` (um por recurso) executados de ponta
a ponta por `tests/test_programs.py`.

## Roadmap

- Literais e funcoes de data
- Mais funcoes de array
- `CLASS`, `METHOD`, objetos e heranca
- Blocos de codigo
- `Switch`
- `Try/Catch`
- Banco de dados ficticio para estudo
- Alias e comandos como `DBSelectArea()`, `DbSeek()` e `RecLock()`
- MVC simplificado


