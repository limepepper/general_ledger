import copy

from general_ledger.render.formats_abc import StatementFormat
from general_ledger.statements.financial_statement import FinancialStatement
from general_ledger.statements.meta import DetailLevel
from general_ledger.utils.utility import visit_logger

from loguru import logger

logger = logger.opt(colors=True)


class StatementFormatRichTable(StatementFormat):
    def render_statement(self, renderer, node):
        print("Rendering statement with Rich Table")
        node.meta.expand = DetailLevel.EXPAND
        node.set_expand(DetailLevel.EXPAND)

        result = node.accept(NodeTableVisitor("Financial Statement Example 1")).render()
        # result.render()
        renderer.renderable = result
        return result


class NodeTableVisitor:

    fs: FinancialStatement = None

    def __init__(
        self,
        name,
    ):
        self.name: str = name
        self.fs = FinancialStatement(name)
        self.current_level = 0

    # @logger_wraps()
    def visit(self, node, *_) -> FinancialStatement:
        self.visit_node(node)
        return self.fs

    def visit_node(self, node):
        visit_logger(
            logger,
            f"Processing '{node.name}' {node.meta.expand} depth: {node.depth} ",
            node,
            self.current_level,
        )
        self.visit_node_header(node)
        self.visit_node_body(node)
        self.visit_node_footer(node)

    def visit_node_header(self, node):
        if node.is_leaf or node.meta.expand == DetailLevel.VALUE:
            return
        self.fs.add_value(
            node.label,
            "-",
            col_idx=self.current_level,
            node_type=FinancialStatement.Type.HEADER,
            indent=self.current_level,
            node=node,
            extra=copy.deepcopy(self.fs.used_columns),
        )

    def visit_node_footer(self, node):
        if node.is_leaf or node.meta.expand == DetailLevel.VALUE:
            return
        self.fs.add_value(
            node.label,
            "-",
            col_idx=self.current_level,
            node_type=FinancialStatement.Type.FOOTER,
            indent=self.current_level,
            node=node,
            extra=f"value: {node.value} accum: {node.accumulated_value}",
        )

    def visit_leaf(self, node):
        self.fs.add_value(
            node.label,
            node.value,
            col_idx=self.current_level,
            node_type=FinancialStatement.Type.LEAF,
            indent=self.current_level,
            node=node,
        )
        return self.fs

    def visit_node_body(self, node):

        # choose available column
        first = False if self.fs.counts[self.current_level] else True
        count = self.fs.counts[self.current_level]

        visit_logger(
            logger,
            f"before columns: {self.fs.used_columns} {count} {first} xxx",
            node,
            self.current_level,
        )

        original_current_level = self.current_level
        next_level = self.current_level

        if node.is_leaf or node.meta.expand == DetailLevel.VALUE:
            self.visit_leaf(node)
            return

        if not self.fs.used_columns[self.current_level]:
            """if the level is unused we can use it for our children"""
            self.fs.used_columns[self.current_level] = [node.name]
            next_level = self.current_level
        elif self.fs.used_columns[self.current_level] and first:
            self.fs.used_columns[self.current_level].append(node.name)
            next_level = self.current_level
        else:
            """if the level is used we need to move to the next level
            and record that we used the current level"""
            next_level = self.current_level + 1
            self.fs.used_columns[next_level].append(node.name)

        visit_logger(
            logger,
            f"after columns: {self.fs.used_columns} {count} {first}",
            node,
            self.current_level,
        )
        self.current_level = next_level
        for i, child in enumerate(node.values()):
            is_first = i == 0
            is_last = i == len(node) - 1
            self.visit(child)
            if is_last:
                """if we are the end of list of children. can draw a line"""
                self.fs.add_value(
                    "",
                    "---------",
                    col_idx=self.current_level,
                    node_type=FinancialStatement.Type.RUNNING,
                    indent=self.current_level,
                    node=child,
                    extra=[
                        "",
                        f"value: {child.value} total: {node.sections.value}",
                    ],
                )
        self.current_level = original_current_level
        node_type = (
            FinancialStatement.Type.SUBTOTAL
            if node.parent
            else FinancialStatement.Type.TOTAL
        )
        self.fs.add_value(
            node.label,
            # node.sections.value if node.has_children else node.value,
            node.operation.calculate(node),
            col_idx=self.current_level,
            node_type=node_type,
            indent=self.current_level,
            node=node,
            extra=[
                copy.deepcopy(self.fs.used_columns),
                f"value: {node.value} accum: {node.accumulated_value}",
            ],
        )

        if node.name in self.fs.used_columns[next_level]:
            self.fs.used_columns[next_level].remove(node.name)
        self.current_level = original_current_level
