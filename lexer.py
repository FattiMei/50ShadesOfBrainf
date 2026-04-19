#!/usr/bin/env python3


from enum import Enum
from typing import Iterator


class Token(Enum):
    PLUS        = '+'
    MINUS       = '-'
    SHIFTL      = '<'
    SHIFTR      = '>'
    GETC        = ','
    PUTC        = '.'
    OPENPAREN   = '['
    CLOSEDPAREN = ']'
    END         = 0


def token_generator(src: str) -> Iterator[tuple[Token, int, int]]:
    """
    Generator for the program tokens from a generic source string,
    each token is annotated with the position in the file (row, col)
    """
    LANGUAGE_TOKENS = {
        '+': Token.PLUS,
        '-': Token.MINUS,
        '<': Token.SHIFTL,
        '>': Token.SHIFTR,
        ',': Token.GETC,
        '.': Token.PUTC,
        '[': Token.OPENPAREN,
        ']': Token.CLOSEDPAREN
    }

    row, col = 1, 1

    for c in src:
        if c in LANGUAGE_TOKENS:
            yield (LANGUAGE_TOKENS[c], row, col)

        if c == '\n':
            row += 1
            col = 1
        else:
            col += 1

    while True:
        yield (Token.END, row, col)


class Lexer:
    """
    This class has been designed to support a recursive descent parser
    that needs to look ahead at the next token without consuming it
    """
    LANGUAGE_TOKENS = {
        '+': Token.PLUS,
        '-': Token.MINUS,
        '<': Token.SHIFTL,
        '>': Token.SHIFTR,
        ',': Token.GETC,
        '.': Token.PUTC,
        '[': Token.OPENPAREN,
        ']': Token.CLOSEDPAREN
    }

    def __init__(self, source: str):
        self.tokens = token_generator(source)
        self.curr = next(self.tokens)

    def peek(self) -> tuple[Token, int, int]:
        return self.curr

    def next(self):
        self.curr = next(self.tokens)
