import pprint

from minipar.lexer import LexerImpl
from minipar.parser import ParserImpl
from minipar.semantic import SemanticImpl

if __name__ == '__main__':
    path_to_source = './examples/minipar/ex1.minipar'

    with open(path_to_source, 'r', encoding='utf-8') as f:
        source = f.read()
        lexer = LexerImpl(source)
        parser = ParserImpl(lexer)
        semantic = SemanticImpl()
        ast = parser.start()
        semantic.visit(ast)

        pprint.pprint(ast)
        print(parser.symtable.table)
