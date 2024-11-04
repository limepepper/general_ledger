from general_ledger.render.formats_abc import StatementFormat
from general_ledger.statements.meta import DetailLevel
from util.visitors.recursive_func import RecursiveFuncVisitor


class StatementFormatJ2(StatementFormat):
    def render_statement(self, renderer, node):
        print("Rendering statement with Jinja templates")
        node.meta.expand = DetailLevel.EXPAND
        node.set_expand(DetailLevel.EXPAND)

        result = "".join(
            node.accept(
                RecursiveFuncVisitor(
                    pre_func=self.pre_func,
                    post_func=self.post_func,
                )
            )
        )
        # result.render()
        renderer.renderable = result
        return result

    def pre_func(self, node, level, *_, **__):
        out = ""
        out += f'<div class="node-container node-level-{node.depth+3}">'
        out += f'<h1 class="node-title">{node.title}</h1>'
        out += f"<div>"
        out += f'<p class="node-value">{node.value}</p><span>{level}</span>'
        padding = 20 * level
        out += f'<div class="node-content" style="padding-left: {padding}px;">'
        return out

    def post_func(self, node, *_, **__):
        out = ""
        out += f'</div><div class="node-end">end of {node.name}</div></div></div>'
        return out


# class NodeHtmlVisitor(RecursiveFuncVisitor):
#     def visit(self, node):
#         return node.accept
