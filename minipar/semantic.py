from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from minipar import ast
from minipar.parser import DEFAULT_FUNCTION_NAMES


class Semantic(ABC):
    @abstractmethod
    def visit(self, node: ast.Node):
        pass

    @abstractmethod
    def generic_visit(self, node: ast.Node):
        pass


@dataclass  # noqa: PLR0904
class SemanticImpl(Semantic):
    context_stack: list[ast.Node] = field(default_factory=list)
    function_table: dict[str, ast.FuncDef] = field(default_factory=dict)

    def __post_init__(self):
        self.default_func_names = list(DEFAULT_FUNCTION_NAMES.keys())

    def visit(self, node: ast.Node):
        meth_name: str = f'visit_{type(node).__name__}'
        visitor = getattr(self, meth_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ast.Node):
        self.context_stack.append(node)

        for attr in dir(node):
            value = getattr(node, attr)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.Node):
                        self.visit(item)
            elif isinstance(value, ast.Node):
                self.visit(node)

        self.context_stack.pop()

    def visit_Assign(self, node: ast.Assign):
        if not (
            isinstance(node.left, ast.ID) or isinstance(node.left, ast.Access)
        ):
            raise Exception(
                'Erro: Atribuição deve ser feita para uma variável.'
            )

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if (
            isinstance(node.left, ast.Access)
            or left_type == 'LIST'
            or isinstance(node.right, ast.Arithmetic)
        ):
            return

        if left_type != right_type:
            raise Exception(
                f'Erro de Tipagem: esperado {left_type}, mas obteve {right_type}.'
            )

    def visit_Declaration(self, node: ast.Declaration):
        if not isinstance(node.left, ast.ID):
            raise Exception(
                'Erro: Atribuição deve ser feita para uma variável'
            )

        if node.right is not None:
            left_type = self.visit(node.left)
            right_type = self.visit(node.right)

            if (
                isinstance(node.right, ast.Access)
                or isinstance(node.left, ast.Access)
                or isinstance(node.right, ast.ArrayLiteral)
                or isinstance(node.right, ast.Comprehention)
                or isinstance(node.right, ast.Arithmetic)
            ):
                return
            elif left_type != right_type:
                raise Exception(
                    f'Erro de Tipagem: esperado {left_type}, mas obteve {right_type}.'
                )

    def visit_Return(self, node: ast.Return):
        function: ast.FuncDef = next(
            (
                n
                for n in self.context_stack[::-1]
                if isinstance(n, ast.FuncDef)
            ),
            None,
        )

        if function is None:
            raise Exception('Erro: declaração de retorno fora de uma função.')

        expr_type = self.visit(node.expr)
        if function.return_type != expr_type:
            raise Exception(
                f'Erro de Tipagem: tipo de retorno esperado {function.return_type}, mas obteve {expr_type}.'
            )

    def visit_Break(self, _: ast.Break):
        if not any(
            isinstance(parent, (ast.While, ast.For))
            for parent in self.context_stack
        ):
            raise Exception('Erro: declaração de break fora de um laço.')

    def visit_Continue(self, _: ast.Continue):
        if not any(
            isinstance(parent, (ast.While, ast.For))
            for parent in self.context_stack
        ):
            raise Exception('Erro: declaração de continue fora de um laço.')

    def visit_FuncDef(self, node: ast.FuncDef):
        if any(
            isinstance(parent, (ast.If, ast.While, ast.Par))
            for parent in self.context_stack
        ):
            raise Exception(
                'Erro: Proibido criar funções dentro de escopos locais.'
            )

        if node.name not in self.function_table:
            self.function_table[node.name] = node

        self.generic_visit(node)

    def visit_Block(self, block: ast.Body):
        for node in block:
            self.visit(node)

    def visit_If(self, node: ast.If):
        conditon_type = self.visit(node.condition)

        if conditon_type not in {'BOOL', 'LIST', 'DICT'}:
            raise Exception(
                f'Erro de Tipagem: tipo de retorno esperado BOOL, mas obteve {conditon_type}.'
            )

        self.context_stack.append(node)
        self.visit_Block(node.body)
        if node.else_stmt:
            self.visit_Block(node.else_stmt)
        self.context_stack.pop()

    def visit_While(self, node: ast.While):
        conditon_type = self.visit(node.condition)

        if conditon_type != 'BOOL':
            raise Exception(
                f'Erro de Tipagem: tipo de retorno esperado BOOL, mas obteve {conditon_type}.'
            )

        self.context_stack.append(node)
        self.visit_Block(node.body)
        self.context_stack.pop()

    def visit_For(self, node: ast.For):
        iterable_type = self.visit(node.iterable)

        if iterable_type not in {'LIST', 'DICT'}:
            raise Exception(
                'Erro de Tipagem: O interável deve ser do tipo LIST ou DICT.'
            )

        self.context_stack.append(node)
        self.visit_Block(node.body)
        self.context_stack.pop()

    def visit_Par(self, node: ast.Par):
        if any(not isinstance(inst, ast.Call) for inst in node.body):
            raise Exception(
                'Erro: Apenas chamadas de função são permitidas dentro de execução paralela.'
            )

    def visit_CChannel(self, node: ast.CChannel):
        host_type = self.visit(node._host)
        port_type = self.visit(node._port)

        if host_type != 'STRING':
            raise Exception(
                'Erro de Tipagem: O localhost deve ser do tipo STRING.'
            )

        if port_type != 'NUMBER':
            raise Exception(
                'Erro de Tipagem: A porta deve ser do tipo NUMBER.'
            )

    def visit_SChannel(self, node: ast.SChannel):
        host_type = self.visit(node._host)
        port_type = self.visit(node._port)
        description_type = self.visit(node.description)
        function = self.function_table[node.func_name]

        if host_type != 'STRING':
            raise Exception(
                'Erro de Tipagem: O localhost deve ser do tipo STRING.'
            )

        if port_type != 'NUMBER':
            raise Exception(
                'Erro de Tipagem: A porta deve ser do tipo NUMBER.'
            )

        if description_type != 'STRING':
            raise Exception(
                'Erro de Tipagem: A descrição deve ser do tipo STRING'
            )

        if function.return_type != 'STRING':
            raise Exception(
                'Erro de Tipagem: A função associada ao canal deve retornar um valor do tipo STRING.'
            )

    def visit_Slice(self, node: ast.Slice):
        inital_type = self.visit(node.initial)
        final_type = self.visit(node.final)

        if node.initial and inital_type != 'NUMBER':
            raise Exception(
                'Erro de Tipagem: Os índices inicial devem ser do tipo NUMBER.'
            )

        if node.final and final_type != 'NUMBER':
            raise Exception(
                'Erro de Tipagem: Os índices final devem ser do tipo NUMBER.'
            )
        return node.type

    def visit_Comprehention(self, node: ast.Comprehention):
        iterable_type = self.visit(node.iterable)

        if iterable_type not in {'LIST', 'DICT'}:
            raise Exception(
                'Erro de Tipagem: O identificador deve ser do tipo LIST ou DICT.'
            )
        return node.type

    def visit_Access(self, node: ast.Access):
        id_type = self.visit(node.id)

        if id_type not in {'LIST', 'DICT', 'STRING'}:
            raise Exception(
                'Erro de Tipagem: O identificador deve ser do tipo LIST, DICT ou STRING.'
            )

        expr_type = self.visit(node.expr)
        if id_type in {'STRING', 'LIST'}:
            if expr_type != 'NUMBER':
                raise Exception(
                    'Erro de Tipagem: O índice deve ser do tipo NUMBER.'
                )
        elif expr_type != 'STRING':
            raise Exception(
                'Erro de Tipagem: A chave deve ser do tipo STRING.'
            )

        return node.type

    def visit_ArrayLiteral(self, node: ast.ArrayLiteral):
        element_types = {self.visit(element) for element in node.values}

        # if len(element_types) > 1:
        #     raise Exception(
        #         'Erro de Tipagem: Todos os elementos do array devem ser do mesmo tipo.'
        #     )

        return next(iter(element_types)) if element_types else None

    def visit_DictLiteral(self, node: ast.DictLiteral):
        return node.type

    def visit_Call(self, node: ast.Call):
        func_name = node.oper if node.oper else node.token.value

        if (
            func_name not in self.function_table
            and func_name not in DEFAULT_FUNCTION_NAMES
        ):
            raise Exception(f'Erro: A função "{func_name}" não está definida.')

        for arg in node.args:
            self.visit(arg)

        if func_name in DEFAULT_FUNCTION_NAMES:
            return DEFAULT_FUNCTION_NAMES[func_name]

        function = self.function_table.get(str(func_name))

        nondefault_params = [
            default
            for _, default in function.params.values()
            if default is not None
        ]

        if len(node.args) < len(nondefault_params):
            raise Exception(
                f'Erro: A função "{func_name}" recebeu mais argumentos do que o esperado. '
                f'Esperado {len(function.params)}, mas obteve {len(node.args)}.'
            )

        return function.return_type

    def visit_Constant(self, node: ast.Constant):
        return node.type

    def visit_ID(self, node: ast.ID):
        return node.type

    def visit_Logical(self, node: ast.Logical):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if left_type != 'BOOL' or right_type != 'BOOL':
            raise Exception(
                'Erro de Tipagem: Operações lógicas requerem operandos do tipo BOOL.'
            )

        return 'BOOL'

    def visit_Relational(self, node: ast.Relational):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if isinstance(node.left, ast.Access) or isinstance(
            node.right, ast.Access
        ):
            return 'BOOL'

        if left_type != right_type:
            raise Exception(
                f'Erro de Tipagem: esperado {left_type}, mas obteve {right_type}.'
            )

        return 'BOOL'

    def visit_Arithmetic(self, node: ast.Arithmetic):
        if isinstance(node.right, ast.Access) or isinstance(
            node.left, ast.Access
        ):
            return

        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if isinstance(node.right, ast.Access) or isinstance(
            node.right, ast.ArrayLiteral
        ):
            return left_type
        elif isinstance(node.left, ast.Access) or isinstance(
            node.left, ast.ArrayLiteral
        ):
            return right_type

        if node.token.value == '+':
            if left_type != right_type:
                raise Exception(
                    f'Erro de Tipagem: Operação "+" requer operandos do mesmo tipo, mas obteve {left_type} e {right_type}.'
                )
        elif left_type != 'NUMBER' or right_type != 'NUMBER':
            raise Exception(
                f'Erro de Tipagem: Operação "{node.token.value}" requer operandos do tipo NUMBER, mas obteve {left_type} e {right_type}.'
            )

        return left_type

    def visit_Unary(self, node: ast.Unary):
        expr_type = self.visit(node.expr)

        if node.token.label == '-' and expr_type != 'NUMBER':
            raise Exception(
                f'Erro de Tipagem: Operação "{node.token.label}" requer um operando do tipo NUMBER, mas obteve {expr_type}.'
            )
        elif node.token.label == '!' and expr_type not in {
            'BOOL',
            'LIST',
            'DICT',
        }:
            raise Exception(
                f'Erro de Tipagem: Operação "{node.token.label}" requer um operando do tipo BOOL, mas obteve {expr_type}.'
            )

        return expr_type
