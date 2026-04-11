#!/usr/bin/env python3

"""
This file acts as the compiler driver, it loads the source code
and calls the compiler functions for parsing, optimization and
code generation for multiple targets
"""


import argparse
from parser import parse_source


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="bfcom")
    parser.add_argument("input_file", type=str, help="which file to compile")

    args = parser.parse_args()
    with open(args.input_file, 'r') as file:
        src = file.read()

    print(parse_source(src))
