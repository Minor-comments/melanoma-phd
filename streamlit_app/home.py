import os
import sys
from datetime import datetime
from itertools import islice
from typing import Any, Dict, Iterable, Iterator

import pandas as pd
import streamlit as st

from melanoma_phd.database.variable.BaseVariable import BaseVariable

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app.AppLoader import AppLoader  # isort: skip <- Force to be after workaround
from melanoma_phd.database.filter.PatientDataFilterer import (
    PatientDataFilterer,
)  # isort: skip <- Force to be after workaround
from melanoma_phd.database.variable.BooleanVariable import BooleanVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from streamlit_app.AppLoader import create_database_section, select_filters, select_variables
from streamlit_app.table.CsvTable import CsvTable
from streamlit_app.table.MarkdownTable import MarkdownTable
from streamlit_app.table.VariableTable import VariableTable


def batched_dict(iterable: Dict[Any, Any], chunk_size: int) -> Iterator[Any]:
    iterator = iter(iterable)
    for i in range(0, len(iterable), chunk_size):
        yield {key: iterable[key] for key in islice(iterator, chunk_size)}


def download_statistics(variables_statistics: Dict[BaseVariable, pd.DataFrame]):
    table = VariableTable(variables_statistics)
    csv_creator = CsvTable(table)
    csv_contents = csv_creator.dumps()
    file_name = "descriptive_statistics" + datetime.now().strftime("%d/%m/%Y_%H:%M:%S") + ".csv"
    st.download_button(label="Download as CSV ⬇️ ", data=csv_contents, file_name=file_name)


def plot_statistics(variables_statistics: Dict[BaseVariable, pd.DataFrame]):
    MAX_VARIABLES_TABLE = 100
    for variables_statistics_chunk in batched_dict(variables_statistics, MAX_VARIABLES_TABLE):
        table = VariableTable(variables_statistics_chunk)
        markdown_table = MarkdownTable(table)
        st.markdown(markdown_table.dumps(), unsafe_allow_html=True)
        if len(variables_statistics) > MAX_VARIABLES_TABLE:
            st.markdown(
                f"📃 :orange[Only displaying the first {MAX_VARIABLES_TABLE} variables for performance issues.]"
            )
        return


if __name__ == "__main__":
    st.set_page_config(page_title="Melanoma PHD Statistics", layout="wide")
    st.title("Melanoma PHD Statistics")
    with AppLoader() as app:
        create_database_section(app)

        filters = select_filters(app)
        st.subheader("Filtered data")
        with st.expander(f"Filtered dataframe"):
            df_result = PatientDataFilterer().filter(app.database, filters)
            st.text(f"{len(df_result.index)} patients match with selected filters")
            st.dataframe(df_result)

        st.subheader("Variable selection")
        selected_variables = select_variables(
            app, variable_types=[ScalarVariable, CategoricalVariable, BooleanVariable]
        )
        st.header("Descriptive Statistcs")
        if selected_variables:
            variables_statistics = {}
            for variable in selected_variables:
                variables_statistics[variable] = variable.descriptive_statistics(df_result)

            download_statistics(variables_statistics)
            plot_statistics(variables_statistics)
        else:
            st.text("Select variables to analyze :)")
