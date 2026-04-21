from brainf import ir


def generate_original_src(program: ir.Program) -> str:
    """
    This function generates the unformatted source code from the IR
    """
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


def generate_c(program: ir.Program) -> str:
    pass
