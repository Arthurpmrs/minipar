import pprint
import traceback

from minipar.lexer import LexerImpl
from minipar.parser import ParserImpl
from minipar.runner import RunnerImpl
from minipar.semantic import SemanticImpl

if __name__ == '__main__':
    filename = input('Digite o nome do arquivo de exemplo: ')
    path_to_source = f'./examples/minipar/{filename}.minipar'

    with open(path_to_source, 'r', encoding='utf-8') as f:
        source = f.read()
        lexer = LexerImpl(source)
        parser = ParserImpl(lexer)
        ast = parser.start()

        semantic = SemanticImpl()
        semantic.visit(ast)
        try:
            semantic.visit(ast)
        except Exception as _:
            print(traceback.format_exc)
            pprint.pprint(semantic.context_stack)

        runner = RunnerImpl()
        runner.run(ast)
