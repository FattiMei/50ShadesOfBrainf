#!/usr/bin/env python3

"""
This file acts as the compiler driver, it loads the source code
and calls the compiler functions for parsing, optimization and
code generation for multiple targets
"""


import ir
import parser
import argparse


def parse_cmd_line_args():
    argparser = argparse.ArgumentParser(prog="bfcom")
    argparser.add_argument("input_file", type=str, help="which file to compile")

    return argparser.parse_args()


if __name__ == '__main__':
    args = parse_cmd_line_args()
    with open(args.input_file, 'r') as file:
        src = file.read()

    program = parser.parse_source(src)
    if program is None:
        exit(1)

    assert(program.are_bb_well_formed())
    # assert(program.are_bb_reachable())

    # # if the program is well formed and the parsing function is correct,
    # # one could generate the original source from the intermediate representation
    # filtered_src = ''.join(filter(lambda c: c in parser.LANGUAGE_TOKENS, src))
    # reconstructed_src = parser.reconstruct_src(basic_blocks[0])
    # assert(filtered_src == reconstructed_src)
