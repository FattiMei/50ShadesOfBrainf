import pytest
from pathlib import Path

from brainf import parser
from brainf.opt.loop import annotate_infinite_loops_pass
from brainf.codegen.transpiler import generate_original_src


# at the moment I'm hardcoding where to find the source files
# the test is run only from the root directory of the package
SOURCE_DIR = Path("samples")
SOURCE_FILES = list(SOURCE_DIR.glob("*.b"))


@pytest.mark.parametrize("filename", SOURCE_FILES, ids=lambda p: p.name)
def test_pipeline(filename: str):
    with open(filename, 'r') as file:
        src = file.read()

    program = parser.parse_source(src)
    annotate_infinite_loops_pass(program)

    # this is just the composition of parser and transpiler
    filtered_src = ''.join(filter(lambda c: c in parser.LANGUAGE_TOKENS, src))
    reconstructed_src = generate_original_src(program)
    assert(filtered_src == reconstructed_src)

    assert(program.are_bb_well_formed())
    assert(program.are_bb_reachable())

    for basic_block in program.basic_blocks:
        for successor in basic_block.get_successors():
            assert(basic_block in successor.get_predecessors())
