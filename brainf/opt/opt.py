#!/usr/bin/env python3

"""
This file contains a series of optimization passes on the program IR
Some of the passes don't touch the CFG but operate only inside the BB,
other passes may affect the CFG
"""


from brainf import ir
import itertools


def instruction_fuse(basic_block: ir.BasicBlock):
    # I use a function instead of manually filling a dictionary
    # because a dictionary implementation would have to insert
    # new keys every time a new instruction type is defined
    #
    # With this function, we have the default path
    def fuse_map(instr: ir.Instruction):
        instr_type = type(instr)

        if instr_type in [ir.Increment, ir.Decrement]:
            return ir.Increment
        elif instr_type in [ir.MoveLeft, ir.MoveRight]:
            return ir.MoveRight

        return instr_type

    worklist = []

    groups = itertools.groupby(basic_block.instructions, key=fuse_map)
    for key, group in groups:
        # there is repetition in this logic, I wonder if I can do better...
        # for now I'll leave it like that
        if key == ir.Increment:
            # this sum doesn't take into accounts the signs!!!
            # the result is obviously wrong and it generates only ir.Increment
            # or ir.MoveRight instructions
            imm = sum(map(lambda instr: instr.get_signed_imm(), group))
            if imm > 0:
                worklist.append(ir.Increment(imm))
            elif imm < 0:
                worklist.append(ir.Decrement(-imm))
        elif key == ir.MoveRight:
            imm = sum(map(lambda instr: instr.get_signed_imm(), group))
            if imm > 0:
                worklist.append(ir.MoveRight(imm))
            elif imm < 0:
                worklist.append(ir.MoveLeft(-imm))
        else:
            for instr in group:
                worklist.append(instr)

    basic_block.instructions.clear()
    for instr in worklist:
        basic_block.instructions.append(instr)


def instruction_fusion_pass(program: ir.Program):
    """
    This function applies a non CFG-altering transformation
    on all basic blocks of a program. It is responsible of
    fusing sequences like `++++` into a compact representation,
    for example:
        ++++ -> ir.Increment(4)
        <<<  -> ir.MoveLeft(3)

    Another possible fusion occasion is on sequences like `+++-`
    or `<<<>><' by which pairs of consecutive +- can be elided.
    Programs in the samples/ directory don't show this inefficiency
    """
    for basic_block in program.basic_blocks:
        instruction_fuse(basic_block)
