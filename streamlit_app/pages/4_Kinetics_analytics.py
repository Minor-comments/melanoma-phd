import os
import sys
from typing import List

import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)  # isort: skip
from melanoma_phd.database.Patient import Patient
from melanoma_phd.database.PatientDatabaseView import PatientDatabaseView
from melanoma_phd.database.variable.IterationScalarVariable import IterationScalarVariable
from melanoma_phd.visualizer.KineticsPlotter import KineticsPlotter
from streamlit_app.AppLoader import (
    AppLoader,
    SelectVariableConfig,
    create_database_section,
    filter_database,
    select_filters,
    select_one_variable,
)


def select_patients(database_view: PatientDatabaseView) -> List[Patient]:
    with st.form("select_patients"):
        patient_ids = []
        selected_patient_ids = st.multiselect(
            label="Select a patient/s to display", options=database_view.patient_ids
        )
        if st.form_submit_button("Select"):
            patient_ids = selected_patient_ids
    return database_view.get_patients(patient_ids)


def plot_kinetics(variable: IterationScalarVariable, patients: List[Patient]) -> None:
    figure = KineticsPlotter().plot(variable, patients)
    st.pyplot(figure)


if __name__ == "__main__":
    st.set_page_config(page_title="Kinetics Analytics", layout="wide")
    st.title("Kinetics Analytics")
    with AppLoader() as app:
        database = app.database
        create_database_section(database)
        filters = select_filters(database)
        db_view = filter_database(database=database, filters=filters)
        variable = select_one_variable(
            database=database,
            select_variable_config=SelectVariableConfig(
                variable_selection_name="kinetics itreated variable",
                unique_title="Select iterated variable",
                variable_types=[IterationScalarVariable],
            ),
        )
        if variable:
            patients = select_patients(db_view)
            plot_kinetics(variable, patients)
        else:
            st.text("Select a variable to display :)")
