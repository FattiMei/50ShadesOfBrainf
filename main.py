#!/usr/bin/env python3

"""
This file acts as the compiler driver, it loads the source code
and calls the compiler functions for parsing, optimization and
code generation for multiple targets
"""


from lexer import Lexer
from parser import Parser


import ir
import opt
import parser
import codegen

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
    """
    args = parse_cmd_line_args()

    with open(args.input_file, 'r') as file:
        src = file.read()
    """
    with open('samples/hello.b', 'r') as file:
        src = file.read()

    lexer = Lexer(src)
    parser = Parser(lexer)
    program = parser.run()

    code_generator = codegen.CGenerator()
    print(code_generator.generate(program))
    exit()

    program = parser.parse_source(src)
    if program is None:
        print("Compilation interrupted at parsing stage")
        exit(1)

    # if the parsing was successful, then the data structures
    # must be in valid state
    assert(program.are_bb_well_formed())
    assert(program.are_bb_reachable())

    # this is just a test for the ascii codegen
    filtered_src = ''.join(filter(lambda c: c in parser.LANGUAGE_TOKENS, src))
    reconstructed_src = codegen.generate_original_src(program)
    assert(filtered_src == reconstructed_src)

    # this is a test for the deepcopy function
    #
    # In the future I might use the deepcopy to preserve the original
    # program while doing optimizations.
    #
    # I would like to verify the correctness of the optimizations by executing
    # the original program and the optimized one at runtime and then inspect the
    # memory tape
    cloned_program = program.deepcopy()
    assert(cloned_program.are_bb_reachable())

    # optimization pass, to be selected only if the user requires so
    if args.opt:
        print("Performing instruction fusion...")
        opt.instruction_fusion_pass(program)

    # it's strange that this assertion holds, maybe I need to test more completely the deepcopy
    # function
    assert(codegen.generate_original_src(cloned_program) == codegen.generate_original_src(program))

    machine = os.uname().machine
    if machine == 'x86_64':
        assembly = codegen.generate_x86(program)
    elif machine in ['armv6l']:
        assembly = codegen.generate_armv6l(program)
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
