#!/usr/bin/env python3

"""
This file acts as the compiler driver, it loads the source code
and calls the compiler functions for parsing, optimization and
code generation for multiple targets
"""


from brainf import ir, parser
from brainf.opt.instruction_fusion import instruction_fusion_pass

from brainf.codegen.cpu import generate_x86, generate_armv6l
from brainf.codegen.transpiler import generate_original_src

import os
import argparse
import tempfile
import subprocess


def parse_cmd_line_args():
    parser = argparse.ArgumentParser(prog="bfcom")
    parser.add_argument("input_file", type=str, help="which file to compile")
    parser.add_argument('-o', type=str, default='out', help='the final executable name')
    parser.add_argument('--output-asm', action='store_true')

    # this option is strange: normally I use the compiler to compile runtime.c
    # and assemble my generated assembly. The optimization flag seems to be very
    # important as -O2 builds are significantly faster (twice as fast for mandelbrot).
    # Asking Gemini, GCC seems to skip optimizations on the assembly file...
    parser.add_argument('--compiler-opt-level', type=str, default='O2')

    # later I will select which specific optimizations to enable
    parser.add_argument('--opt', action='store_true', help='enables optimizations')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_cmd_line_args()

    with open(args.input_file, 'r') as file:
        src = file.read()

    program = parser.parse_source(src)

    if args.opt:
        print("Performing instruction fusion...")
        instruction_fusion_pass(program)

    machine = os.uname().machine
    if machine == 'x86_64':
        assembly = generate_x86(program)
    elif machine in ['armv6l']:
        assembly = generate_armv6l(program)
    else:
        print(f'`{machine}` is unsupported')
        print("Compilation interrupted at codegen stage")
        exit(1)

    if args.output_asm:
        with open(args.o + '.s', 'w') as fp:
            fp.write(assembly)

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.s') as fp:
        fp.write(assembly)
        fp.close()

        cmd = ['gcc', '-g', f'-{args.compiler_opt_level}', '-o', args.o, 'runtime.c', fp.name]
        res = subprocess.run(cmd)
