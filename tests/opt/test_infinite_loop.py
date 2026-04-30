import unittest
from brainf import ir, parser
from brainf.codegen.transpiler import generate_original_src
from brainf.opt.loop import annotate_infinite_loops_pass


class TestInfiniteLoop(unittest.TestCase):
    def test_pass_identity(self):
        src = "+++-[]-[[]]--<<,.,"
        program = parser.parse_source(src)
        annotate_infinite_loops_pass(program)

        reconstructed_src = generate_original_src(program)
        self.assertTrue(src == reconstructed_src)

    def test_predecessor(self):
        src = "+++-[]-[[]]--<<,.,"
        program = parser.parse_source(src)
        annotate_infinite_loops_pass(program)

        for basic_block in program.basic_blocks:
            terminator = basic_block.get_terminator()

            if type(terminator) == ir.Return:
                if terminator.returncode != 0:
                    self.assertTrue(len(basic_block.instructions) == 1)
                    self.assertTrue(basic_block not in basic_block.get_successors())
                    self.assertTrue(basic_block not in basic_block.get_predecessors())


if __name__ == '__main__':
    unittest.main()
