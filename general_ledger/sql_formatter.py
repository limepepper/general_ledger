import logging

from rich import inspect


def indent_string(text, indent=20):
    return "\n".join(" " * indent + line for line in text.splitlines())


class SQLFormatter(logging.Formatter):
    def format(self, record):

        if not hasattr(record, "sql"):
            return super().format(record)

        # Check if Pygments is available for coloring
        try:
            import pygments
            from pygments.lexers import SqlLexer
            from pygments.formatters import TerminalTrueColorFormatter
        except ImportError:
            pygments = None

        # Check if sqlparse is available for indentation
        try:
            import sqlparse
        except ImportError:
            sqlparse = None

        # Remove leading and trailing whitespaces
        sql = record.sql.strip()

        if sqlparse:
            # Indent the SQL query
            sql = sqlparse.format(sql, reindent=True)

        if pygments:
            # Highlight the SQL query
            sql = pygments.highlight(
                sql, SqlLexer(), TerminalTrueColorFormatter(style="default")
            )

        # Set the record's statement to the formatted query
        record.statement = indent_string(sql)
        if not hasattr(record, "duration"):
            record.duration = 0
        return super().format(record)
