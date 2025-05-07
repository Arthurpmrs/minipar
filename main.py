import pprint

from minipar.lexer import LexerImpl
from minipar.parser import ParserImpl
from minipar.runner import RunnerImpl

if __name__ == '__main__':
    path_to_source = './examples/minipar/ex9.minipar'

    with open(path_to_source, 'r', encoding='utf-8') as f:
        source = f.read()
        lexer = LexerImpl(source)
        parser = ParserImpl(lexer)
        ast = parser.start()
        # pprint.past)
        # parser.symtable.table)
        runner = RunnerImpl()
        runner.run(ast)
        # pprint.prunner.var_table)
        # pprint.prunner.func_table)
