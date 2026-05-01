from brainf import ir
from brainf.codegen.transpiler import generate_c

import os
import ctypes
import tempfile
import subprocess


class Runtime:
    def __init__(self, program: ir.Program, cell_size: int):
        """
        This function is responsible of allocating the tape memory for a run
        of a brainf program

        It is left to the concrete implementation how to take the program and
        make it executable
        """
        assert(10000 < cell_size < 1000000)
        self.mem = ctypes.c_buffer(init=0, size=cell_size)
        self.cell_size = cell_size

    def run(self, stdin=None) -> tuple[int, str]:
        """
        Runs the program and collect the return code and the stdout
        """
        raise NotImplemented

    def reset(self):
        """
        Clears the memory tape
        """
        pass


class CRuntime(Runtime):
    def __init__(self, program: ir.Program, cell_size: int, opt_level: str):
        super().__init__(program, cell_size)

        c_src = generate_c(program)


class NativeRuntime(Runtime):
    def __init__(self, program: ir.Program, cell_size: int):
        super().__init__(program, cell_size)

        match os.uname().machine:
            case 'x86_64':
                assembly = codegen.cpu.generate_x86(program)
            case 'armv6l':
                assembly = codegen.cpu.generate_armv6l(program)
            case _:
                raise NotImplemented

        # compila l'assembly in un eseguibile con gcc
        # magari per semplicità faremo la dll?
