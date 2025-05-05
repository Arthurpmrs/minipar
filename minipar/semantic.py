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


@dataclass
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
