#!/usr/bin/env python3


import tree


class AbstractGenerator:
    def generate(self, entry_point: tree.TreeNode):
        raise NotImplemented


class BrainfGenerator:
    def __init__(self):
        pass

    def generate(self, entry_point: tree.TreeNode) -> str:
        if type(entry_point) == tree.EmptyNode:
            return ''
        elif type(entry_point) == tree.Seq:
            return self.generate(entry_point.left) + self.generate(entry_point.right)
        elif type(entry_point) == tree.Loop:
            return '[' + self.generate(entry_point.body) + ']'
        elif type(entry_point) == tree.Statement:
            return entry_point.stmt.get_token_repr()

        assert False, "unreachable"


class CGenerator(AbstractGenerator):
    def __init__(self):
        self.lines = []

    def _push_line(self, line: str, indent):
        tabs = '\t' * indent
        self.lines.append(tabs + line)

    def _generate(self, entry_point: tree.TreeNode, indent: int):
        if type(entry_point) == tree.EmptyNode:
            pass
        elif type(entry_point) == tree.Seq:
            self._generate(entry_point.left, indent)
            self._generate(entry_point.right, indent)
        elif type(entry_point) == tree.Loop:
            self._push_line('while (*memory != 0) {', indent)
            self._generate(entry_point.body, indent+1)
            self._push_line('}', indent)
        elif type(entry_point) == tree.Statement:
            pass # TODO

    def generate(self, entry_point: tree.TreeNode) -> str:
        self.lines.clear()
        self._push_line('void run(char* memory) {', indent=0)
        self._generate(entry_point, indent=1)
        self._push_line('}', indent=0)
        return '\n'.join(self.lines)


if __name__ == '__main__':
    from lexer import Lexer, TEST_SOURCE
    from parser import Parser

    lexer = Lexer(TEST_SOURCE)
    parser = Parser(lexer)
    program = parser.run()

    reconstructed_src = BrainfGenerator().generate(program)
    assert(reconstructed_src == TEST_SOURCE)


