from brainf import ir
from brainf.codegen.utils import push_line_functor
from functools import partial



def generate_original_src(program: ir.Program) -> str:
    """
    This function generates the unformatted source code from the IR
    """
    res = ''
    for block in program.navigate_blocks():
        for instr in block.instructions:
            res += instr.get_token()

        terminator = block.get_terminator()
        if type(terminator) == ir.Return and terminator.returncode != 0:
            res += ']'

    return res


def generate_c(program: ir.Program) -> str:
    """
    Generates the C code that implements the program as a function
    with signature `int run(char* memory)`.

    Internally calls getchar() and putchar()
    """
    lines = []
    push_line = partial(push_line_functor, acc=lines)

    indent = 0
    push_line('int run(char* memory) {', indent)
    indent = 1

    for block in program.navigate_blocks():
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

        terminator = block.get_terminator()
        match type(terminator):
            case ir.BranchIfZero:
                push_line('while (*memory) {', indent)
                indent += 1
            case ir.BranchIfNotZero:
                indent -= 1
                push_line('}', indent)
            case ir.Return:
                if terminator.returncode != 0:
                    push_line('return 1;', indent)
                    indent -= 1
                    push_line('}', indent)
            case _:
                assert(False)

    push_line('return 0;', indent)
    push_line('}', indent=0)

    return '\n'.join(lines)
