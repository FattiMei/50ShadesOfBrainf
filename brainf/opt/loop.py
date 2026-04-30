from brainf import ir


def annotate_infinite_loops_pass(program: ir.Program) -> bool:
    """
    This function detects the `[]` loops which are infinite loops
    since their body is empty so the branch condition doesn't ever change.
    We signal this condition by the Return IR node with nonzero return code.

    Note that this transformation alters the control flow in a way that
    makes the old codegen fail
    """
    success = False

    for basic_block in program.basic_blocks:
        if basic_block in basic_block.get_successors() and len(basic_block.instructions) == 1:
            # we need to remove the block from all its successors
            for successor in basic_block.get_successors():
                successor.get_predecessors().remove(basic_block)

            basic_block.instructions.clear()
            basic_block.instructions.append(ir.Return(1))
            success = True

    return success
