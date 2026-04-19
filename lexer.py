#!/usr/bin/env python3


from enum import Enum
from typing import Iterator


TEST_SOURCE = "+++[.->[++--]><].[]"


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

    def get_token_repr(self) -> str:
        return self.value


def token_generator(src: str) -> Iterator[tuple[Token, int, int]]:
    """
    Generator for the program tokens from a generic source string,
    each token is annotated with the position in the file (row, col)

    This generator is meant to never terminate, but instead keeps
    yielding the `END` token
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

    This class is parametric on the type of the token generator and
    can potentially be reused on other projects
    """
    def __init__(self, source: str):
        self.tokens = token_generator(source)
        self.curr = next(self.tokens)

    def peek(self) -> tuple[Token, int, int]:
        return self.curr

    def next(self):
        self.curr = next(self.tokens)

    def consume(self) -> tuple[Token, int, int]:
        tmp = self.peek()
        self.next()
        return tmp


if __name__ == '__main__':
    import itertools

    lexer = Lexer(TEST_SOURCE)

    token_stream = map(
        lambda self: self.consume(),
        itertools.repeat(lexer)
    )

    reconstructed_source = ''.join(
        map(
            lambda t: t[0].value,
            itertools.takewhile(
                lambda t: t[0] != Token.END,
                token_stream
            )
        )
    )

    assert(TEST_SOURCE == reconstructed_source)
