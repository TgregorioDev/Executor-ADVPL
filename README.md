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

- `User Function` e `Static Function`
- `Return`
- variaveis `Local`, `Static`, `Public` e `Private`
- tipos simulados: character, numeric, logical, date, nil e arrays
- operadores aritmeticos, relacionais e logicos
- strings e concatenacao com `+`
- comentarios `//` e `/* ... */`
- `If`, `ElseIf`, `Else`, `EndIf`
- `For`, `Next`, `Do While`, `EndDo`, `Exit`, `Loop`
- arrays com `{}`, `AAdd()`, `Len()` e indice 1-based com `aItens[1]`
- funcoes internas: `ConOut`, `MsgInfo`, `Len`, `Upper`, `Lower`, `AllTrim`, `Str`, `Val`, `AAdd`, `CToD`, `DToC`
- escopo local por chamada de funcao
- tabela de simbolos e pilha de execucao
- excecoes especificas para erros lexicos, sintaticos e de runtime

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

## Limitacoes atuais

- Nao ha banco de dados, alias, areas, RDD, MVC, telas ou componentes TOTVS.
- `Static Function` ainda nao aplica restricao real de visibilidade por arquivo.
- `Public` e `Private` sao simplificados.
- Datas sao simuladas por `CToD`/`DToC`, mas ainda nao cobrem todas as funcoes de data do ADVPL real.
- Arrays suportam criacao literal, `AAdd`, `Len` e leitura por indice, mas ainda nao cobrem toda a API ADVPL.
- Nao ha classes, objetos, blocos de codigo, `Switch` ou `Try/Catch`.

## Testes

Execute a suite com:

```bash
python -m unittest discover
```

Os testes cobrem lexer, parser, interpreter, funcoes internas, variaveis, `If`, `For` e `Do While`.

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


