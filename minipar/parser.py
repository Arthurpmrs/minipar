from abc import ABC, abstractmethod
from copy import deepcopy

from minipar import ast
from minipar.lexer import Lexer, NextToken
from minipar.symbol import Symbol, SymTable
from minipar.token import Token

DEFAULT_FUNCTION_NAMES = {
    'print': 'VOID',
    'input': 'STRING',
    'sleep': 'VOID',
    'to_number': 'NUMBER',
    'to_string': 'STRING',
    'to_bool': 'BOOL',
    'send': 'STRING',
    'close': 'VOID',
    'len': 'NUMBER',
    'isalpha': 'BOOL',
    'isnum': 'BOOL',
    'sum': 'NUMBER',
    'pow': 'NUMBER',
    'sqrt': 'NUMBER',
}

STATEMENT_TOKENS = {
    'ID',
    'FUNC',
    'IF',
    'ELSE',
    'WHILE',
    'FOR',
    'RETURN',
    'BREAK',
    'CONTINUE',
    'SEQ',
    'PAR',
    'C_CHANNEL',
    'S_CHANNEL',
    'VAR',
}


class Parser(ABC):
    @abstractmethod
    def match(self, label: str) -> bool:
        pass

    @abstractmethod
    def start(self) -> ast.Program:
        pass


