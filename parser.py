#!/usr/bin/env python3

"""
This file is responsible for the parsing of the source code.
There isn't much structure to recover from a brainf program since
its primitives are characters, but I need to annotate the branch
instructions with the position (row, col) in the original source.
"""


from enum import Enum


class TokenType(Enum):
    PLUS  = '+'
    MINUS = '-'
    MOVEL = '<'
    MOVER = '>'
    GETC  = ','
    PUTC  = '.'
    BZ    = '['
    BNZ   = ']'


class Token:
    def __init__(self, ttype: TokenType, annotation=None):
        self.ttype = ttype
        self.annotation = annotation

    def __repr__(self) -> str:
        if self.annotation is None:
            return f'{{ {self.ttype} }}'
        else:
            return f'{{ {self.ttype} at {self.annotation} }}'


def parse_source(src: str) -> list[Token]:
    tokens = []
    row = 1
    col = 1

    for c in src:
        curr = None

        if c == '+':
            curr = TokenType.PLUS
        elif c == '-':
            curr = TokenType.MINUS
        elif c == '<':
            curr = TokenType.MOVEL
        elif c == '>':
            curr = TokenType.MOVER
        elif c == ',':
            curr = TokenType.GETC
        elif c == '.':
            curr = TokenType.PUTC
        elif c == '[':
            curr = TokenType.BZ
        elif c == ']':
            curr = TokenType.BNZ

        if curr is not None:
            if curr in [TokenType.BZ, TokenType.BNZ]:
                token = Token(curr, (row,col))
            else:
                token = Token(curr)

            tokens.append(token)

        if c == '\n':
            row += 1
            col = 1
        else:
            col += 1

    return tokens
