#!/usr/bin/env python3

"""
This file defines the instructions in the intermediate representation (IR).
I use an object oriented approach because each instruction type have its
particular fields.

The branching instructions point to BasicBlock objects, which are defined
as the nodes of a control flow graph.
"""


class Instruction:
    def __init__(self):
        pass

    def get_token(self) -> str:
        pass


class BasicBlock:
    # default mutable arguments are a source of bugs!!
    def __init__(self, label: int = None, instructions: list[Instruction] = None):
        self.label = label

        if instructions is None:
            self.instructions = []
        else:
            self.instructions = instructions

    def append(self, instr: Instruction):
        self.instructions.append(instr)

    def get_terminator(self) -> Instruction:
        return self.instructions[-1]

    def is_well_formed(self) -> bool:
        return type(self.get_terminator()) in [BranchIfZero, BranchIfNotZero, Return]

    def __repr__(self) -> str:
        return f'BasicBlock({self.label}, {self.instructions})'


class Increment(Instruction):
    def __init__(self, imm: int = 1):
        self.imm = imm

    def get_token(self) -> str:
        return '+' * self.imm

    def __repr__(self) -> str:
        return f'Increment({self.imm})'


class Decrement(Instruction):
    def __init__(self, imm: int = 1):
        self.imm = imm

    def get_token(self) -> str:
        return '-' * self.imm

    def __repr__(self) -> str:
        return f'Decrement({self.imm})'


class MoveLeft(Instruction):
    def __init__(self, imm: int = 1):
        self.imm = imm

    def get_token(self) -> str:
        return '<' * self.imm

    def __repr__(self) -> str:
        return f'MoveLeft({self.imm})'

class MoveRight(Instruction):
    def __init__(self, imm: int = 1):
        self.imm = imm

    def get_token(self) -> str:
        return '>' * self.imm

    def __repr__(self) -> str:
        return f'MoveRight({self.imm})'


class GetChar(Instruction):
    def __init__(self):
        pass

    def get_token(self) -> str:
        return ','

    def __repr__(self) -> str:
        return 'GetChar()'


class PutChar(Instruction):
    def __init__(self):
        pass

    def get_token(self) -> str:
        return '.'

    def __repr__(self) -> str:
        return 'PutChar()'


class BranchIfZero(Instruction):
    def __init__(self, target_block: BasicBlock, fallthrough_block: BasicBlock, debug_info = None):
        self.target_block = target_block
        self.fallthrough_block = fallthrough_block
        self.debug_info = debug_info

    def get_token(self) -> str:
        return '['

    def __repr__(self) -> str:
        return f'BranchIfZero(target_block={self.target_block.label}, fallthrough_block={self.fallthrough_block.label})'


class BranchIfNotZero(Instruction):
    def __init__(self, target_block: BasicBlock, fallthrough_block: BasicBlock, debug_info = None):
        self.target_block = target_block
        self.fallthrough_block = fallthrough_block
        self.debug_info = debug_info

    def get_token(self) -> str:
        return ']'

    def __repr__(self) -> str:
        return f'BranchIfNotZero(target_block={self.target_block.label}, fallthrough_block={self.fallthrough_block.label})'

"""
This instruction encodes the end of the program
it is useful for keeping the basic block interface, since
I expect every BB to end with a terminator instruction

I also plan on using this instruction for the runtimes
"""
class Return(Instruction):
    def __init__(self):
        pass

    def get_token(self) -> str:
        return ''

    def __repr__(self) -> str:
        return 'Return()'
