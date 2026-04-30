from brainf import ir


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
    end = False
    curr = program.get_entry_point()

    head = head_register
    val = val_register
    assert(head != val)

    lines += ['\t.data']
    lines += ['\t.globl run']
    lines += ['\t.text']
    lines += ['run:']

    # %rdi should be the first argument in the call
    # of run(char*)
    lines += [f'mov %rdi, {head}']

    # the iteration on the basic blocks in program order
    # should be abstracted away
    while not end:
        lines += [f'.L{curr.label}:']

        for instr in curr.instructions:
            if type(instr) == ir.Increment:
                lines += [f'mov ({head}), {val}']
                lines += [f'add ${instr.imm}, {val}']
                lines += [f'mov {val}, ({head})']

            elif type(instr) == ir.Decrement:
                lines += [f'mov ({head}), {val}']
                lines += [f'sub ${instr.imm}, {val}']
                lines += [f'mov {val}, ({head})']

            elif type(instr) == ir.MoveLeft:
                lines += [f'sub ${instr.imm}, {head}']

            elif type(instr) == ir.MoveRight:
                lines += [f'add ${instr.imm}, {head}']

            elif type(instr) == ir.GetChar:
                # it should be a syscall to getchar()
                assert(False)

            elif type(instr) == ir.PutChar:
                lines += [f'push {head}']
                lines += [f'mov ({head}), %rdi']
                lines += ['call putchar']
                lines += [f'pop {head}']

            elif type(instr) == ir.BranchIfZero:
                target_block = instr.target_block

                lines += [f'mov ({head}), {val}']
                lines += [f'cmp $0, {val}']
                lines += [f'jz .L{target_block.label}']

                curr = instr.fallthrough_block

            elif type(instr) == ir.BranchIfNotZero:
                target_block = instr.target_block

                lines += [f'mov ({head}), {val}']
                lines += [f'cmp $0, {val}']
                lines += [f'jnz .L{target_block.label}']

                curr = instr.fallthrough_block

            elif type(instr) == ir.Return:
                lines += ['mov %rax, ${instr.returncode}']
                lines += ['ret']

                if instr.returncode == 0:
                    end = True
                else:
                    curr = curr.get_predecessors()[0].get_terminator().target_block

    lines += ['']

    return '\n'.join(lines)


def generate_armv6l(program: ir.Program) -> str:
    """
    For the arm backend the problem of storing only a single byte
    doesn't exist as there is a `strb` instruction
    """
    lines = []
    end = False
    curr = program.get_entry_point()

    head = 'r0'
    val  = 'r1'

    lines += ['\t.globl run']
    lines += ['\t.text']
    lines += ['run:']
    lines += ['push {fp, lr}']

    while not end:
        lines += [f'.L{curr.label}:']

        for instr in curr.instructions:
            if type(instr) == ir.Increment:
                lines += [f'ldr {val}, [{head}]']
                lines += [f'add {val}, #{instr.imm}']
                lines += [f'strb {val}, [{head}]']

            elif type(instr) == ir.Decrement:
                lines += [f'ldr {val}, [{head}]']
                lines += [f'sub {val}, #{instr.imm}']
                lines += [f'strb {val}, [{head}]']

            elif type(instr) == ir.MoveLeft:
                lines += [f'sub {head}, #{instr.imm}']

            elif type(instr) == ir.MoveRight:
                lines += [f'add {head}, #{instr.imm}']

            elif type(instr) == ir.GetChar:
                # it should be a syscall to getchar()
                assert(False)

            elif type(instr) == ir.PutChar:
                lines += [f'push {{ {head} }}']
                lines += [f'ldr r0, [{head}]']
                lines += [f'bl putchar']
                lines += [f'pop {{ {head} }}']

            elif type(instr) == ir.BranchIfZero:
                target_block = instr.target_block

                lines += [f'ldr {val}, [{head}]']
                lines += [f'and {val}, #255']
                lines += [f'cmp {val}, #0']
                lines += [f'beq .L{target_block.label}']

                curr = instr.fallthrough_block

            elif type(instr) == ir.BranchIfNotZero:
                target_block = instr.target_block

                lines += [f'ldr {val}, [{head}]']
                lines += [f'and {val}, #255']
                lines += [f'cmp {val}, #0']
                lines += [f'bne .L{target_block.label}']

                curr = instr.fallthrough_block

            elif type(instr) == ir.Return:
                lines += [f'mov r0, #{instr.returncode}']
                lines += ['pop {fp, pc}']

                if instr.returncode == 0:
                    end = True
                else:
                    curr = curr.get_predecessors()[0].get_terminator().target_block

    lines += ['']

    return '\n'.join(lines)
