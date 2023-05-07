import csv
import io
from typing import Any, List

from streamlit_app.table.VariableTable import VariableTable


class CsvTable:
    def __init__(self, variable_table: VariableTable) -> None:
        self._variable_table = variable_table

    def dumps(self) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(self.__variable_rows())
        return output.getvalue()

    def to_file(self, file_path: str) -> None:
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(self.__variable_rows())

    def __variable_rows(self) -> List[List[Any]]:
        return [variable_row for row in self._variable_table.rows() for variable_row in row]
