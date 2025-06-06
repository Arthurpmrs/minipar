"""
Módulo da Tabela de Símbolos e Variáveis

O módulo das tabelas define as classes que representam
o acesso as variáveis de acordo com seus escopos na análise
sintática e no módulo de execução
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Union


@dataclass
class Symbol:
    var: str
    type: str


@dataclass
class SymTable:
    table: dict[str, Symbol] = field(default_factory=dict)
    prev: Optional['SymTable'] = None

    def insert(self, string: str, symbol: Symbol):
        if self.table.get(string):
            return False
        self.table[string] = symbol
        return True

    def find(self, string: str) -> Symbol | None:
        st = self
        while st:
            value = st.table.get(string)
            if value is None:
                st = st.prev
                continue
            return value


@dataclass
class VarTable:
    table: dict[str, Any] = field(default_factory=dict)
    prev: Optional['VarTable'] = None

    def find(self, string: str) -> Union['VarTable', None]:
        st = self
        while st:
            if string in st.table:
                return st
            st = st.prev
