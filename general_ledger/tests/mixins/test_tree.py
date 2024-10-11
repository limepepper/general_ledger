import unittest

from rich.console import Console

from general_ledger.statements.mixins import TreeMixin

console = Console()


class TestTreeMixin(unittest.TestCase):
    def setUp(self):
        """Setup method to create a sample tree for testing."""
        self.tree = TreeMixin("root")
        self.tree.add_child(TreeMixin("A"))
        self.tree.add_child(TreeMixin("B"))
        self.tree["A"].add_child(TreeMixin("A1"))
        self.tree["A"].add_child(TreeMixin("A2"))
        self.tree["B"].add_child(TreeMixin("B1"))

    def test_init(self):
        """Test the constructor of the TreeMixin class."""
        self.assertEqual(self.tree.name, "root")
        self.assertEqual(len(self.tree._children), 2)
        self.assertIsNone(self.tree.parent)

    def test_add_child(self):
        """Test adding a child to the tree."""
        self.tree.add_child(TreeMixin("C"))
        self.assertEqual(len(self.tree._children), 3)
        self.assertEqual(self.tree["C"].name, "C")
        self.assertEqual(self.tree["C"].parent, self.tree)

    def test_get_child(self):
        """Test retrieving a child node."""
        self.assertEqual(self.tree.get_child("A").name, "A")
        self.assertIsNone(self.tree.get_child("Nonexistent", strict=False))
        with self.assertRaises(KeyError):
            self.tree.get_child("Nonexistent")

    def test_is_leaf(self):
        """Test checking if a node is a leaf."""
        self.assertTrue(self.tree.find("A1").is_leaf)
        self.assertFalse(self.tree["A"].is_leaf)

    def test_has_children(self):
        """Test checking if a node has children."""
        self.assertTrue(self.tree["A"].has_children)
        self.assertFalse(self.tree.find("B1").has_children)

    def test_depth(self):
        """Test calculating the depth of a node."""
        self.assertEqual(self.tree.depth, 0)
        self.assertEqual(self.tree["A"].depth, 1)
        self.assertEqual(self.tree.find("A1").depth, 2)

    def test_get_path(self):
        """Test retrieving the path to a node."""
        self.assertEqual(self.tree.get_path(), "root")
        self.assertEqual(self.tree["A"].get_path(), "root/A")
        self.assertEqual(self.tree.find("A1").get_path(), "root/A/A1")

    def test_show_nest(self):
        """Test retrieving the path to a node in dictionary format."""
        self.assertEqual(self.tree.show_nest(), "['root']")
        self.assertEqual(self.tree["A"].show_nest(), "['root']['A']")
        self.assertEqual(self.tree["A"]["A1"].show_nest(), "['root']['A']['A1']")

    def test_delitem(self):
        """Test deleting a child node."""
        del self.tree["A"]
        self.assertEqual(len(self.tree._children), 1)
        with self.assertRaises(KeyError):
            del self.tree["A"]

    def test_remove(self):
        """Test removing a node from the tree."""
        TreeMixin.remove(self.tree["A"])
        self.assertEqual(len(self.tree._children), 1)
        with self.assertRaises(ValueError):
            TreeMixin.remove(self.tree)

    def test_removes_node_correctly(self):
        root = TreeMixin(name="root")
        child = TreeMixin(name="child")
        root.add_child(child)
        TreeMixin.remove(child)
        assert child not in root._children.values()
        assert child.parent is None

    def test_find(self):
        """Test finding a node by name."""
        self.assertEqual(self.tree.find("A1"), self.tree["A"]["A1"])
        self.assertIsNone(self.tree.find("Nonexistent", strict=False))

    def test_pre_order_traversal(self):
        """Test pre-order traversal of the tree."""
        expected_order = ["root", "A", "A1", "A2", "B", "B1"]
        self.assertEqual(
            [node.name for node in self.tree.pre_order_traversal()], expected_order
        )

    def test_post_order_traversal(self):
        """Test post-order traversal of the tree."""
        expected_order = ["A1", "A2", "A", "B1", "B", "root"]
        self.assertEqual(
            [node.name for node in self.tree.post_order_traversal()], expected_order
        )

    def test_level_order_traversal(self):
        """Test level-order traversal of the tree."""
        expected_order = ["root", "A", "B", "A1", "A2", "B1"]
        self.assertEqual(
            [node.name for node in self.tree.level_order_traversal()], expected_order
        )

    def test_reversed_traversals(self):
        """Test the traversal methods with the reverse flag."""
        expected_pre_order = ["root", "B", "B1", "A", "A2", "A1"]
        self.assertEqual(
            [node.name for node in self.tree.pre_order_traversal(reverse=True)],
            expected_pre_order,
        )

        expected_post_order = ["B1", "B", "A2", "A1", "A", "root"]
        self.assertEqual(
            [node.name for node in self.tree.post_order_traversal(reverse=True)],
            expected_post_order,
        )

        expected_level_order = ["root", "B", "A", "B1", "A2", "A1"]
        self.assertEqual(
            [node.name for node in self.tree.level_order_traversal(reverse=True)],
            expected_level_order,
        )

    def test_len(self):
        """Test getting the number of children."""
        self.assertEqual(len(self.tree), 2)
        self.assertEqual(len(self.tree["A"]), 2)
        self.assertEqual(len(self.tree["B"]["B1"]), 0)
        property()

    def test_getitem(self):
        """Test accessing children using indexing."""
        self.assertEqual(self.tree["A"].name, "A")
        with self.assertRaises(KeyError):
            _ = self.tree["Nonexistent"]

    def test_setitem(self):
        """Test setting a child node using indexing."""
        new_node = TreeMixin("C")
        self.tree["C"] = new_node
        self.assertEqual(self.tree["C"], new_node)
        self.assertEqual(new_node.parent, self.tree)

    def test_iter(self):
        """Test iterating over the children."""
        children_names = [child.name for child in self.tree.values()]
        self.assertEqual(children_names, ["A", "B"])
