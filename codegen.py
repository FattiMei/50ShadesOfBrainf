#!/usr/bin/env python3


import ir
from enum import Enum


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


"""
This function generates the x86 assembly code for the function run(char *) that
implements `program`

We don't have the concept of registers in the IR, so all the decisions are hardcoded here.
  * where to store the pointer to the memory tape
  * where to store the cell value for local processing before storing it

I'm still uncertain about using %rbx as the source value in a store instruction. The memory
tape is made of bytes, so the instruction `mov %rbx, (%rax)` may overwrite the adjacent
memory cells. This must be tested
"""
def generate_x86(program: ir.Program, head_register: str = '%rax', val_register: str = '%rbx') -> str:
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

                # with this trick, I avoid using special register
                # names to address only the LSB
                lines += [f'and $255, {val}']
                lines += [f'cmp $0, {val}']
                lines += [f'jz .L{target_block.label}']

                curr = instr.fallthrough_block

            elif type(instr) == ir.BranchIfNotZero:
                target_block = instr.target_block

                lines += [f'mov ({head}), {val}']
                lines += [f'and $255, {val}']
                lines += [f'cmp $0, {val}']
                lines += [f'jnz .L{target_block.label}']

                curr = instr.fallthrough_block

            elif type(instr) == ir.Return:
                lines += ['ret']
                end = True

    lines += ['']

    return '\n'.join(lines)


"""
For the arm backend the problem of storing only a single byte
doesn't exist as there is a `strb` instruction
"""
def generate_armv6l(program: ir.Program) -> str:
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
                lines += ['pop {fp, pc}']
                end = True

    lines += ['']

    return '\n'.join(lines)


class FixedSizeInstruction:
    class Type(Enum):
        INCREMENT = 0
        DECREMENT = 1
        MOVELEFT  = 2
        MOVERIGHT = 3
        GETC      = 4
        PUTC      = 5
        BZ        = 6
        BNZ       = 7

    # in the case of branching instructions, the operand
    # should be the absolute address of the target
    #
    # I imagine that in a future one may want relative
    # addressing, how should I implement this?
    def __init__(self, instruction_type: Type, operand: int):
        self.instruction_type = instruction_type
        self.operand = operand


def generate_fixed_size_instructions(program: ir.Program) -> list[FixedSizeInstruction]:
    result = []

    return result
