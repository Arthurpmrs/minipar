import io
import sys
from abc import ABC, abstractmethod
from contextlib import contextmanager, redirect_stderr, redirect_stdout

from minipar.lexer import LexerImpl
from minipar.parser import ParserImpl
from minipar.runner import RunnerImpl
from minipar.semantic import SemanticImpl


@contextmanager
def redirect_stdin(new_stdin):
    old_stdin = sys.stdin
    sys.stdin = new_stdin
    try:
        yield
    finally:
        sys.stdin = old_stdin


class Interpreter(ABC):
    @abstractmethod
    def run(self, source: str) -> str:
        pass


class Minipar(Interpreter):
    def run(self, source: str, input_data: str = '') -> str:
        if not source:
            raise Exception('Não há código para executar.')

        input_buffer = io.StringIO(input_data)
        output_buffer = io.StringIO()
        with (
            redirect_stdout(output_buffer),
            redirect_stderr(output_buffer),
            redirect_stdin(input_buffer),
        ):
            try:
                lexer = LexerImpl(source)

                parser = ParserImpl(lexer)
                ast = parser.start()

                semantic = SemanticImpl()
                semantic.visit(ast)

                runner = RunnerImpl()
                runner.run(ast)
            except EOFError:
                print('[erro] Fim da entrada alcançado.')
            except Exception as e:
                print(f'[erro] {e}')

        return output_buffer.getvalue()
