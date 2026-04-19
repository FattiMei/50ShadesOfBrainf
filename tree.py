"""
This file is an attempt to first produce a tree representation
of a Brainf program.

I think that tree representations can still provide good value
for example in detecting empty loops or similar structures
"""


from enum import Enum


class TreeNode:
    def __init__(self, parent: "TreeNode" = None):
        self.parent = parent

    def set_parent(self, parent: "TreeNode"):
        self.parent = parent


class EmptyNode(TreeNode):
    def __init__(self, parent: TreeNode = None):
        super().__init__(parent)

    def __repr__(self) -> str:
        return 'EmptyNode()'


class Seq(TreeNode):
    def __init__(self,
                 left: TreeNode = None,
                 right: TreeNode = None,
                 parent: TreeNode = None):
        super().__init__(parent)
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f'Seq({self.left}, {self.right}'


class Loop(TreeNode):
    def __init__(self,
                 body: TreeNode,
                 parent: TreeNode = None,
                 source_pos: tuple[int, int] = None):
        super().__init__(parent)
        self.body = body
        self.source_pos = source_pos

    def __repr__(self) -> str:
        return f'Loop({self.body})'


class Statement(TreeNode):
    """
    This class is designed to be generic about the type
    of statement. It could be a token or an instruction
    """
    def __init__(self, stat = None, parent: TreeNode = None):
        super().__init__(parent)
        self.stat = stat

    def __repr__(self) -> str:
        return f'Statement({self.stat})'


def update_parent_relations(entry_point: TreeNode):
    """
    Assuming the arc parent->child is correct, builds the arc
    child->parent recursively on every node in the tree
    """
    if type(entry_point) == Seq:
        left, right = entry_point.left, entry_point.right
        left.set_parent(entry_point)
        right.set_parent(entry_point)

        update_parent_relations(left)
        update_parent_relations(right)

    elif type(entry_point) == Loop:
        body = entry_point.body
        body.set_parent(entry_point)

        update_parent_relations(body)
