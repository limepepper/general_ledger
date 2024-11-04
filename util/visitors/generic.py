#
# pure visitor pattern
#


class GenericVisitor:
    def __init__(self, method):
        self.method = method

    def visit(self, node, *args):
        func = getattr(node, self.method)
        # func = getattr(node, self.method)
        # print(func())
        # for child in node._children.values():
        #     self.visit(child)
