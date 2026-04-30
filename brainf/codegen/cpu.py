from brainf import ir
from brainf.codegen.utils import push_line_functor
from functools import partial


# I could use an ir similar to the one used in the professor compiler
# an then use an object to lower the IR into the specific target
#
# The codegen process is not sophisticated at all, but there may be
# a possibility for a final optimization at this level. I want
# to remove a load from memory when computing the branch condition
# in the case the predecessors of branches


def generate_x86(program: ir.Program, head_register: str = '%rax', val_register: str = '%bl') -> str:
    """
    This function generates the x86 assembly code for the function run(char *) that
    implements `program`

    We don't have the concept of registers in the IR, so all the decisions are hardcoded here.
    * where to store the pointer to the memory tape
    * where to store the cell value for local processing before storing it

    It's important that `val_register` is an 8-bit register, otherwise the store operations like
        mov %rbx, [%rax]

    will write 8 bytes and so will overwrite adjacent cells. The "samples/sierpinski.b" program
    suffers from this phenomenon
    """
    lines = []
    indent = 1
    push_line = partial(push_line_functor, acc=lines)

    head = head_register
    val = val_register
    assert(head != val)

    push_line('.data', indent)
    push_line('.globl run', indent)
    push_line('.text', indent)

    push_line('run:', 0)

    # %rdi should be the first argument in the call
    # of run(char*)
    indent = 1
    push_line(f'mov %rdi, {head}', indent)

    # the iteration on the basic blocks in program order
    # should be abstracted away
    for block in program.navigate_blocks():
        push_line(f'.L{block.label}:', indent=0)

        for instr in block.instructions:
            if type(instr) == ir.Increment:
                push_line(f'mov ({head}), {val}', indent)
                push_line(f'add ${instr.imm}, {val}', indent)
                push_line(f'mov {val}, ({head})', indent)

            elif type(instr) == ir.Decrement:
                push_line(f'mov ({head}), {val}', indent)
                push_line(f'sub ${instr.imm}, {val}', indent)
                push_line(f'mov {val}, ({head})', indent)

            elif type(instr) == ir.MoveLeft:
                push_line(f'sub ${instr.imm}, {head}', indent)

            elif type(instr) == ir.MoveRight:
                push_line(f'add ${instr.imm}, {head}', indent)

            elif type(instr) == ir.GetChar:
                # it should be a syscall to getchar()
                assert(False)

            elif type(instr) == ir.PutChar:
                push_line(f'push {head}', indent)
                push_line(f'mov ({head}), %rdi', indent)
                push_line('call putchar', indent)
                push_line(f'pop {head}', indent)

            elif type(instr) == ir.BranchIfZero:
                target_block = instr.target_block

                push_line(f'mov ({head}), {val}', indent)
                push_line(f'cmp $0, {val}', indent)
                push_line(f'jz .L{target_block.label}', indent)

            elif type(instr) == ir.BranchIfNotZero:
                target_block = instr.target_block

                push_line(f'mov ({head}), {val}', indent)
                push_line(f'cmp $0, {val}', indent)
                push_line(f'jnz .L{target_block.label}', indent)

            elif type(instr) == ir.Return:
                push_line(f'mov ${instr.returncode}, %rax', indent)
                push_line('ret', indent)

    lines += ['']

    return '\n'.join(lines)


def generate_armv6l(program: ir.Program) -> str:
    """
    For the arm backend the problem of storing only a single byte
    doesn't exist as there is a `strb` instruction
    """
    lines = []
    indent = 1

    head = 'r0'
    val  = 'r1'

    push_line = partial(push_line_functor, acc=lines)
    push_line('\t.globl run', indent)
    push_line('\t.text', indent)
    push_line('run:', 0)

    indent = 1
    push_line('push {fp, lr}', indent)

    for block in program.navigate_blocks():
        push_line(f'.L{block.label}:', indent)

        for instr in block.instructions:
            if type(instr) == ir.Increment:
                push_line(f'ldr {val}, [{head}]', indent)
                push_line(f'add {val}, #{instr.imm}', indent)
                push_line(f'strb {val}, [{head}]', indent)

            elif type(instr) == ir.Decrement:
                push_line(f'ldr {val}, [{head}]', indent)
                push_line(f'sub {val}, #{instr.imm}', indent)
                push_line(f'strb {val}, [{head}]', indent)

            elif type(instr) == ir.MoveLeft:
                push_line(f'sub {head}, #{instr.imm}', indent)

            elif type(instr) == ir.MoveRight:
                push_line(f'add {head}, #{instr.imm}', indent)

            elif type(instr) == ir.GetChar:
                # it should be a syscall to getchar()
                assert(False)

            elif type(instr) == ir.PutChar:
                push_line(f'push {{ {head} }}', indent)
                push_line(f'ldr r0, [{head}]', indent)
                push_line(f'bl putchar', indent)
                push_line(f'pop {{ {head} }}', indent)

            elif type(instr) == ir.BranchIfZero:
                target_block = instr.target_block

                push_line(f'ldr {val}, [{head}]', indent)
                push_line(f'and {val}, #255', indent)
                push_line(f'cmp {val}, #0', indent)
                push_line(f'beq .L{target_block.label}', indent)

            elif type(instr) == ir.BranchIfNotZero:
                target_block = instr.target_block

                push_line(f'ldr {val}, [{head}]', indent)
                push_line(f'and {val}, #255', indent)
                push_line(f'cmp {val}, #0', indent)
                push_line(f'bne .L{target_block.label}', indent)

            elif type(instr) == ir.Return:
                push_line(f'mov r0, #{instr.returncode}', indent)
                push_line('pop {fp, pc}', indent)

    lines += ['']

    return '\n'.join(lines)
