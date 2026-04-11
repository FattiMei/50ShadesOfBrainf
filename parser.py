#!/usr/bin/env python3

"""
This file is responsible for the parsing of the source code.
There isn't much structure to recover from a brainf program since
its primitives are characters, but I need to annotate the branch
instructions with the position (row, col) in the original source.
"""


import ir


LANGUAGE_TOKENS = '+-<>,.[]'
CONTROL_TOKENS = '[]'


"""
Returns a list of basic blocks and the first one is the entry point.
It may fail when the program is ill-formed because of parenthesis mismatch.
"""
def parse_source(src: str) -> list[ir.BasicBlock]:
    curr = ir.BasicBlock()
    basic_blocks = [curr]

    # this is the data structure I use for keeping track
    # of which BB I still need to properly connect
    bb_stack = []

    row, col = 1, 1
    for c in src:
        if c == '+':
            curr.append(ir.Increment())
        elif c == '-':
            curr.append(ir.Decrement())
        elif c == '<':
            curr.append(ir.MoveLeft())
        elif c == '>':
            curr.append(ir.MoveRight())
        elif c == ',':
            curr.append(ir.GetChar())
        elif c == '.':
            curr.append(ir.PutChar())

        # we are at the end of the current basic block
        # a branch instruction must be made
        elif c == '[':
            next = ir.BasicBlock()
            basic_blocks.append(next)

            curr.append(
                ir.BranchIfZero(
                    target_block=None, # we don't know it yet
                    fallthrough_block=next
                )
            )

            assert(curr.is_well_formed())
            bb_stack.append(curr)
            curr = next

        elif c == ']':
            next = ir.BasicBlock()
            basic_blocks.append(next)

            if len(bb_stack) > 0:
                old = bb_stack.pop()
                assert(old.is_well_formed())
                old.get_terminator().target_block = next

                curr.append(
                    ir.BranchIfNotZero(
                        target_block=old.get_terminator().fallthrough_block,
                        fallthrough_block=next
                    )
                )
                curr = next
            else:
                print(f"[ERROR] parenthesis mismatch: found `]` at ({row},{col}) but the corresponding `[` was never opened")
                return None

        # this is just some logic to figure out the position in the file...
        if c == '\n':
            row += 1
            col = 1
        else:
            col += 1

    # for a well formed program, all the parenthesis should be closed
    if len(bb_stack) > 0:
        print(f"[ERROR] there are still {len(bb_stack)} parenthesis to be closed")
        return None

    # at the end of the program we insert a return instruction
    # so that every basic block is well formed
    curr.append(ir.Return())

    # we simply enumerate the basic blocks in the order
    # they appear in the program. This is just for debugging
    # purposes.
    for i, bb in enumerate(basic_blocks):
        bb.label = i

    return basic_blocks
