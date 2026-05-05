The goal of this project is to produce a compiler for the Brainfuck (BF) computational model.

## General
The compiler must take the source code from either a string or a file and produce an intermediate representation. In the process it must signal to the user the possible errors in the source code, which can be:
  * a `]` instruction was found, but the corresponding `[` was never opened
  * some `[` instructions were never closed

these are the only sources of errors as we allow for empty programs and any character not in `+-<>[],.` is considered a comment. It would be nice if the error were signaled with also source position (row, column pair)

## Structure of the IR
The IR must be designed to capture the semantics of the BF computational model, but also allow for optimizations and analyses passes. Two designs for the IR were considered: a tree based and a CFG based representation.

### Tree based IR
The tree based representation allows for pattern matching and easy recognition of loops, but it has the complication of selecting a good data structure for sequence of statements. Consider the following definition of an IR node:

```haskell
data IrNode
  = Statement Instr
  | Loop IrNode
  | Seq IrNode IrNode
  | Empty
  deriving Show
```

this allows the `Seq` node to have both arbitrary deep subtrees as left and right child. I think this would impact the performance when navigating recursively the tree in program order. Ideally I would like the sequence tree to grow only on the right like

```
   Seq
   /  \
  /    \
 Stat  Seq
       /  \
     Loop  Seq
           ...
```

the idea of a tree based IR was abandoned after the first recursive descent parser (implemented in python) reached the *maximum recursion depth*. A possible solution would be to merge the sequence nodes into a list of nodes.

### CFG based IR
The original implementation used a control flow graph: a directed graph of basic blocks. This has the disadvantage of requiring to maintain a correct state after each pass. For example a basic block contains:
  * a list of predecessors
  * a list of successors (which is coupled with the operands of the terminator instruction, the last instruction in the block)

everything must be in order, especially when removing basic blocks from the graph.


### Additions
I needed to add new IR nodes for operations that extend the computational model like:
  * adding an immediate instead of only 1
  * setting a cell to 0
