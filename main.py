import pprint

from minipar.lexer import LexerImpl
from minipar.parser import ParserImpl
from minipar.runner import RunnerImpl

if __name__ == '__main__':
    path_to_source = './examples/minipar/okok.minipar'

    with open(path_to_source, 'r', encoding='utf-8') as f:
        source = f.read()
        lexer = LexerImpl(source)
        parser = ParserImpl(lexer)
        ast = parser.start()
        pprint.pprint(ast)
        print(parser.symtable.table)
        runner = RunnerImpl()
        runner.run(ast)
        print()
        pprint.pprint(runner.var_table)
        pprint.pprint(runner.func_table)
