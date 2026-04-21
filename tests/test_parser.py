import unittest
from brainf import parser
from brainf.codegen.transpile import generate_original_src


class TestParser(unittest.TestCase):
    def test_parser_identity(self):
        src = "[][---.,.]++,..<>>[[-]]"
        filtered_src = ''.join(filter(lambda c: c in parser.LANGUAGE_TOKENS, src))

        program = parser.parse_source(src)

        reconstructed_src = generate_original_src(program)
        self.assertTrue(filtered_src == reconstructed_src)

    def test_missing_closed_paren(self):
        ill_formed_src = "[][--,.<<"

        with self.assertRaises(SyntaxError):
            program = parser.parse_source(ill_formed_src)

    def test_unmatched_closed_paren(self):
        ill_formed_src = "....fdsk]"

        with self.assertRaises(SyntaxError):
            program = parser.parse_source(ill_formed_src)


if __name__ == '__main__':
    unittest.main()
