from abc import ABC, abstractmethod
from pathlib import Path


class Interpreter(ABC):
    @abstractmethod
    def run(path_to_source: Path) -> str:
        pass


class Minipar(Interpreter):
    def run(path_to_source: Path) -> str:
        if not path_to_source.is_file():
            raise Exception('There is no file.')

        with open(path_to_source, 'r', encoding='utf-8') as f:
            source = f.read()

        if not source:
            raise Exception('The file is empty.')

        # lexer (generate tokens)
        # Parser (generate ast)
        # Semantic (validate ast)
        # Runner (execute based on ast)

        return ''
