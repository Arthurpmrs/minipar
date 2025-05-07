from abc import ABC, abstractmethod
from pathlib import Path


class Interpreter(ABC):
    @abstractmethod
    def run(self, source: str) -> str:
        pass


class Minipar(Interpreter):
    def run(self, source: str) -> str:
        if not source:
            raise Exception('The file is empty.')

        # lexer (generate tokens)
        # Parser (generate ast)
        # Semantic (validate ast)
        # Runner (execute based on ast)

        return 'Faltou implementar'
