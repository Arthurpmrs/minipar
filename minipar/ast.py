"""
Módulo da Árvore Sintática Abstrata (AST)

O módulo da AST conta com uma estrutura de classes responsável
por representa o conjunto de declarações e expressões da linguagem
"""

from dataclasses import dataclass

from minipar.token import Token


class Node:
    pass


@dataclass
class Statement(Node):
    pass


@dataclass
class Expression(Node):
    type: str
    token: Token

    @property
    def name(self) -> str | None:
        if self.token:
            return self.token.value


type Body = list[Statement]
type Arguments = list[Expression]
type Parameters = dict[str, tuple[str, Expression | None]]


@dataclass
class Constant(Expression):
    pass


@dataclass
class ID(Expression):
    decl: bool = False


@dataclass
class Access(Expression):
    id: ID
    expr: Expression


@dataclass
class Logical(Expression):
    left: Expression
    right: Expression


@dataclass
class Relational(Expression):
    left: Expression
    right: Expression


@dataclass
class Arithmetic(Expression):
    left: Expression
    right: Expression


@dataclass
class Unary(Expression):
    expr: Expression


@dataclass
class Call(Expression):
    id: ID | None
    args: Arguments
    oper: str | None


@dataclass
class Program(Statement):
    stmts: Body | None


@dataclass
class Assign(Statement):
    left: Expression
    right: Expression


@dataclass
class Declaration(Statement):
    left: Expression
    right: Expression | None


@dataclass
class Return(Statement):
    expr: Expression


@dataclass
class Break(Statement):
    pass


@dataclass
class Continue(Statement):
    pass


@dataclass
class FuncDef(Statement):
    name: str
    return_type: str
    params: Parameters
    body: Body


@dataclass
class If(Statement):
    condition: Expression
    body: Body
    else_stmt: Body | None


@dataclass
class While(Statement):
    condition: Expression
    body: Body


@dataclass
class For(Statement):
    iterator: Declaration
    iterable: Expression
    body: Body


@dataclass
class Par(Statement):
    body: Body


@dataclass
class Seq(Statement):
    body: Body


@dataclass
class Channel(Statement):
    name: str
    _localhost: Expression
    _port: Expression

    @property
    def localhost(self):
        return self._localhost.token.value

    @property
    def localhost_node(self):
        return self._localhost

    @property
    def port(self):
        return self._port.token.value

    @property
    def port_node(self):
        return self._port


@dataclass
class SChannel(Channel):
    func_name: str
    description: Expression


@dataclass
class CChannel(Channel):
    pass
