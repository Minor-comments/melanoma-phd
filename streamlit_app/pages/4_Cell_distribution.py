import os
import sys
from typing import Dict, List

import streamlit as st

from melanoma_phd.visualizer.PiePlotter import PiePlotter
from melanoma_phd.visualizer.StackedHistogram import StackedHistogram

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # isort: skip <- Force to be after workaround
from streamlit_app.AppLoader import (
    AppLoader,
    create_database_section,
    filter_database,
    select_filters,
    select_group_by,
)


def get_variable_groups() -> Dict[str, List[str]]:
    return {
        "T(CD3+)/LB(CD19+)/NK(CD16/56+)": ["T(CD3+)({N})", "LB(CD19+)({N})", "NK(CD16/56+)({N})"],
        "CD4+/CD8+/DP/DN": ["T(CD3+CD4+)({N})", "T(CD3+CD8+)({N})", "DP ({N})", "DN ({N})"],
        "CTLA4+/PDL1+": ["CTLA4+({N})", "PDL1+({N})"],
        "naive/memoria/mem efectora/efectora": [
            "naïve(CD3+CCR7+CD45A+)({N})",
            "mem central(CD3+CCR7+CD45RO+)({N})",
            "efectora (CCR7-CD45RO-) ({N})",
            "mem efectora(CD3+CCR7-CD45RO+)({N})",
        ],
        "CD69+/HLA-DR+/CD40L+/CD25+/CD62L+": [
            "CD69+({N})",
            "HLA-DR+({N})",
            "CD40L+({N})",
            "CD25+({N})",
            "CD62L+({N})",
        ],
        "Treg vs no Treg": ["Treg(CD3+CD4+CD25+FOXP3)({N})"],
    }


if __name__ == "__main__":
    st.set_page_config(page_title="Melanoma PHD Statistics", layout="wide")
    st.title("Cell distribution")
    with AppLoader() as app:
        create_database_section(app)

        filters = select_filters(app)
        selected_group_by = select_group_by(app)
        df_result = filter_database(app=app, filters=filters)

        variable_names_to_plot = get_variable_groups()
        for group_name, variable_names in variable_names_to_plot.items():
            st.header(group_name)
            variables_to_plot = dict(
                (
                    app.database.get_variable(variable_name),
                    app.database.get_variable(variable_name).descriptive_statistics(
                        df_result, group_by=selected_group_by
                    ),
                )
                for variable_name in variable_names
            )
            st.pyplot(PiePlotter().plot(variable_statistics=variables_to_plot))
