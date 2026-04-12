#!/usr/bin/env python3

"""
This file is responsible for the parsing of the source code.
There isn't much structure to recover from a brainf program since
its primitives are characters, but I need to annotate the branch
instructions with the position (row, col) in the original source.
"""


import ir
from enum import Enum


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


"""
This function is a generator for the program tokens, each token is
annotated with the position in the file
"""
def token_generator(src: str):
    row = 1
    col = 1

    for c in src:
        if c in LANGUAGE_TOKENS:
            yield (LANGUAGE_TOKENS[c], row, col)

        if c == '\n':
            row += 1
            col = 1
        else:
            col += 1


"""
This function is a generator of basic block with increasing labels.
The basic blocks generated are guaranteed to have unique labels
"""
def bb_generator():
    count = 0

    while True:
        yield ir.BasicBlock(label=count)
        count += 1


"""
Returns a list of basic blocks and the first one is the entry point.
It may fail when the program is ill-formed because of parenthesis mismatch.
"""
def parse_source(src: str) -> list[ir.BasicBlock]:
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
                    debug_info=(row,col)
                )
            )

            bb_stack.append(curr)
            curr = new

        elif token == Token.CLOSEDPAREN:
            new = next(bb_gen)
            basic_blocks.append(new)

            if len(bb_stack) == 0:
                print(f"ERROR: found `]` at ({row},{col}) but the corresponding `[` was never opened")
                return None

            old = bb_stack.pop()
            old.get_terminator().target_block = new

            curr.append(
                ir.BranchIfNotZero(
                    target_block=old.get_terminator().fallthrough_block,
                    fallthrough_block=new
                )
            )
            curr = new

    # in a well formed program all the parenthesis should be closed
    if len(bb_stack) > 0:
        missing_closing = [bb.get_terminator().debug_info for bb in bb_stack]
        print(f"ERROR: some parenthesis are still to be closed at {missing_closing}")
        return None

    # at the end of the program we insert a return instruction
    # so that every basic block is well formed
    curr.append(ir.Return())

    return basic_blocks
