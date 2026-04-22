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
    """
    Generates the C code that implements the program as a function
    with signature `void run(char* memory)`.

    Internally calls getchar() and putchar()
    """
    lines = []
    indent = 0

    def push_line(l: str, indent: int):
        lines.append('\t' * indent + l)

    push_line('void run(char* memory) {', indent)
    indent = 1

    end = False
    curr = program.get_entry_point()

    while not end:
        for instr in curr.instructions[:-1]:
            match type(instr):
                case ir.Increment:
                    push_line(f'*memory += {instr.imm};', indent)
                case ir.Decrement:
                    push_line(f'*memory -= {instr.imm};', indent)
                case ir.MoveLeft:
                    push_line(f'memory -= {instr.imm};', indent)
                case ir.MoveRight:
                    push_line(f'memory += {instr.imm};', indent)
                case ir.GetChar:
                    push_line('*memory = getchar();', indent)
                case ir.PutChar:
                    push_line('putchar(*memory);', indent)
                case _:
                    assert(False)

        terminator = curr.get_terminator()
        match type(terminator):
            case ir.BranchIfZero:
                push_line('while (*memory) {', indent)
                indent += 1
                curr = terminator.fallthrough_block
            case ir.BranchIfNotZero:
                indent -= 1
                push_line('}', indent)
                curr = terminator.fallthrough_block
            case ir.Return:
                end = True
            case _:
                assert(False)

    push_line('}', indent=0)

    return '\n'.join(lines)
