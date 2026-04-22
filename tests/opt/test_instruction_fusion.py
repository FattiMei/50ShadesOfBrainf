import unittest
from brainf import parser
from brainf.codegen.transpiler import generate_original_src
from brainf.opt.instruction_fusion import instruction_fusion_pass


class TestInstructionFusion(unittest.TestCase):
    def test_pass_identity(self):
        src = "+++++[<<<-[---]>>>]"
        program = parser.parse_source(src)

        instruction_fusion_pass(program)
        reconstructed_src = generate_original_src(program)

        self.assertTrue(src == reconstructed_src)

    def test_elision(self):
        program = parser.parse_source(
            " +- <> -+ >< ++ -- << >>"
        )
        instruction_fusion_pass(program)

        self.assertTrue(generate_original_src(program) == "")

    def test_elision_limits(self):
        # in this example we miss an optimization chance
        #   1. the instruction fusion pass generates an empty block
        #   2. the loop elimination pass collapses that block
        #   3. possibly go to (1)
        #
        # this process can be stopped if an optimization pass didn't
        # mutate the IR
        program = parser.parse_source("+[+-]-")
        instruction_fusion_pass(program)

        self.assertTrue(generate_original_src(program) == "+[]-")


if __name__ == '__main__':
    unittest.main()