# import ir
# from enum import Enum
# 
# 
# def generate_original_src(program: ir.Program) -> str:
#     """
#     This function generates the unformatted source code from the IR
#     """
#     res = ''
#     end = False
#     curr = program.get_entry_point()
# 
#     while not end:
#         for instr in curr.instructions:
#             res += instr.get_token()
# 
#         terminator = curr.get_terminator()
#         if type(terminator) == ir.Return:
#             end = True
#         else:
#             curr = terminator.fallthrough_block
# 
#     return res
# 
# def generate_x86(program: ir.Program, head_register: str = '%rax', val_register: str = '%bl') -> str:
#     """
#     This function generates the x86 assembly code for the function run(char *) that
#     implements `program`
# 
#     We don't have the concept of registers in the IR, so all the decisions are hardcoded here.
#     * where to store the pointer to the memory tape
#     * where to store the cell value for local processing before storing it
# 
#     It's important that `val_register` is an 8-bit register, otherwise the store operations like
#         mov %rbx, [%rax]
# 
#     will write 8 bytes and so will overwrite adjacent cells. The "samples/sierpinski.b" program
#     suffers from this phenomenon
#     """
#     lines = []
#     end = False
#     curr = program.get_entry_point()
# 
#     head = head_register
#     val = val_register
#     assert(head != val)
# 
#     lines += ['\t.data']
#     lines += ['\t.globl run']
#     lines += ['\t.text']
#     lines += ['run:']
# 
#     # %rdi should be the first argument in the call
#     # of run(char*)
#     lines += [f'mov %rdi, {head}']
# 
#     while not end:
#         lines += [f'.L{curr.label}:']
# 
#         for instr in curr.instructions:
#             if type(instr) == ir.Increment:
#                 lines += [f'mov ({head}), {val}']
#                 lines += [f'add ${instr.imm}, {val}']
#                 lines += [f'mov {val}, ({head})']
# 
#             elif type(instr) == ir.Decrement:
#                 lines += [f'mov ({head}), {val}']
#                 lines += [f'sub ${instr.imm}, {val}']
#                 lines += [f'mov {val}, ({head})']
# 
#             elif type(instr) == ir.MoveLeft:
#                 lines += [f'sub ${instr.imm}, {head}']
# 
#             elif type(instr) == ir.MoveRight:
#                 lines += [f'add ${instr.imm}, {head}']
# 
#             elif type(instr) == ir.GetChar:
#                 # it should be a syscall to getchar()
#                 assert(False)
# 
#             elif type(instr) == ir.PutChar:
#                 lines += [f'push {head}']
#                 lines += [f'mov ({head}), %rdi']
#                 lines += ['call putchar']
#                 lines += [f'pop {head}']
# 
#             elif type(instr) == ir.BranchIfZero:
#                 target_block = instr.target_block
# 
#                 lines += [f'mov ({head}), {val}']
#                 lines += [f'cmp $0, {val}']
#                 lines += [f'jz .L{target_block.label}']
# 
#                 curr = instr.fallthrough_block
# 
#             elif type(instr) == ir.BranchIfNotZero:
#                 target_block = instr.target_block
# 
#                 lines += [f'mov ({head}), {val}']
#                 lines += [f'cmp $0, {val}']
#                 lines += [f'jnz .L{target_block.label}']
# 
#                 curr = instr.fallthrough_block
# 
#             elif type(instr) == ir.Return:
#                 lines += ['ret']
#                 end = True
# 
#     lines += ['']
# 
#     return '\n'.join(lines)
# 
# 
# def generate_armv6l(program: ir.Program) -> str:
#     """
#     For the arm backend the problem of storing only a single byte
#     doesn't exist as there is a `strb` instruction
#     """
#     lines = []
#     end = False
#     curr = program.get_entry_point()
# 
#     head = 'r0'
#     val  = 'r1'
# 
#     lines += ['\t.globl run']
#     lines += ['\t.text']
#     lines += ['run:']
#     lines += ['push {fp, lr}']
# 
#     while not end:
#         lines += [f'.L{curr.label}:']
# 
#         for instr in curr.instructions:
#             if type(instr) == ir.Increment:
#                 lines += [f'ldr {val}, [{head}]']
#                 lines += [f'add {val}, #{instr.imm}']
#                 lines += [f'strb {val}, [{head}]']
# 
#             elif type(instr) == ir.Decrement:
#                 lines += [f'ldr {val}, [{head}]']
#                 lines += [f'sub {val}, #{instr.imm}']
#                 lines += [f'strb {val}, [{head}]']
# 
#             elif type(instr) == ir.MoveLeft:
#                 lines += [f'sub {head}, #{instr.imm}']
# 
#             elif type(instr) == ir.MoveRight:
#                 lines += [f'add {head}, #{instr.imm}']
# 
#             elif type(instr) == ir.GetChar:
#                 # it should be a syscall to getchar()
#                 assert(False)
# 
#             elif type(instr) == ir.PutChar:
#                 lines += [f'push {{ {head} }}']
#                 lines += [f'ldr r0, [{head}]']
#                 lines += [f'bl putchar']
#                 lines += [f'pop {{ {head} }}']
# 
#             elif type(instr) == ir.BranchIfZero:
#                 target_block = instr.target_block
# 
#                 lines += [f'ldr {val}, [{head}]']
#                 lines += [f'and {val}, #255']
#                 lines += [f'cmp {val}, #0']
#                 lines += [f'beq .L{target_block.label}']
# 
#                 curr = instr.fallthrough_block
# 
#             elif type(instr) == ir.BranchIfNotZero:
#                 target_block = instr.target_block
# 
#                 lines += [f'ldr {val}, [{head}]']
#                 lines += [f'and {val}, #255']
#                 lines += [f'cmp {val}, #0']
#                 lines += [f'bne .L{target_block.label}']
# 
#                 curr = instr.fallthrough_block
# 
#             elif type(instr) == ir.Return:
#                 lines += ['pop {fp, pc}']
#                 end = True
# 
#     lines += ['']
# 
#     return '\n'.join(lines)
# 
# 
# class FixedSizeInstruction:
#     class Type(Enum):
#         INCREMENT = 0
#         DECREMENT = 1
#         MOVELEFT  = 2
#         MOVERIGHT = 3
#         GETC      = 4
#         PUTC      = 5
#         BZ        = 6
#         BNZ       = 7
# 
#     # in the case of branching instructions, the operand
#     # should be the absolute address of the target
#     #
#     # I imagine that in a future one may want relative
#     # addressing, how should I implement this?
#     def __init__(self, instruction_type: Type, operand: int):
#         self.instruction_type = instruction_type
#         self.operand = operand
# 
# 
# def generate_fixed_size_instructions(program: ir.Program) -> list[FixedSizeInstruction]:
#     result = []
# 
#     return result
