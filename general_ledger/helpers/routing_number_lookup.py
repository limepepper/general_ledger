class RoutingLookup:
    def __init__(self, routing_number):
        self.routing_number = routing_number

    @classmethod
    def lookup(
        cls,
        account_number,
        routing_number,
        bankid=None,
    ):
        return "Bank Name"


class SortCodeNode:
    def __init__(self):
        self.children = {}
        self.char = None
        self.value = None


class SortCodeTrie:
    def __init__(self):
        self.root = SortCodeNode()

    def insert_sort_code(self, sort_code, value):
        if sort_code is None or value is None:
            raise ValueError("sort_code and value must be provided")
        self.segment_sort_code(self.root, sort_code, value)

    def segment_sort_code(self, node,  remaining, value):
        # find range of prefixes for this segment
        start, end, remaining = self._parse_range(remaining)
        #print(f"range info '{value}' start:{start} end:{end} remaining '{remaining}'")

        for i in range(int(start), int(end)+1):
            segment = f"{i:0>2}"
            #print(f"processing insert from node '{node}' segment '{segment}' remaining '{remaining}' value '{value}'")
            seg_node = self.insert(node, segment, None if remaining else value)
            if remaining:
                self.segment_sort_code(seg_node, remaining, value)


    def insert(self, node, remaining, value):
        #print(f"inside insert from node '{node.char}' remaining '{bool(remaining)}' value '{value}'")
        if not remaining:
            if "terminal" in node.children:
                pass
            elif value:
                #print(f"adding child with value {value}")
                child = SortCodeNode()
                node.children["terminal"] = child
                child.value = value
            return node
        if remaining[:1] in node.children:
            child = node.children[remaining[:1]]
        else:
            child = SortCodeNode()
            node.children[remaining[:1]] = child
            child.char = remaining[:1]
        return self.insert(child, remaining[1:], value)



    def lookup(self, sort_code):
        node = self.root
        best_match = None
        sort_code = sort_code.replace('-', '')

        for i, char in enumerate(sort_code):
            if char not in node.children:
                break
            node = node.children[char]
            if "terminal" in node.children and node.children["terminal"].value is not None:
                best_match = node.children["terminal"].value
        return best_match


    def _parse_range(self, sort_code):
        #if '-' in sort_code:
        parts = sort_code.split('-', 1)
        part = parts[0]
        if ".." in part:
            start, end = part.split("..")
        else:
            start = part
            end = part

        return start, end, parts[1] if len(parts) > 1 else ""


    def display_tree(self):
        def _display_node(node, prefix='', last=True):
            lines = []
            connector = '└── ' if last else '├── '
            lines.append(prefix + connector + self._node_to_string(node))

            new_prefix = prefix + ('    ' if last else '│   ')
            child_items = list(node.children.items())

            for i, (char, child) in enumerate(child_items):
                lines.extend(_display_node(child, new_prefix, i == len(child_items) - 1))

            return lines

        return '\n'.join(_display_node(self.root))

    def _node_to_string(self, node):
        parts = []
        if node.value:
            parts.append(f"Value: {node.value}")
        if node.char:
            parts.append(f"char {node.char}")
        return f"Node({', '.join(parts)})" if parts else "Node"


def create_sort_code_trie(sort_code_dict):
    trie = SortCodeTrie()
    for sort_code, value in sort_code_dict.items():
        trie.insert_sort_code(sort_code, value)
    return trie
