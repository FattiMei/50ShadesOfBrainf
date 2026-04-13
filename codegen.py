#!/usr/bin/env python3


import ir


"""
This function generates the unformatted source code from the IR
"""
def generate_original_src(program: ir.Program) -> str:
    res = ''
    end = False
    curr = program.get_entry_point()

    while not end:
        for instr in curr.instructions:
            res += instr.get_token()

        terminator = curr.get_terminator()
        if type(terminator) == ir.Return:
            end = True
        else:
            curr = terminator.fallthrough_block

    return res
