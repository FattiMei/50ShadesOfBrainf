#!/usr/bin/env python3

"""
This file acts as the compiler driver, it loads the source code
and calls the compiler functions for parsing, optimization and
code generation for multiple targets
"""


import ir
import parser
import codegen
import runtime
import argparse


def parse_cmd_line_args():
    argparser = argparse.ArgumentParser(prog="bfcom")
    argparser.add_argument("input_file", type=str, nargs='+', help="which file to compile")

    return argparser.parse_args()


if __name__ == '__main__':
    args = parse_cmd_line_args()

    for input_file in args.input_file:
        with open(input_file, 'r') as file:
            src = file.read()

        program = parser.parse_source(src)
        if program is None:
            exit(1)

        assert(program.are_bb_well_formed())
        assert(program.are_bb_reachable())

        filtered_src = ''.join(filter(lambda c: c in parser.LANGUAGE_TOKENS, src))
        reconstructed_src = codegen.generate_original_src(program)
        assert(filtered_src == reconstructed_src)

        cloned_program = program.deepcopy()
        assert(cloned_program.are_bb_reachable())

        print(codegen.generate_x86(program))
        print(codegen.generate_arm(program))
