#!/usr/bin/env python3


import tree
from lexer import Lexer, Token, TEST_SOURCE


class Parser:
    """
    This class takes a lexer objects and produces a tree IR and possibly errors.
    I have designed it to mimic the professor's Parser class, but I want to add
    clear error messages
    """
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.fail = False

    def error(self, msg: str):
        """
        This function is used by the parser to signal errors in the program.
        """
        print(f'[PARSER]: {msg}')
        self.fail = True

    def expect(self, token: Token) -> bool:
        """
        Consumes a token only if matches `token` and returns True,
        otherwise does nothing and returns False
        """
        t, _, _ = self.lexer.peek()
        if t == token:
            self.lexer.next()
            return True
        else:
            return False

    def block(self) -> tree.TreeNode:
        t, _, _ = self.lexer.peek()

        if t == Token.END:
            return tree.EmptyNode()
        elif t == Token.CLOSEDPAREN:
            return tree.EmptyNode()
        elif t == Token.OPENPAREN:
            loop = self.loop()
            return tree.Seq(left=loop, right=self.block())
        else:
            self.lexer.next()

            # a right recursive tree allows for tail recursion
            # when navigating the tree in program order
            return tree.Seq(
                left=tree.Statement(t),
                right=self.block()
            )

    def loop(self) -> tree.TreeNode:
        t, row, col = self.lexer.peek()
        assert(self.expect(Token.OPENPAREN))

        body = self.block()
        if self.expect(Token.CLOSEDPAREN):
            return tree.Loop(body)

        self.error(f'In loop opened at {(row,col)} expected `]` but found EOF')
        return tree.EmptyNode()

    def run(self) -> tree.TreeNode:
        program = self.block()

        t, row, col = self.lexer.peek()
        if t == Token.END:
            return program

        assert(t == Token.CLOSEDPAREN)
        self.error(f'Found `]` at {(row,col)} for a loop that was never opened')

        return program


# import ir
# 
# """
# This function is a generator of basic block with increasing labels.
# The basic blocks generated are guaranteed to have unique labels
# """
# def bb_generator():
#     count = 0
# 
#     while True:
#         yield ir.BasicBlock(label=count)
#         count += 1
# 
# 
# """
# Returns a list of basic blocks and the first one is the entry point.
# It may fail when the program is ill-formed because of parenthesis mismatch.
# """
# def parse_source(src: str) -> ir.Program:
#     bb_gen = bb_generator()
#     curr = next(bb_gen)
#     basic_blocks = [curr]
# 
#     # this is the data structure I use for keeping track
#     # of which BB I still need to properly connect
#     bb_stack = []
# 
#     for (token, row, col) in token_generator(src):
#         if token == Token.PLUS:
#             curr.append(ir.Increment())
#         elif token == Token.MINUS:
#             curr.append(ir.Decrement())
#         elif token == Token.SHIFTL:
#             curr.append(ir.MoveLeft())
#         elif token == Token.SHIFTR:
#             curr.append(ir.MoveRight())
#         elif token == Token.GETC:
#             curr.append(ir.GetChar())
#         elif token == Token.PUTC:
#             curr.append(ir.PutChar())
# 
#         # we are at the end of the current basic block
#         elif token == Token.OPENPAREN:
#             new = next(bb_gen)
#             basic_blocks.append(new)
# 
#             curr.append(
#                 ir.BranchIfZero(
#                     target_block=None, # we don't know it yet
#                     fallthrough_block=new,
#                     debug_info=(row,col)
#                 )
#             )
# 
#             bb_stack.append(curr)
#             curr = new
# 
#         elif token == Token.CLOSEDPAREN:
#             new = next(bb_gen)
#             basic_blocks.append(new)
# 
#             if len(bb_stack) == 0:
#                 print(f"ERROR: found `]` at ({row},{col}) but the corresponding `[` was never opened")
#                 return None
# 
#             old = bb_stack.pop()
#             old.get_terminator().target_block = new
# 
#             curr.append(
#                 ir.BranchIfNotZero(
#                     target_block=old.get_terminator().fallthrough_block,
#                     fallthrough_block=new
#                 )
#             )
#             curr = new
# 
#     # in a well formed program all the parenthesis should be closed
#     if len(bb_stack) > 0:
#         missing_closing = [bb.get_terminator().debug_info for bb in bb_stack]
#         print(f"ERROR: some parenthesis are still to be closed at {missing_closing}")
#         return None
# 
#     # at the end of the program we insert a return instruction
#     # so that every basic block is well formed
#     curr.append(ir.Return())
# 
#     return ir.Program(basic_blocks)
