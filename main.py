#!/usr/bin/env python3

"""
This file acts as the compiler driver, it loads the source code
and calls the compiler functions for parsing, optimization and
code generation for multiple targets
"""


import ir
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

    # later, which optimizations to perform

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_cmd_line_args()

    with open(args.input_file, 'r') as file:
        src = file.read()

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

    machine = os.uname().machine
    if machine == 'x86_64':
        assembly = codegen.generate_x86(program)
    elif machine in ['aarch64']:
        assembly = codegen.generate_arm(program)
    else:
        print(f'`{machine}` is unsupported')
        print("Compilation interrupted at codegen stage")
        exit(1)

    with tempfile.NamedTemporaryFile(mode='w', delete_on_close=False, suffix='.s') as fp:
        fp.write(assembly)
        fp.close()

        cmd = ['gcc', '-o', args.o, 'runtime.c', fp.name]
        res = subprocess.run(cmd)
