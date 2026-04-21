#!/usr/bin/env python3


from brainf import ir
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


def token_generator(src: str) -> Iterator[tuple[Token, int, int]]:
    """
    Generator for the program tokens from a generic source string,
    each token is annotated with the position in the file (row, col)

    This generator is meant to never terminate, but instead keeps
    yielding the `END` token
    """
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


def bb_generator():
    """
    This function is a generator of basic block with increasing labels.
    The basic blocks generated are guaranteed to have unique labels
    """
    count = 0

    while True:
        yield ir.BasicBlock(label=count)
        count += 1


def parse_source(src: str) -> ir.Program:
    """
    Returns a list of basic blocks and the first one is the entry point.
    It may fail when the program is ill-formed because of parenthesis mismatch.
    """
    bb_gen = bb_generator()
    curr = next(bb_gen)
    basic_blocks = [curr]

    # this is the data structure I use for keeping track
    # of which BB I still need to properly connect
    bb_stack = []

    for (token, row, col) in token_generator(src):
        if token == Token.PLUS:
            curr.append(ir.Increment())
        elif token == Token.MINUS:
            curr.append(ir.Decrement())
        elif token == Token.SHIFTL:
            curr.append(ir.MoveLeft())
        elif token == Token.SHIFTR:
            curr.append(ir.MoveRight())
        elif token == Token.GETC:
            curr.append(ir.GetChar())
        elif token == Token.PUTC:
            curr.append(ir.PutChar())

        # we are at the end of the current basic block
        elif token == Token.OPENPAREN:
            new = next(bb_gen)
            basic_blocks.append(new)

            curr.append(
                ir.BranchIfZero(
                    target_block=None, # we don't know it yet
                    fallthrough_block=new,
                    source_pos=(row,col)
                )
            )

            bb_stack.append(curr)
            curr = new

        elif token == Token.CLOSEDPAREN:
            new = next(bb_gen)
            basic_blocks.append(new)

            if len(bb_stack) == 0:
                raise SyntaxError(
                    f"ERROR: found `]` at ({row},{col}) but the corresponding `[` was never opened"
                )

            old = bb_stack.pop()
            old.get_terminator().target_block = new

            curr.append(
                ir.BranchIfNotZero(
                    target_block=old.get_terminator().fallthrough_block,
                    fallthrough_block=new
                )
            )
            curr = new

        elif token == Token.END:
            curr.append(ir.Return())
            break

    # in a well formed program all the parenthesis should be closed
    if len(bb_stack) > 0:
        missing_closing = [bb.get_terminator().source_pos for bb in bb_stack]
        raise SyntaxError(
            f"ERROR: some parenthesis are still to be closed at {missing_closing}"
        )

    return ir.Program(basic_blocks)