class ParserImpl(Parser):  # noqa: PLR0904
    def __init__(self, lexer: Lexer):
        self.token_generator: NextToken = lexer.scan()
        self.lookahead, self.line = next(self.token_generator)
        print(self.lookahead, self.line)
        self.symtable = SymTable()
        for func_name in DEFAULT_FUNCTION_NAMES.keys():
            self.symtable.insert(func_name, Symbol(func_name, 'FUNC'))

    def match(self, label: str) -> bool:
        if label == self.lookahead.label:
            print(self.lookahead, self.line)
            # Se label corresponde, tenta pegar o próximo token
            # ou retorna Token de EOF
            try:
                self.lookahead, self.line = next(self.token_generator)
            except StopIteration:
                self.lookahead = Token('EOF', 'EOF')
            return True
        return False

    def start(self) -> ast.Program:
        return self.program()

    def program(self) -> ast.Program:
        return ast.Program(self.stmts())

    def stmts(self) -> ast.Body:
        body: ast.Body = []

        while self.lookahead.label in STATEMENT_TOKENS:
            body.append(self.stmt())

        if self.lookahead.label not in {'RIGHT_BRACE', 'EOF'}:
            raise Exception(
                self.line,
                f'{self.lookahead.value} não inicia uma instrução válida',
            )

        return body

    def stmt(self) -> ast.Statement:
        match self.lookahead.label:
            case 'VAR':
                node = self.declaration()
            case 'IF':
                self.match('IF')
                if not self.match('LEFT_PARENTHESIS'):
                    raise Exception(
                        self.line,
                        f'esperando ( no lugar de {self.lookahead.value}',
                    )

                cond = self.expression()

                if not self.match('RIGHT_PARENTHESIS'):
                    raise Exception(
                        self.line,
                        f'esperando ) no lugar de {self.lookahead.value}',
                    )
                block: ast.Body = self.block()

                _else = None
                if self.lookahead == 'ELSE':
                    self.match('ELSE')
                    _else = self.block()

                return ast.If(condition=cond, body=block, else_stmt=_else)
            case 'WHILE':
                self.match('WHILE')
                if not self.match('LEFT_PARENTHESIS'):
                    raise Exception(
                        self.line,
                        f'esperando ( no lugar de {self.lookahead.value}',
                    )

                cond = self.expression()

                if not self.match('RIGHT_PARENTHESIS'):
                    raise Exception(
                        self.line,
                        f'esperando ) no lugar de {self.lookahead.value}',
                    )
                block: ast.Body = self.block()
                return ast.While(condition=cond, body=block)
            case 'FOR':
                self.match('FOR')
                if not self.match('LEFT_PARENTHESIS'):
                    raise Exception(
                        self.line,
                        f'esperando ( no lugar de {self.lookahead.value}',
                    )

                iterator = self.declaration()

                if not self.match('IN'):
                    raise Exception(
                        self.line,
                        f'esperando "in" no lugar de {self.lookahead.value}',
                    )

                iterable = self.expression()

                if not self.match('RIGHT_PARENTHESIS'):
                    raise Exception(
                        self.line,
                        f'esperando ) no lugar de {self.lookahead.value}',
                    )
                block = self.block()
                return ast.For(iterator, iterable, block)
            case 'FUNC':
                self.match('FUNC')
                name = self.variable('FUNC')
                if not self.match('LEFT_PARENTHESIS'):
                    raise Exception(
                        self.line,
                        f'esperando ( no lugar de {self.lookahead.value}',
                    )
                params: ast.Parameters = self.params()
                if not self.match('RIGHT_PARENTHESIS'):
                    raise Exception(
                        self.line,
                        f'esperando ) no lugar de {self.lookahead.value}',
                    )

                if not self.match('RARROW'):
                    raise Exception(
                        self.line,
                        f'esperando -> no lugar de {self.lookahead.value}',
                    )
                _type = self.lookahead.value
                if not self.match('TYPE'):
                    raise Exception(
                        self.line,
                        f'esperando TYPE no lugar de {self.lookahead.value}',
                    )
                body: ast.Body = self.block(params)
                self.symtable.insert(name, Symbol(name, 'FUNC'))
                return ast.FuncDef(name, _type.upper(), params, body)
            case 'RETURN':
                self.match('RETURN')
                expr: ast.Expression = self.logic_or()
                return ast.Return(expr)
            case 'BREAK':
                self.match('BREAK')
                return ast.Break()
            case 'CONTINUE':
                self.match('CONTINUE')
                return ast.Continue()
            case 'SEQ':
                self.match('SEQ')
                return ast.Seq(body=self.block())
            case 'PAR':
                self.match('PAR')
                return ast.Par(body=self.block())
            case 'C_CHANNEL':
                self.match('C_CHANNEL')
                name = self.variable('C_CHANNEL')
                if not self.match('LEFT_BRACE'):
                    raise Exception(
                        self.line,
                        f'esperando {{ no lugar de {self.lookahead.value}',
                    )
                localhost: ast.Expression = self.sum()
                if not self.match('COMMA'):
                    raise Exception(
                        self.line,
                        f'esperando , no lugar de {self.lookahead.value}',
                    )
                port: ast.Expression = self.sum()
                if not self.match('RIGHT_BRACE'):
                    raise Exception(
                        self.line,
                        f'esperando }} no lugar de {self.lookahead.value}',
                    )
                return ast.CChannel(name=name, _host=localhost, _port=port)
            case _:
                node = self.expression()

        return node

    def params(self) -> ast.Parameters:
        params: ast.Parameters = {}

        while self.lookahead.label != 'RIGHT_PARENTHESIS':
            name, _type, default = self.param()
            params.update({name: (_type.upper(), default)})
            if not self.match('COMMA'):
                break

        return params

    def param(self):
        name = self.lookahead.value
        self.match('ID')
        print(name, self.lookahead)
        if not self.match('COLON'):
            raise Exception(
                self.line,
                f'esperando : no lugar de {self.lookahead.value}',
            )
        _type = self.lookahead.value
        if not self.match('TYPE'):
            raise Exception(
                self.line,
                f'esperando TYPE no lugar de {self.lookahead.value}',
            )
        default = None
        if self.lookahead.label == 'EQUAL':
            self.match('EQUAL')
            default = self.expression()

        return name, _type, default

    def block(self, params: ast.Parameters | None = None) -> ast.Body:
        if not self.match('LEFT_BRACE'):
            raise Exception(
                self.line,
                f'esperando {{ no lugar de {self.lookahead.value}',
            )

        outer = self.symtable
        self.symtable = SymTable(prev=outer)

        if params:
            for name, (_type, _) in params.items():
                self.symtable.insert(name, Symbol(name, _type))

        body: ast.Body = self.stmts()

        if not self.match('RIGHT_BRACE'):
            raise Exception(
                self.line,
                f'esperando }} no lugar de {self.lookahead.value}',
            )

        self.symtable = outer
        return body

    def declaration(self) -> ast.Assign:
        self.match('VAR')
        token = deepcopy(self.lookahead)
        name = token.value
        self.match('ID')
        if not self.match('COLON'):
            raise Exception(
                self.line,
                f'Esperado : no lugar de {self.lookahead.value}',
            )
        _type = self.lookahead.value
        if not self.match('TYPE'):
            raise Exception(
                self.line,
                f'Esperado um TYPE no lugar de {self.lookahead.value}',
            )
        if not self.symtable.insert(name, Symbol(name, _type.upper())):
            raise Exception(
                self.line,
                f'variável {name} já foi declarada neste escopo',
            )
        left = ast.ID(type=_type.upper(), token=token, decl=True)

        if self.match('EQUAL'):
            right: ast.Expression = self.logic_or()
            node = ast.Declaration(left=left, right=right)
        else:
            node = ast.Declaration(left=left, right=None)

        return node

    def variable(self, _type: str):
        name = self.lookahead.value
        if not self.match('ID'):
            raise Exception(
                self.line,
                f'variável esperada ao invés de {self.lookahead.value}',
            )

        if not self.symtable.insert(name, Symbol(name, _type.upper())):
            raise Exception(
                self.line,
                f'variável {name} já foi declarada neste escopo',
            )

        return name

    def expression(self) -> ast.Expression:
        expr = self.logic_or()

        if self.match('EQUAL'):
            right = self.expression()

            if isinstance(expr, ast.Assignable):
                return ast.Assign(left=expr, right=right)

            raise Exception(
                self.line,
                f'{expr.token.value} não pode ser usada para atribuição.',
            )

        return expr

    def logic_or(self) -> ast.Expression:
        expr = self.logic_and()

        while self.lookahead.label == 'OR':
            operator = self.lookahead
            self.match('OR')
            right = self.logic_and()
            expr = ast.Logical('BOOL', operator, expr, right)

        return expr

    def logic_and(self) -> ast.Expression:
        expr = self.equality()

        while self.lookahead.label == 'AND':
            operator = self.lookahead
            self.match('AND')
            right = self.equality()
            expr = ast.Logical('BOOL', operator, expr, right)

        return expr

    def equality(self) -> ast.Expression:
        expr = self.comp()

        while self.lookahead.label in {'EQUAL_EQUAL', 'NOT_EQUAL'}:
            operator = self.lookahead
            self.match(self.lookahead.label)
            right = self.comp()
            expr = ast.Relational('BOOL', operator, expr, right)

        return expr

    def comp(self) -> ast.Expression:
        expr = self.sum()

        while self.lookahead.label in {
            'LESS_EQUAL',
            'GREATER_EQUAL',
            'GREATER',
            'LESS',
        }:
            operator = self.lookahead
            self.match(self.lookahead.label)
            right = self.sum()
            expr = ast.Relational('BOOL', operator, expr, right)

        return expr

    def sum(self) -> ast.Expression:
        expr = self.term()

        while self.lookahead.label in {'PLUS', 'MINUS'}:
            operator = self.lookahead
            self.match(self.lookahead.label)
            right = self.term()
            expr = ast.Arithmetic(expr.type, operator, expr, right)

        return expr

    def term(self) -> ast.Expression:
        expr = self.unary()

        while self.lookahead.label in {'SLASH', 'STAR', 'MOD'}:
            operator = self.lookahead
            self.match(self.lookahead.label)
            right = self.unary()
            expr = ast.Arithmetic(expr.type, operator, expr, right)
        return expr

    def unary(self) -> ast.Expression:
        if self.lookahead.label in {'BANG', 'MINUS'}:
            operator = self.lookahead
            self.match(self.lookahead.label)
            right = self.unary()
            return ast.Unary('EXPR', operator, right)

        return self.primary()

    def primary(self) -> ast.Expression:
        match self.lookahead.label:
            case 'ID':
                expr = self.call()
            case 'FALSE':
                expr = ast.Constant('BOOL', self.lookahead)
                self.match('FALSE')
            case 'TRUE':
                expr = ast.Constant('BOOL', self.lookahead)
                self.match('TRUE')
            case 'STRING':
                expr = ast.Constant('STRING', self.lookahead)
                self.match('STRING')
            case 'NUMBER':
                expr = ast.Constant('NUMBER', self.lookahead)
                self.match('NUMBER')
            case 'LEFT_PARENTHESIS':
                self.match('LEFT_PARENTHESIS')
                expr = self.logic_or()
                if not self.match('RIGHT_PARENTHESIS'):
                    raise Exception(
                        self.line,
                        f'esperando ) no lugar de {self.lookahead.value}',
                    )
            case 'LEFT_BRACKET':
                self.match('LEFT_BRACKET')
                expr = self.list_literal()
                if not self.match('RIGHT_BRACKET'):
                    raise Exception(
                        self.line,
                        f'esperando ] no lugar de {self.lookahead.value}',
                    )
            case 'LEFT_BRACE':
                self.match('LEFT_BRACE')
                expr = self.dict_literal()
                if not self.match('RIGHT_BRACE'):
                    raise Exception(
                        self.line,
                        f'esperando ] no lugar de {self.lookahead.value}',
                    )
            case _:
                raise Exception(self.line, 'Erro de sintaxe.')

        return expr

    def call(self) -> ast.Expression:
        token = self.lookahead
        self.match('ID')

        s: Symbol | None = self.symtable.find(token.value)
        if not s:
            raise Exception(self.line, f'variável {token.value} não declarada')
        expr = ast.ID(type=s.type.upper(), token=token)

        operations = ''
        while True:
            match self.lookahead.label:
                case 'LEFT_BRACKET':
                    expr = self.index(expr)
                case 'DOT':
                    self.match('DOT')
                    operations += self.lookahead.value
                    self.match(self.lookahead.label)
                case 'LEFT_PARENTHESIS':
                    self.match('LEFT_PARENTHESIS')
                    args: ast.Arguments = self.args()
                    expr = ast.Call(
                        type='FUNC',
                        token=expr.token,
                        id=expr,
                        oper=operations,
                        args=args,
                    )
                    if not self.match('RIGHT_PARENTHESIS'):
                        raise Exception(
                            self.line,
                            f'esperando ( no lugar de {self.lookahead.value}',
                        )
                    break
                case _:
                    break

        return expr

    def index(self, ID: ast.ID) -> ast.Expression:
        self.match('LEFT_BRACKET')
        expr = self.index_expression(ID)
        if not self.match('RIGHT_BRACKET'):
            raise Exception(
                self.line,
                f'esperando ] no lugar de {self.lookahead.value}',
            )

        if isinstance(expr, ast.Access):
            return ast.Access(ID.type, ID.token, ID, expr)

        return expr

    def index_expression(self, ID: ast.ID) -> ast.Expression:
        initial = None
        final = None

        if self.lookahead.label == 'COLON':
            self.match('COLON')
            if self.lookahead.label != 'RIGHT_BRACKET':
                final = self.sum()
            return ast.Slice(
                type=ID.type, token=ID.token, initial=initial, final=final
            )

        initial = self.sum()

        if self.match('COLON'):
            if self.lookahead.label != 'RIGHT_BRACKET':
                final = self.sum()
            return ast.Slice(
                type=ID.type, token=ID.token, initial=initial, final=final
            )

        return initial

    def args(self) -> ast.Arguments:
        args: ast.Arguments = []

        while self.lookahead.label != 'RIGHT_PARENTHESIS':
            args.append(self.expression())
            if not self.match('COMMA'):
                break

        return args

    def list_literal(self):
        match self.lookahead.label:
            case 'FOR':
                return self.comprehention()
            case _:
                values = []
                while self.lookahead.label != 'RIGHT_BRACKET':
                    values.append(self.expression())
                    if not self.match('COMMA'):
                        break

                return ast.ArrayLiteral(
                    'LIST', Token(value='[]', label='LIST'), values=values
                )

    def comprehention(self):
        self.match('FOR')
        if not self.match('LEFT_PARENTHESIS'):
            raise Exception(
                self.line,
                f'esperando ( no lugar de {self.lookahead.value}',
            )

        iterator = self.declaration()

        if not self.match('IN'):
            raise Exception(
                self.line,
                f'esperando "in" no lugar de {self.lookahead.value}',
            )

        iterable = self.expression()

        if not self.match('RIGHT_PARENTHESIS'):
            raise Exception(
                self.line,
                f'esperando ) no lugar de {self.lookahead.value}',
            )

        if not self.match('RARROW'):
            raise Exception(
                self.line,
                f'esperando -> no lugar de {self.lookahead.value}',
            )

        expr = self.expression()

        return ast.Comprehention(
            type='COMPREHENTION',
            token=Token(label='COMPREHENTION', value='[for]'),
            iterable=iterable,
            iterator=iterator,
            expr=expr,
        )

    def dict_literal(self) -> ast.DictLiteral:
        entries: ast.DictEntries = {}

        while self.lookahead.label != 'RIGHT_BRACE':
            key = self.lookahead.value
            if not self.match('STRING'):
                raise Exception(
                    self.line,
                    f'esperando STRING no lugar de {self.lookahead.value}',
                )
            if not self.match('COLON'):
                raise Exception(
                    self.line,
                    f'esperando : no lugar de {self.lookahead.value}',
                )
            value = self.expression()
            entries.update({key: value})
            if not self.match('COMMA'):
                break

        return ast.DictLiteral(
            'DICT', Token(value='{}', label='DICT'), entries=entries
        )
