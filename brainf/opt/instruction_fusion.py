from brainf import ir
import itertools


def instruction_fuse(basic_block: ir.BasicBlock) -> bool:
    """
    Perform instruction fusion on a (mutable) basic block.
    Returns if the fusion was made
    """
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
    has_fused = False

    groups = itertools.groupby(basic_block.instructions, key=fuse_map)
    for key, group in groups:
        # there is repetition in this logic, I wonder if I can do better...
        # for now I'll leave it like that
        if key == ir.Increment:
            has_fused = True
            # this sum doesn't take into accounts the signs!!!
            # the result is obviously wrong and it generates only ir.Increment
            # or ir.MoveRight instructions
            imm = sum(map(lambda instr: instr.get_signed_imm(), group))
            if imm > 0:
                worklist.append(ir.Increment(imm))
            elif imm < 0:
                worklist.append(ir.Decrement(-imm))
        elif key == ir.MoveRight:
            has_fused = True

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

    return has_fused


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
    has_fused = False

    for basic_block in program.basic_blocks:
        has_fused |= instruction_fuse(basic_block)

    if has_fused:
        program.ir_flags.add(ir.IrFlags.FUSED_INSTRUCTIONS)
        program.ir_flags.remove(ir.IrFlags.ORIGINAL_INSTRUCTIONS)
