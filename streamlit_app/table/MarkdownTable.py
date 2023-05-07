from typing import List

from streamlit_app.table.VariableTable import VariableTable


class MarkdownTable:
    def __init__(self, variable_table: VariableTable) -> None:
        self._variable_table = variable_table

    def dumps(self) -> str:
        rows: List[str] = []
        max_column_count = 0
        highlight_rows = []
        for index, variable_rows in enumerate(self._variable_table.rows()):
            if index % 2 == 0:
                highlight_rows.extend(
                    list(range(len(rows) + 1, len(rows) + 1 + len(variable_rows)))
                )
            for row in variable_rows:
                rows.append(f"| {'|'.join(list(map(lambda row_value : str(row_value), row)))} |")
                if len(row) > max_column_count:
                    max_column_count = len(row)
        table = [
            f"|{' | ' * (max_column_count-1)}|",
            f"|{'--|--' * (max_column_count-1)}|",
        ]
        table.extend(rows)
        return (
            f"<style> {''.join(['tr:nth-child(' + str(index) + ' ) { background-color: #6b6b6b!important; }' for index in highlight_rows])}</style>\n"
            + "\n".join(table)
        )
