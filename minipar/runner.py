from abc import ABC, abstractmethod

from minipar import ast
from minipar.symbol import VarTable


class Runner(ABC):
    @abstractmethod
    def run(self, node: ast.Program):
        pass

    @abstractmethod
    def execute(self, node: ast.Node):
        pass

    @abstractmethod
    def enter_scope(self):
        pass

    @abstractmethod
    def exit_scope(self):
        pass


class RunnerImpl(Runner):  # noqa: PLR0904
    var_table: VarTable
    func_table: dict[str, ast.FuncDef]
    DEFAULT_FUNCTIONS = {
        'print': print,
        'input': input,
        # 'to_number': self.number,
        'to_string': str,
        'to_bool': bool,
        # 'sleep': sleep,
        # 'send': self.send,
        # 'close': self.close,
        'len': len,
        # 'isalpha': self.isalpha,
        # 'isnum': self.isnum,
    }

    def __init__(self):
        self.var_table = VarTable()
        self.func_table = {}

    def run(self, node: ast.Program):
        if node.stmts:
            for inst in node.stmts:
                self.execute(inst)

    def execute(self, node: ast.Node):
        method_name = f'exec_{type(node).__name__}'
        method = getattr(self, method_name, None)

        if method:
            return method(node)

    def enter_scope(self):
        self.var_table = VarTable(prev=self.var_table)

    def exit_scope(self):
        if self.var_table.prev:
            self.var_table = self.var_table.prev

    def exec_Declaration(self, node: ast.Declaration):
        rvalue = self.execute(node.right) if node.right else None
        var_name = node.left.name
        self.var_table.table[var_name] = rvalue
        return var_name

    def exec_Assign(self, node: ast.Assign):
        rvalue = self.execute(node.right)
        var_name = node.left.name
        lvalue_table = self.var_table.find(var_name)
        if lvalue_table:
            lvalue_table[var_name] = rvalue
        else:
            self.var_table.table[var_name] = rvalue

    def exec_FuncDef(self, node: ast.FuncDef):
        if node.name not in self.func_table:
            self.func_table[node.name] = node

    def exec_Constant(self, node: ast.Constant):
        match node.type:
            case 'STRING':
                return node.token.value
            case 'NUMBER':
                return eval(node.token.value)
            case 'BOOL':
                return bool(node.token.value)
            case _:
                return node.token.value

    def exec_ID(self, node: ast.ID):
        var_name = node.token.value
        lvalue_table = self.var_table.find(var_name)
        if lvalue_table:
            return lvalue_table.table[var_name]
        else:
            raise Exception(f'variável {var_name} não definida')

    def exec_Access(self, node: ast.Access):
        index = self.execute(node.expr)

        var_name = node.id.token.value
        lvalue_table = self.var_table.find(var_name)
        if lvalue_table:
            return lvalue_table.table[var_name][index]
        else:
            raise Exception(f'variável {var_name} não definida')

    def exec_Logical(self, node: ast.Logical):
        left = self.execute(node.left)

        match node.token.value:
            case '&&':
                if left:
                    return self.execute(node.right)
                return left
            case '||':
                right = self.execute(node.right)
                return left or right
            case _:
                return

    def exec_Relational(self, node: ast.Relational):
        left = self.execute(node.left)
        right = self.execute(node.right)

        if left is None or right is None:
            return

        match node.token.value:
            case '==':
                return left == right
            case '!=':
                return left != right
            case '>':
                return left > right
            case '<':
                return left < right
            case '>=':
                return left >= right
            case '<=':
                return left <= right
            case _:
                return

    def exec_Arithmetic(self, node: ast.Arithmetic):
        left = self.execute(node.left)
        right = self.execute(node.right)

        if left is None or right is None:
            return

        match node.token.value:
            case '+':
                return left + right
            case '-':
                return left - right
            case '*':
                return left * right
            case '/':
                return left / right
            case '%':
                return left % right
            case _:
                return

    def exec_Unary(self, node: ast.Unary):
        expr = self.execute(node.expr)

        if expr is None:
            return

        match node.token.value:
            case '!':
                return not expr
            case '-':
                return expr * (-1)
            case _:
                return

    def exec_ArrayLiteral(self, node: ast.ArrayLiteral):
        computed_values = []
        for value in node.values:
            computed_values.append(self.execute(value))
        return computed_values

    def exec_DictLiteral(self, node: ast.DictLiteral):
        computed_values = {}
        for key, value in node.entries.items():
            computed_values.update({key: self.execute(value)})
        return computed_values

    def exec_Call(self, node: ast.Call):
        name = node.oper if node.oper else node.token.value

        if name in self.DEFAULT_FUNCTIONS:
            args = [self.execute(arg) for arg in node.args]
            return self.DEFAULT_FUNCTIONS[name](*args)

        func = self.func_table.get(str(name))

        if not func:
            return

        self.enter_scope()

        # Compute default values from function parameters
        for param_name, (_, default) in func.params.items():
            if default:
                self.var_table.table[param_name] = self.execute(default)

        # Map args to parameters in function var_table
        for (param_name, _), arg in zip(func.params.items(), node.args):
            self.var_table.table[param_name] = self.execute(arg)

        block_result = self.exec_block(func.body)
        self.exit_scope()
        return block_result

    def exec_Return(self, node: ast.Return):
        return self.execute(node.expr)

    def exec_Break(self, _: ast.Break):
        return 'BREAK'

    def exec_Continue(self, _: ast.Continue):
        return 'CONTINUE'

    def exec_block(self, block: ast.Body):
        ret = None
        for inst in block:
            if isinstance(inst, ast.Return):
                return self.execute(inst)
            else:
                ret = self.execut(inst)

            if ret is None or ret in {'BREAK', 'CONTINUE'}:
                return ret
        return None

    def exec_Comprehention(self, node: ast.Comprehention):
        result = []
        iterable = self.execute(node.iterable)
        self.enter_scope()
        for value in iterable:
            self.var_table.table[node.iterator.left.name] = value
            result.append(self.execute(node.expr))
        self.exit_scope()
        return result
