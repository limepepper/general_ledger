from typing import Dict, Optional, TypeVar, Generic, Iterator
from collections import deque, OrderedDict

from rich import inspect

T = TypeVar("T", bound="TreeMixin")


class TreeMixin(Generic[T]):
    """a tree that supports visiting"""

    def __init__(
        self,
        name: str,
        **kwargs,
    ):
        self.name = name
        self._children: OrderedDict[str, T] = OrderedDict()
        self.parent: Optional[T] = None
        self._depth = None

    def accept(self, visitor, /, *args, **kwargs):
        return visitor.visit(self, *args, **kwargs)

    @property
    def is_leaf(self) -> bool:
        return len(self._children) == 0

    @property
    def has_children(self) -> bool:
        return not self.is_leaf

    @property
    def is_root(self) -> bool:
        return self.parent is None

    @property
    def root(self) -> T:
        current_node = self
        while current_node.parent is not None:
            current_node = current_node.parent
        return current_node

    def add_child(self, child: T) -> T:
        if self.root.find(child.name, strict=False):
            raise ValueError(
                f"Node '{child.name}' already exists in tree. name must be unique."
            )
        self._children[child.name] = child
        child.parent = self
        child._depth = None
        return self

    def get_child(self, name: str, strict: bool = True) -> T | None:
        """Get a child node by name"""
        if name not in self._children and strict:
            raise KeyError(f"Child node '{name}' does not exist")
        elif name not in self._children:
            return None
        return self._children[name]

    @property
    def depth(self) -> int:
        if self._depth is not None:
            return self._depth
        count = 0
        current_node = self
        while current_node.parent is not None:
            count += 1
            current_node = current_node.parent
        self._depth = count
        return count

    def get_path(self) -> str:
        """Get the path to this node"""
        if self.parent:
            return f"{self.parent.get_path()}/{self.name}"
        return self.name

    def show_nest(self) -> str:
        """Get the path to this node in dictionary format"""
        if self.parent:
            return f"{self.parent.show_nest()}['{self.name}']"
        return f"['{self.name}']"

    def items(self, reverse=False):
        return reversed(self._children.items()) if reverse else self._children.items()

    def keys(self, reverse=False):
        return reversed(self._children.keys()) if reverse else self._children.keys()

    def values(self, reverse=False):
        return reversed(self._children.values()) if reverse else self._children.values()

    def __len__(self):
        return len(self._children)

    def __getitem__(self, item):
        return self._children[item]

    def __setitem__(self, key, value):
        self._children[key] = value
        value.parent = self

    def __iter__(self):
        return iter(self._children.keys())

    def __delitem__(self, name: str) -> None:
        if name in self._children:
            child = self._children[name]
            del self._children[name]
            child.parent = None
        else:
            raise KeyError(f"Node '{self.name}' has no child named '{name}'")

    def __bool__(self) -> bool:
        """A TreeMixin instance is always True unless it's None."""
        return True

    @staticmethod
    def remove(node: T) -> None:
        if node.parent:
            del node.parent._children[node.name]
            node.parent = None
        else:
            raise ValueError(
                "Cannot remove the root node directly. "
                "Use another approach like clearing the tree."
            )

    def find(self, name: str, strict: bool = True) -> Optional[T]:
        """Finds a node by name in self or subtree."""
        if self.name == name:
            return self
        for child in self.values():
            found_node = child.find(name, strict=False)
            if found_node:
                return found_node
        if strict:
            raise LookupError(f"Node '{name}' not found in tree")
        return None

    def pre_order_traversal(self, reverse=False) -> Iterator[T]:
        yield self
        for child in self.values(reverse):
            yield from child.pre_order_traversal(reverse)

    def post_order_traversal(self, reverse=False) -> Iterator[T]:
        for child in self.values(reverse):
            yield from child.post_order_traversal(reverse)
        yield self

    def level_order_traversal(self, reverse=False) -> Iterator[T]:
        queue = deque([self])
        while queue:
            node = queue.popleft()
            yield node
            queue.extend(node.values(reverse))  # Enqueue all children of the node

    def __rich_repr__(self):
        yield self.name
        yield "depth", self.depth
        yield "is_leaf", self.is_leaf
        yield "children", self._children.keys()
        # yield from self.pre_order_traversal()
