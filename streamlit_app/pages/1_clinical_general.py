import streamlit as st

from melanoma_phd.data_processor.PatientDataFilterer import PatientDataFilterer
from melanoma_phd.data_processor.PatientFilter import PatientFilter
from melanoma_phd.database.variable.PopulationGroup import PopulationGroup
from melanoma_phd.database.variable.TreatmentType import TreatmentType
from streamlit_app.AppLoader import AppLoader


def generate_patient_filter() -> PatientDataFilterer:
    filter = PatientFilter()
    with st.sidebar.form("Patients Filter"):
        population_groups = st.multiselect(
            "Population Group",
            [entry.option_name for entry in PopulationGroup],
        )
        treatment_types = st.multiselect(
            "Current Treatment",
            [entry.option_name for entry in TreatmentType],
        )
        st.form_submit_button("Filter")

        filter.population_groups = [
            entry for entry in PopulationGroup if entry.option_name in population_groups
        ]
        filter.current_treatment_types = [
            entry for entry in TreatmentType if entry.option_name in treatment_types
        ]
    return filter


if __name__ == "__main__":
    st.title("Clinical General Database")
    with AppLoader() as app:
        filter = generate_patient_filter()
        df_result = PatientDataFilterer().filter(
            app.database.general_clinical_database.dataframe, filter
        )
        st.dataframe(df_result)
        st.header("Descriptive Statistcs")
        for variable in app.database.general_clinical_database.variables_to_analyze:
            st.text(variable.name)
            st.dataframe(variable.descriptive_statistics(df_result))
