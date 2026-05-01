from brainf import ir
from brainf.codegen import cpu, transpiler

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

    def run(self, stdin=None) -> int:
        """
        Runs the program and collect the return code and the stdout
        For now only the return code since redirecting stdout is a problem

        It is assumed that a properly constructed derived class of `Runtime`
        has the `lib.run` attibute which is a callable
        """
        return self.lib.run(self.mem)

    def reset(self):
        """
        Clears the memory tape
        """
        # maybe ctypes.memset??
        raise NotImplemented


def compile_shared_object(so_name: str, src: str, filetype: str, opt: str = ''):
    """
    Compiles the C or ASM file with gcc in a shared object.
    This makes it much easier to load the binary with `ctypes.CDLL(...)`

    The implementation could have used a temporary file, but I decided to
    pass the file directly to gcc from stdin. This requires to specify the
    file type:
      * C files   -> c
      * ASM files -> assembler
    """
    compile_command = [
        'gcc',
        '-fPIC', '-shared',
        '-o', so_name,
        '-x', filetype, '-', # this line tells gcc we are passing a `filetype` file to stdin
        opt
    ]

    res = subprocess.run(
        compile_command,
        input=src.encode(),
        capture_output=True,
        check=True,
    )


class CRuntime(Runtime):
    def __init__(self, program: ir.Program, cell_size: int = 30000, opt_level: str = '-O0'):
        super().__init__(program, cell_size)

        # I know there is a little repetition...
        c_src = transpiler.generate_c(program)
        with tempfile.NamedTemporaryFile() as tmp:
            compile_shared_object(tmp.name, c_src, filetype='c', opt=opt_level)

            self.lib = ctypes.CDLL(tmp.name)


class NativeRuntime(Runtime):
    def __init__(self, program: ir.Program, cell_size: int):
        super().__init__(program, cell_size)

        match os.uname().machine:
            case 'x86_64':
                asm_src = cpu.generate_x86(program)
            case 'armv6l':
                asm_src = cpu.generate_armv6l(program)
            case _:
                raise NotImplemented

        with tempfile.NamedTemporaryFile() as tmp:
            compile_shared_object(tmp.name, asm_src, filetype='assembler')

            self.lib = ctypes.CDLL(tmp.name)
