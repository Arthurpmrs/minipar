import re
from abc import ABC, abstractmethod
from typing import Generator

from minipar.token import Token

TOKEN_PATTERNS = [
    ('NAME', r'[A-Za-z_][A-Za-z0-9_]*'),
    ('NUMBER', r'\b\d+\.\d+|\.\d+|\d+\b'),
    ('RARROW', r'->'),
    ('STRING', r'"([^"]*)"'),
    ('LINECOMMENT', r'#.*'),
    ('BLOCKCOMMENT', r'/\*[\s\S]*?\*/'),
    ('OR', r'\|\|'),
    ('AND', r'&&'),
    ('EQUAL_EQUAL', r'=='),
    ('NOT_EQUAL', r'!='),
    ('LESS_EQUAL', r'<='),
    ('GREATER_EQUAL', r'>='),
    ('GRATER', r'>'),
    ('LESS', r'<'),
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('STAR', r'\*'),
    ('SLASH', r'/'),
    ('BANG', r'!'),
    ('MOD', r'%'),
    ('FALSE', r'false'),
    ('TRUE', r'true'),
    ('NEWLINE', r'\n'),
    ('WHITESPACE', r'\s+'),
    ('OTHER', r'.'),
]

TOKEN_REGEX = '|'.join(
    f'(?P<{name}>{pattern})' for name, pattern in TOKEN_PATTERNS
)

STATEMENT_TOKENS = {
    'ID',
    'FUNC',
    'IF',
    'ELSE',
    'WHILE',
    'RETURN',
    'BREAK',
    'CONTINUE',
    'SEQ',
    'PAR',
    'C_CHANNEL',
    'S_CHANNEL',
    'VAR',
}

type NextToken = Generator[tuple[Token, int]]


class Lexer(ABC):
    @abstractmethod
    def scan(self) -> NextToken:
        pass


class LexerImpl(Lexer):
    source: str
    line: int = 1
    token_labels: dict[str, str]

    def __init__(self, source: str):
        self.source = source
        self.token_labels = {
            'number': 'TYPE',
            'bool': 'TYPE',
            'string': 'TYPE',
            'void': 'TYPE',
            'true': 'TRUE',
            'false': 'FALSE',
            'func': 'FUNC',
            'while': 'WHILE',
            'if': 'IF',
            'else': 'ELSE',
            'return': 'RETURN',
            'break': 'BREAK',
            'continue': 'CONTINUE',
            'par': 'PAR',
            'seq': 'SEQ',
            'c_channel': 'C_CHANNEL',
            's_channel': 'S_CHANNEL',
        }

    def scan(self) -> NextToken:
        compiled_re = re.compile(TOKEN_REGEX)

        for match in compiled_re.finditer(self.source):
            token_label = match.lastgroup
            token_value = match.group()

            if token_label in {'WHITESPACE', 'LINECOMMENT'}:
                continue
            elif token_label == 'BLOCKCOMMENT':
                self.line += token_value.count('\n')
                continue
            elif token_label == 'NEWLINE':
                self.line += 1
                continue
            elif token_label == 'NAME':
                token_label = self.token_labels.get(token_value, 'ID')
            elif token_label == 'STRING':
                token_value = token_value.replace('"', '')
            elif token_label == 'OTHER':
                token_label = token_value

            yield Token(token_label, token_value), self.line
