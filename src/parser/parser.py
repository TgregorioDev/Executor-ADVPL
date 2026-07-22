"""Recursive descent parser for the supported ADVPL grammar."""

from collections.abc import Sequence

from src.errors.errors import AdvplSyntaxError, UnexpectedToken
from src.lexer.token import Token
from src.lexer.token_type import TokenType
from src.parser.ast_nodes import (
    ArrayLiteral,
    AssignmentStatement,
    BinaryExpression,
    CallExpression,
    Expression,
    ExpressionStatement,
    ExitStatement,
    ForStatement,
    FunctionDeclaration,
    Identifier,
    IfStatement,
    IndexExpression,
    Literal,
    LoopStatement,
    Program,
    ReturnStatement,
    Statement,
    UnaryExpression,
    VariableDeclaration,
    WhileStatement,
)


class Parser:
    """Build an AST from the token stream produced by the lexer."""

    BLOCK_END_TOKENS = {
        TokenType.ELSEIF,
        TokenType.ELSE,
        TokenType.ENDIF,
        TokenType.NEXT,
        TokenType.ENDDO,
        TokenType.USER_FUNCTION,
        TokenType.STATIC_FUNCTION,
        TokenType.EOF,
    }

    def __init__(self, tokens: Sequence[Token]) -> None:
        self.tokens = list(tokens)
        self.current = 0

    def parse(self) -> Program:
        """Parse a full source file into a Program node."""

        functions: list[FunctionDeclaration] = []
        self._skip_newlines()

        while not self._is_at_end():
            functions.append(self._function_declaration())
            self._skip_newlines()

        return Program(functions)

    def _function_declaration(self) -> FunctionDeclaration:
        if self._match(TokenType.USER_FUNCTION):
            kind = "USER"
        elif self._match(TokenType.STATIC_FUNCTION):
            kind = "STATIC"
        else:
            token = self._peek()
            raise UnexpectedToken(
                f"Expected User Function or Static Function at {token.location()}, "
                f"got {token.type.name}."
            )

        name = self._consume(TokenType.IDENTIFIER, "Expected function name.").lexeme
        self._consume(TokenType.LPAREN, "Expected '(' after function name.")
        params = self._parameter_list()
        self._consume(TokenType.RPAREN, "Expected ')' after function parameters.")
        self._skip_newlines()

        body = self._statement_list(
            stop_tokens=(TokenType.USER_FUNCTION, TokenType.STATIC_FUNCTION)
        )
        return FunctionDeclaration(kind, name, params, body)

    def _parameter_list(self) -> list[str]:
        params: list[str] = []
        if self._check(TokenType.RPAREN):
            return params

        while True:
            params.append(
                self._consume(TokenType.IDENTIFIER, "Expected parameter name.").lexeme
            )
            if not self._match(TokenType.COMMA):
                break

        return params

    def _statement_list(self, stop_tokens: tuple[TokenType, ...]) -> list[Statement]:
        statements: list[Statement] = []

        while not self._is_at_end() and not self._check_any(stop_tokens):
            self._skip_newlines()
            if self._is_at_end() or self._check_any(stop_tokens):
                break
            statements.append(self._statement())
            self._skip_newlines()

        return statements

    def _statement(self) -> Statement:
        if self._match(
            TokenType.LOCAL, TokenType.STATIC, TokenType.PUBLIC, TokenType.PRIVATE
        ):
            return self._variable_declaration(self._previous())
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.DO):
            return self._while_statement()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        if self._match(TokenType.EXIT):
            return ExitStatement()
        if self._match(TokenType.LOOP):
            return LoopStatement()

        if self._check(TokenType.IDENTIFIER) and self._check_next(TokenType.ASSIGN):
            name = self._advance().lexeme
            self._advance()
            value = self._expression()
            return AssignmentStatement(name, value)

        if self._check_any(tuple(self.BLOCK_END_TOKENS)):
            token = self._peek()
            raise UnexpectedToken(f"Unexpected {token.type.name} at {token.location()}.")

        return ExpressionStatement(self._expression())

    def _variable_declaration(self, keyword: Token) -> VariableDeclaration:
        name = self._consume(TokenType.IDENTIFIER, "Expected variable name.").lexeme
        initializer = None
        if self._match(TokenType.ASSIGN):
            initializer = self._expression()
        return VariableDeclaration(keyword.type.name, name, initializer)

    def _if_statement(self) -> IfStatement:
        condition = self._expression()
        self._skip_newlines()

        then_branch = self._statement_list(
            stop_tokens=(TokenType.ELSEIF, TokenType.ELSE, TokenType.ENDIF)
        )
        elseif_branches: list[tuple[Expression, list[Statement]]] = []

        while self._match(TokenType.ELSEIF):
            branch_condition = self._expression()
            self._skip_newlines()
            branch_body = self._statement_list(
                stop_tokens=(TokenType.ELSEIF, TokenType.ELSE, TokenType.ENDIF)
            )
            elseif_branches.append((branch_condition, branch_body))

        else_branch: list[Statement] = []
        if self._match(TokenType.ELSE):
            self._skip_newlines()
            else_branch = self._statement_list(stop_tokens=(TokenType.ENDIF,))

        self._consume(TokenType.ENDIF, "Expected EndIf to close If block.")
        return IfStatement(condition, then_branch, elseif_branches, else_branch)

    def _for_statement(self) -> ForStatement:
        variable = self._consume(TokenType.IDENTIFIER, "Expected FOR variable.").lexeme
        self._consume(TokenType.ASSIGN, "Expected ':=' after FOR variable.")
        start = self._expression()
        self._consume(TokenType.TO, "Expected TO in FOR statement.")
        end = self._expression()

        step = None
        if self._match(TokenType.STEP):
            step = self._expression()

        self._skip_newlines()
        body = self._statement_list(stop_tokens=(TokenType.NEXT,))
        self._consume(TokenType.NEXT, "Expected Next to close FOR block.")
        if self._check(TokenType.IDENTIFIER):
            self._advance()
        return ForStatement(variable, start, end, step, body)

    def _while_statement(self) -> WhileStatement:
        self._consume(TokenType.WHILE, "Expected While after Do.")
        condition = self._expression()
        self._skip_newlines()
        body = self._statement_list(stop_tokens=(TokenType.ENDDO,))
        self._consume(TokenType.ENDDO, "Expected EndDo to close Do While block.")
        return WhileStatement(condition, body)

    def _return_statement(self) -> ReturnStatement:
        if self._is_statement_boundary():
            return ReturnStatement(None)
        return ReturnStatement(self._expression())

    def _expression(self) -> Expression:
        return self._or()

    def _or(self) -> Expression:
        expression = self._and()
        while self._match(TokenType.OR):
            operator = self._previous().type
            right = self._and()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def _and(self) -> Expression:
        expression = self._equality()
        while self._match(TokenType.AND):
            operator = self._previous().type
            right = self._equality()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def _equality(self) -> Expression:
        expression = self._comparison()
        while self._match(TokenType.EQUAL_EQUAL, TokenType.NOT_EQUAL):
            operator = self._previous().type
            right = self._comparison()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def _comparison(self) -> Expression:
        expression = self._term()
        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self._previous().type
            right = self._term()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def _term(self) -> Expression:
        expression = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous().type
            right = self._factor()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def _factor(self) -> Expression:
        expression = self._unary()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self._previous().type
            right = self._unary()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def _unary(self) -> Expression:
        if self._match(TokenType.NOT, TokenType.MINUS, TokenType.PLUS):
            operator = self._previous().type
            return UnaryExpression(operator, self._unary())
        return self._call()

    def _call(self) -> Expression:
        expression = self._primary()

        while True:
            if self._match(TokenType.LPAREN):
                expression = self._finish_call(expression)
            elif self._match(TokenType.LBRACKET):
                index = self._expression()
                self._consume(TokenType.RBRACKET, "Expected ']' after index.")
                expression = IndexExpression(expression, index)
            else:
                break

        return expression

    def _finish_call(self, callee: Expression) -> CallExpression:
        arguments: list[Expression] = []
        if not self._check(TokenType.RPAREN):
            while True:
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RPAREN, "Expected ')' after arguments.")
        return CallExpression(callee, arguments)

    def _primary(self) -> Expression:
        if self._match(TokenType.NUMBER, TokenType.STRING, TokenType.LOGICAL):
            return Literal(self._previous().literal)
        if self._match(TokenType.NIL):
            return Literal(None)
        if self._match(TokenType.IDENTIFIER):
            return Identifier(self._previous().lexeme)
        if self._match(TokenType.LPAREN):
            expression = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression.")
            return expression
        if self._match(TokenType.LBRACE):
            return self._array_literal()

        token = self._peek()
        raise AdvplSyntaxError(
            f"Expected expression at {token.location()}, got {token.type.name}."
        )

    def _array_literal(self) -> ArrayLiteral:
        elements: list[Expression] = []
        if not self._check(TokenType.RBRACE):
            while True:
                elements.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RBRACE, "Expected '}' after array literal.")
        return ArrayLiteral(elements)

    def _match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()

        token = self._peek()
        raise UnexpectedToken(
            f"{message} At {token.location()}, got {token.type.name}."
        )

    def _skip_newlines(self) -> None:
        while self._match(TokenType.NEWLINE):
            pass

    def _is_statement_boundary(self) -> bool:
        return self._check(TokenType.NEWLINE) or self._check_any(
            tuple(self.BLOCK_END_TOKENS)
        )

    def _check_any(self, types: tuple[TokenType, ...]) -> bool:
        return any(self._check(token_type) for token_type in types)

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return token_type is TokenType.EOF
        return self._peek().type is token_type

    def _check_next(self, token_type: TokenType) -> bool:
        if self.current + 1 >= len(self.tokens):
            return False
        return self.tokens[self.current + 1].type is token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type is TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]
