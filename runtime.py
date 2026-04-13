#!/usr/bin/env python3


import ir

# I include the numpy dependency for faster array access
# I'm not particularly happy about that, but I need to make
# the IrRuntime faster
import numpy as np
from enum import Enum
from math import inf
from time import perf_counter
from dataclasses import dataclass


class MemoryTape:
    def __init__(self, ncells: int, cell_dtype: np.dtype):
        self.mem = [0] * ncells
        self.mem = np.zeros(ncells, dtype=cell_dtype)
        self.cell_dtype = cell_dtype
        self.max_ptr = -inf
        self.total_reads = 0
        self.total_writes = 0

    def read(self, ptr: int) -> int:
        self.max_ptr = max(self.max_ptr, ptr)
        self.total_reads += 1

        return self.mem[ptr]

    def write(self, ptr: int, value: int):
        self.max_ptr = max(self.max_ptr, ptr)
        self.total_writes += 1

        self.mem[ptr] = value

    def clear(self):
        for i in range(len(self.mem)):
            self.mem[i] = 0


@dataclass
class RuntimeStatus:
    memory_tape: MemoryTape
    ptr: int
    stdout: str
    ok: bool
    execution_time: float
    total_instructions_executed: int
    total_branches_evaluated: int


"""
This class operates directly on the IR. Uses the entry point
of the program and then follows the control flow to select
the next basic block to run.

This implementation is very slow, too much for my taste
"""
class IrRuntime:
    def __init__(self,
                 ncells: int,
                 cell_dtype: np.dtype = np.uint8):
        self.mem = MemoryTape(ncells, cell_dtype)

    # I'm aware that there could be repetition in the runtime codes
    # in this case I think that "a little repetition is better than
    # a little dependency"
    def run(self, program: ir.Program, stdin='') -> RuntimeStatus:
        # all those variables will then be aggregated into
        # the RuntimeStatus class
        ptr = 0
        stdout = ''
        status = True
        total_instructions_executed = 0
        total_branches_evaluated = 0

        curr = program.get_entry_point()

        # begin program execution
        start_time = perf_counter()
        while True:
            for instr in curr.instructions[:-1]:
                if type(instr) == ir.Increment:
                    self.mem.write(ptr, self.mem.read(ptr) + instr.imm)
                elif type(instr) == ir.Decrement:
                    self.mem.write(ptr, self.mem.read(ptr) - instr.imm)
                elif type(instr) == ir.MoveLeft:
                    ptr += instr.imm
                elif type(instr) == ir.MoveRight:
                    ptr -= instr.imm
                elif type(instr) == ir.GetChar:
                    self.mem.write(ptr, next(stdin))
                elif type(instr) == ir.PutChar:
                    c = chr(self.mem.read(ptr))
                    stdout += c

                total_instructions_executed += 1

            terminator = curr.get_terminator()
            if type(terminator) == ir.Return:
                break
            else:
                cond = self.mem.read(ptr)

                if type(terminator) == ir.BranchIfZero:
                    curr = terminator.target_block if cond == 0 else terminator.fallthrough_block
                elif type(terminator) == ir.BranchIfNotZero:
                    curr = terminator.target_block if cond != 0 else terminator.fallthrough_block

                total_branches_evaluated += 1

        end_time = perf_counter()

        return RuntimeStatus(
            memory_tape=self.mem,
            ptr=ptr,
            stdout=stdout,
            ok=True,
            execution_time=end_time-start_time,
            total_instructions_executed=total_instructions_executed,
            total_branches_evaluated=total_branches_evaluated
        )
