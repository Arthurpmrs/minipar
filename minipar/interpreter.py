import io
from abc import ABC, abstractmethod
from contextlib import redirect_stdout

from minipar.lexer import LexerImpl
from minipar.parser import ParserImpl
from minipar.runner import RunnerImpl
from minipar.semantic import SemanticImpl


class Interpreter(ABC):
    @abstractmethod
    def run(self, source: str) -> str:
        pass


class Minipar(Interpreter):
    def run(self, source: str) -> str:
        if not source:
            raise Exception('Não há código para executar.')

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            try:
                lexer = LexerImpl(source)

                parser = ParserImpl(lexer)
                ast = parser.start()

                semantic = SemanticImpl()
                semantic.visit(ast)

                runner = RunnerImpl()
                runner.run(ast)
            except Exception as e:
                print(e)

        return buffer.getvalue()
