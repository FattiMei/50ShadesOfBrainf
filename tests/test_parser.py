import unittest
from brainf import parser
from brainf.codegen.transpile import generate_original_src


class TestParser(unittest.TestCase):
    def test_parser_identity(self):
        src = "[][---.,.]++,..<>>[[-]]"
        filtered_src = ''.join(filter(lambda c: c in parser.LANGUAGE_TOKENS, src))

        program = parser.parse_source(src)
        self.assertTrue(program is not None)

        reconstructed_src = generate_original_src(program)
        self.assertTrue(filtered_src == reconstructed_src)


if __name__ == '__main__':
    unittest.main()
