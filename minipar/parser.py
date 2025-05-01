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

    def match(self, label: str) -> bool:
        if label == self.lookahead.label:
            # Se label corresponde, tenta pegar o próximo token
            # ou retorna Token de EOF
            try:
                self.lookahead, self.line = next(self.lexer)
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
        return self.expression()

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

    def expression(self) -> ast.Expression:
        expr = self.logic_or()

        # match self.lookahead.label:
        #     case 'EQ':
                
    def logic_or(self) -> ast.Expression:
        expr = self.logic_and()

        while(self.lookahead.label == "OR"):
            operator = self.lookahead
            self.match("OR")
            right = self.logic_and()
            expr = ast.Logical("BOOL", operator, expr, right)

        return expr
    
    def logic_and(self) -> ast.Expression:
        expr = self.equality()
        
        while(self.lookahead.label == "AND"):
            operator = self.lookahead
            self.match("AND")
            right = self.equality()
            expr = ast.Logical("BOOL", operator, expr, right)

        return expr
    
    def equality(self) -> ast.Expression:
        expr = self.comp()

        while self.lookahead.label in ["EQUAL_EQUAL", "NOT_EQUAL"]:
            operator = self.lookahead
            self.match(self.lookahead.label)
            right = self.comp()
            expr = ast.Relational("BOOL", operator, expr, right)
        
        return expr
    
    def comp(self) -> ast.Expression:
        expr = self.sum()

        while self.lookahead.label in ["LESS_EQUAL", "GREATER_EQUAL", "GRATER", "LESS"]:
            operator = self.lookahead
            self.match(self.lookahead.label)
            right = self.sum()
            expr = ast.Relational("BOOL", operator, expr, right)
        
        return expr

    def sum(self) -> ast.Expression:
        expr = self.term()

        while self.lookahead.label in ["PLUS", "MINUS"]:
            operator = self.lookahead
            self.match(self.lookahead.label)
            right = self.term()
            expr = ast.Arithmetic(expr.left.type, operator, expr, right)
        
        return expr
    


    def term(self) -> ast.Expression:
        expr = self.unary()

        while self.lookahead.label in ["SLASH", "STAR", "MOD"]:
            operator = self.lookahead
            self.match(self.lookahead.label)
            right = self.unary()
            expr = ast.Arithmetic(expr.left.type, operator, expr, right)
        return expr
    
    def unary(self) -> ast.Expression:
        if self.lookahead.label in ["BANG", "MINUS"]:
            operator = self.lookahead
            self.match(self.lookahead.label)
            right = self.unary()
            return ast.Unary("EXPR", operator, right)
        
        return self.primary()

    def primary(self) -> ast.Expression:
        match self.lookahead.label:
            case "FALSE":
                expr = ast.Constant("BOOL", self.lookahead)
                self.match("FALSE")
            case "TRUE":
                expr = ast.Constant("BOOL", self.lookahead)
                self.match("TRUE")
            case "STRING":
                expr = ast.Constant("STRING", self.lookahead)
                self.match("STRING")
            case "NUMBER":
                expr = ast.Constant("NUMBER", self.lookahead)
                self.match("NUMBER")
            case "SEILA MEU IRMAO":
                pass
        return expr