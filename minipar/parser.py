from abc import ABC, abstractmethod
from copy import deepcopy
from symtable import Symbol

from minipar import ast
from minipar.lexer import STATEMENT_TOKENS, Lexer, NextToken
from minipar.symbol import SymTable
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
}


class Parser(ABC):
    @abstractmethod
    def match(self, label: str) -> bool:
        pass

    @abstractmethod
    def start(self) -> ast.Program:
        pass


class ParserImpl(Parser):
    def __init__(self, lexer: Lexer):
        self.lexer: NextToken = lexer.scan()
        self.lookahead, self.line = next(self.lexer)
        self.symtable = SymTable()
        for func_name in DEFAULT_FUNCTION_NAMES.keys():
            self.symtable.insert(func_name, Symbol(func_name, 'FUNC'))

        def match(self, tag: str) -> bool:
            if tag == self.lookahead.tag:
                # Se tag corresponde, tenta pegar o próximo token
                # ou retorna Token de EOF
                try:
                    self.lookahead, self.lineno = next(self.lexer)
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

        if self.lookahead.label not in {'}', 'EOF'}:
            raise Exception(
                self.line,
                f'{self.lookahead.value} não inicia uma instrução válida',
            )

        return body

    def stmt(self) -> ast.Statment:
        match self.lookahead.label:
            case 'VAR':
                return self.declaration()

    def declaration(self) -> ast.Assign:
        # declaration -> var ID : TYPE = expression
        self.match('VAR')
        name = deepcopy(self.lookahead)
        self.match('ID')
        if not self.match(':'):
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
        if not self.symtable.insert(name, Symbol(name, _type)):
            raise Exception(
                self.line,
                f'variável {name} já foi declarada neste escopo',
            )
        left = ast.ID(type=_type.upper(), token=name, decl=True)

        if not self.match('='):
            raise Exception(
                self.line,
                f'Esperado = no lugar de {self.lookahead.value}',
            )
        right: ast.Expression = self.disjunction()
        return ast.Assign(left=left, right=right)
