#!/usr/bin/env python3

"""
This file defines the instructions in the intermediate representation (IR).
I use an object oriented approach because each instruction type have its
particular fields.

The branching instructions point to BasicBlock objects, which are defined
as the nodes of a control flow graph.
"""


from enum import Enum
from typing import Iterator
from functools import reduce


ALL_TRUE = lambda xs: reduce(lambda x,y: x and y, xs, True)


class Instruction:
    def __init__(self):
        pass


class IrFlags(Enum):
    ORIGINAL_INSTRUCTIONS = 0
    FUSED_INSTRUCTIONS = 1


class BasicBlock:
    # default mutable arguments are a source of bugs                         v
    def __init__(self, label: int = None, instructions: list[Instruction] = None):
        self.label = label
        self.predecessors = []

        if instructions is None:
            self.instructions = []
        else:
            self.instructions = instructions

    def append(self, instr: Instruction):
        """
        Appends an instruction to the end of the block, it's not
        guaranteed to leave the block into a valid state.
        """
        self.instructions.append(instr)

    def get_terminator(self) -> Instruction:
        """
        Assuming the block is in a valid state, the last
        instruction is the terminator
        """
        return self.instructions[-1]

    def get_successors(self) -> list["BasicBlock"]:
        terminator = self.get_terminator()

        if type(terminator) == Return:
            return []

        return [terminator.fallthrough_block, terminator.target_block]

    def get_predecessors(self) -> list["BasicBlock"]:
        return self.predecessors

    def deepcopy(self) -> "BasicBlock":
        return BasicBlock(
            label=self.label,
            instructions=self.instructions.copy()
        )

    def is_well_formed(self) -> bool:
        BRANCH_INSTRUCTIONS = [BranchIfZero, BranchIfNotZero, Return]

        is_terminator_branch = type(self.get_terminator()) in BRANCH_INSTRUCTIONS
        are_other_non_branch = ALL_TRUE(
            map(
                lambda instr: type(instr) not in BRANCH_INSTRUCTIONS,
                self.instructions[:-1]
            )
        )

        return is_terminator_branch and are_other_non_branch

    def is_inner_loop(self) -> bool:
        return self in self.get_successors()

    def __repr__(self) -> str:
        return f'BasicBlock({self.label}, {self.instructions})'


class Program:
    """
    This class is the container of basic blocks. It's the output of
    the parsing function and stores all basic blocks plus the entry point

    It will be the input of the optimization passes and the code generation.
    It will store important flags about the ir used in its blocks:
      * contains fused operators?
      * are only original instructions?
      * ...
    """
    def __init__(self, basic_blocks: list[BasicBlock]):
        self.basic_blocks = basic_blocks
        self._make_child_parent_connection()

    def get_entry_point(self) -> BasicBlock:
        """
        Assuming the entry point is always the first block
        """
        return self.basic_blocks[0]

    def navigate_blocks(self) -> Iterator[BasicBlock]:
        """
        Iterator of basic blocks along program order.
        Program order means the loops are always inspected before
        what comes after the loop
        """
        curr = self.get_entry_point()
        end = False

        while not end:
            yield curr

            terminator = curr.get_terminator()
            if type(terminator) == Return:
                if terminator.returncode == 0:
                    end = True
                else:
                    curr = curr.get_predecessors()[0].get_terminator().target_block
            else:
                curr = terminator.fallthrough_block

    def _make_child_parent_connection(self):
        """
        Add to each basic block the predecessor objects
        """
        for basic_block in self.basic_blocks:
            basic_block.predecessors.clear()

        # we don't have repetitions because each parent is visited once
        for parent in self.basic_blocks:
            for child in parent.get_successors():
                child.predecessors.append(parent)

    def deepcopy(self) -> "Program":
        # only copying the basic blocks without updating
        # the connections is wrong. Thankfully this bug is
        # detected by `are_bb_reachable`
        #   return Program(basic_blocks=[bb.deepcopy() for bb in self.basic_blocks])

        # I think using labels as indices for later bookkeeping
        # of the data structures is a pattern in compiler design
        cloned_bb = {
            bb.label: bb.deepcopy()
            for bb in self.basic_blocks
        }

        # fixing the edges
        for bb in cloned_bb.values():
            terminator = bb.get_terminator()

            if type(terminator) in [BranchIfZero, BranchIfNotZero]:
                terminator.target_block = cloned_bb[terminator.target_block.label]
                terminator.fallthrough_block = cloned_bb[terminator.fallthrough_block.label]

        return Program(list(cloned_bb.values()))


    def are_bb_well_formed(self) -> bool:
        return ALL_TRUE(bb.is_well_formed() for bb in self.basic_blocks)

    def are_bb_reachable(self) -> bool:
        # simple graph reachability implementation
        explored = set()
        queue = [self.get_entry_point()]

        while len(queue) > 0:
            curr = queue.pop()

            if curr not in explored:
                explored.add(curr)

                for succ in curr.get_successors():
                    if succ not in explored:
                        queue.append(succ)

        return explored == set(self.basic_blocks)

    def __repr__(self) -> str:
        return f'{self.basic_blocks}'


class Increment(Instruction):
    def __init__(self, imm: int = 1):
        self.imm = imm

    def get_token(self) -> str:
        return '+' * self.imm

    def get_signed_imm(self) -> int:
        return self.imm

    def __repr__(self) -> str:
        return f'Increment({self.imm})'


class Decrement(Instruction):
    def __init__(self, imm: int = 1):
        self.imm = imm

    def get_token(self) -> str:
        return '-' * self.imm

    def get_signed_imm(self) -> int:
        return -self.imm

    def __repr__(self) -> str:
        return f'Decrement({self.imm})'


class MoveLeft(Instruction):
    def __init__(self, imm: int = 1):
        self.imm = imm

    def get_token(self) -> str:
        return '<' * self.imm

    def get_signed_imm(self) -> int:
        return -self.imm

    def __repr__(self) -> str:
        return f'MoveLeft({self.imm})'


class MoveRight(Instruction):
    def __init__(self, imm: int = 1):
        self.imm = imm

    def get_token(self) -> str:
        return '>' * self.imm

    def get_signed_imm(self) -> int:
        return self.imm

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
    def __init__(self, target_block: BasicBlock, fallthrough_block: BasicBlock, source_pos = None):
        self.target_block = target_block
        self.fallthrough_block = fallthrough_block
        self.source_pos = source_pos

    def get_token(self) -> str:
        return '['

    def __repr__(self) -> str:
        return f'BranchIfZero(target_block={self.target_block.label}, fallthrough_block={self.fallthrough_block.label})'


class BranchIfNotZero(Instruction):
    def __init__(self, target_block: BasicBlock, fallthrough_block: BasicBlock, source_pos = None):
        self.target_block = target_block
        self.fallthrough_block = fallthrough_block
        self.source_pos = source_pos

    def get_token(self) -> str:
        return ']'

    def __repr__(self) -> str:
        return f'BranchIfNotZero(target_block={self.target_block.label}, fallthrough_block={self.fallthrough_block.label})'


class Return(Instruction):
    """
    This instruction encodes the end of the program
    it is useful for keeping the basic block interface, since
    I expect every BB to end with a terminator instruction

    I also plan on using this instruction for the runtimes
    """
    def __init__(self, returncode: int = 0):
        """
        Any nonzero return value indicate an infinite loop
        """
        self.returncode = returncode

    def get_token(self) -> str:
        return ''

    def __repr__(self) -> str:
        return f'Return({self.returncode})'
