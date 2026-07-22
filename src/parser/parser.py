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
    CaseStatement,
    Expression,
    ExpressionStatement,
    ExitStatement,
    ForStatement,
    FunctionDeclaration,
    HashLiteral,
    Identifier,
    IfStatement,
    IndexAssignment,
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
        TokenType.CASE,
        TokenType.OTHERWISE,
        TokenType.ENDCASE,
        TokenType.USER_FUNCTION,
        TokenType.STATIC_FUNCTION,
        TokenType.FUNCTION,
        TokenType.EOF,
    }

    # Tokens that terminate a top-level function body.
    FUNCTION_STOP_TOKENS = (
        TokenType.USER_FUNCTION,
        TokenType.STATIC_FUNCTION,
        TokenType.FUNCTION,
    )

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
        elif self._match(TokenType.FUNCTION):
            kind = "FUNCTION"
        elif self._check(TokenType.CLASS):
            token = self._peek()
            raise UnexpectedToken(
                "CLASS/METHOD (object orientation) is not supported yet in this "
                "learning version. Use hashes ({\"chave\" => valor} with HB_HSet/"
                f"HB_HGet) for simple objects. At {token.location()}."
            )
        else:
            token = self._peek()
            raise UnexpectedToken(
                f"Expected User Function, Static Function or Function at "
                f"{token.location()}, got {token.type.name}."
            )

        name = self._consume(TokenType.IDENTIFIER, "Expected function name.").lexeme
        self._consume(TokenType.LPAREN, "Expected '(' after function name.")
        params = self._parameter_list()
        self._consume(TokenType.RPAREN, "Expected ')' after function parameters.")
        self._skip_newlines()

        body = self._statement_list(stop_tokens=self.FUNCTION_STOP_TOKENS)
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
            # "Do" introduces either a "Do While" loop or a "Do Case" block.
            # The "Case" keyword right after "Do" is the block header, so it is
            # consumed here before parsing the individual Case branches.
            if self._match(TokenType.CASE):
                return self._case_statement()
            return self._while_statement()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        # Both Exit and Break leave the nearest loop.
        if self._match(TokenType.EXIT, TokenType.BREAK):
            return ExitStatement()
        if self._match(TokenType.LOOP):
            return LoopStatement()

        if self._check_any(tuple(self.BLOCK_END_TOKENS)):
            token = self._peek()
            raise UnexpectedToken(f"Unexpected {token.type.name} at {token.location()}.")

        return self._assignment_or_expression()

    def _assignment_or_expression(self) -> Statement:
        """Parse a statement that is either an assignment or a bare expression.

        The left-hand side is parsed as a full expression so that assignment
        targets can be simple variables (``x``) or array/hash elements
        (``a[i]``). Compound operators and ``++``/``--`` are desugared into a
        plain assignment with a BinaryExpression on the right-hand side.
        """

        target = self._expression()

        if self._match(TokenType.ASSIGN):
            return self._make_assignment(target, self._expression())

        compound = {
            TokenType.PLUS_ASSIGN: TokenType.PLUS,
            TokenType.MINUS_ASSIGN: TokenType.MINUS,
            TokenType.STAR_ASSIGN: TokenType.STAR,
            TokenType.SLASH_ASSIGN: TokenType.SLASH,
        }
        for assign_token, operator in compound.items():
            if self._match(assign_token):
                value = BinaryExpression(target, operator, self._expression())
                return self._make_assignment(target, value)

        if self._match(TokenType.PLUS_PLUS):
            value = BinaryExpression(target, TokenType.PLUS, Literal(1))
            return self._make_assignment(target, value)
        if self._match(TokenType.MINUS_MINUS):
            value = BinaryExpression(target, TokenType.MINUS, Literal(1))
            return self._make_assignment(target, value)

        return ExpressionStatement(target)

    def _make_assignment(self, target: Expression, value: Expression) -> Statement:
        """Build the proper assignment node for a variable or element target."""

        if isinstance(target, Identifier):
            return AssignmentStatement(target.name, value)
        if isinstance(target, IndexExpression):
            return IndexAssignment(target.collection, target.index, value)
        raise AdvplSyntaxError(
            "Invalid assignment target: only variables and array/hash elements "
            "can be assigned."
        )

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

    def _case_statement(self) -> CaseStatement:
        """Parse a Do Case / Case / Otherwise / EndCase selection block."""

        self._skip_newlines()
        branches: list[tuple[Expression, list[Statement]]] = []

        while self._match(TokenType.CASE):
            condition = self._expression()
            self._skip_newlines()
            body = self._statement_list(
                stop_tokens=(
                    TokenType.CASE,
                    TokenType.OTHERWISE,
                    TokenType.ENDCASE,
                )
            )
            branches.append((condition, body))

        otherwise: list[Statement] = []
        if self._match(TokenType.OTHERWISE):
            self._skip_newlines()
            otherwise = self._statement_list(stop_tokens=(TokenType.ENDCASE,))

        self._consume(TokenType.ENDCASE, "Expected EndCase to close Do Case block.")
        return CaseStatement(branches, otherwise)

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
        expression = self._power()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self._previous().type
            right = self._power()
            expression = BinaryExpression(expression, operator, right)
        return expression

    def _power(self) -> Expression:
        # Exponentiation binds tighter than * / % and is right-associative,
        # so 2 ^ 3 ^ 2 evaluates as 2 ^ (3 ^ 2).
        base = self._unary()
        if self._match(TokenType.CARET):
            exponent = self._power()
            return BinaryExpression(base, TokenType.CARET, exponent)
        return base

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
            return self._brace_literal()

        token = self._peek()
        raise AdvplSyntaxError(
            f"Expected expression at {token.location()}, got {token.type.name}."
        )

    def _brace_literal(self) -> Expression:
        """Parse a ``{}`` literal, deciding between an array and a hash.

        An empty ``{}`` is an array. When the first element is followed by
        ``=>`` the whole literal is parsed as a hash (simple object).
        """

        if self._match(TokenType.RBRACE):
            return ArrayLiteral([])

        first = self._expression()

        if self._match(TokenType.FAT_ARROW):
            first_value = self._expression()
            pairs: list[tuple[Expression, Expression]] = [(first, first_value)]
            while self._match(TokenType.COMMA):
                key = self._expression()
                self._consume(TokenType.FAT_ARROW, "Expected '=>' in hash literal.")
                pairs.append((key, self._expression()))
            self._consume(TokenType.RBRACE, "Expected '}' after hash literal.")
            return HashLiteral(pairs)

        elements: list[Expression] = [first]
        while self._match(TokenType.COMMA):
            elements.append(self._expression())
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

        # Friendly diagnostic (Phase 12): the message states what was expected;
        # here we append the token actually found and the exact source position
        # (line and column).
        token = self._peek()
        raise UnexpectedToken(
            f"{message} Found {token.type.name} at {token.location()}."
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
