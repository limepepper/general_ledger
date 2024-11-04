#
# pass and pre and post callable functions to the visitor
#

from general_ledger.utils.inspect import inspect


class RecursiveFuncVisitor:
    """A visitor that allows for pre- and post-functions to be called on each node"""

    def __init__(
        self,
        pre_func: callable = None,
        post_func: callable = None,
        reverse: bool = False,
    ):
        self._pre_func = pre_func
        self._post_func = post_func
        self.reverse = reverse
        super().__init__()

    def visit(self, node, level: int = 0):
        results = []
        # inspect(self, all=True)
        if self._pre_func:
            results.append(
                self._pre_func(node, level + 1),
            )
        for _, child in node.items(self.reverse):
            results.extend(child.accept(self, level + 1))
        if self._post_func:
            results.append(
                self._post_func(node, level + 1),
            )
        return results
