import pandas as pd
import plotly.express as px
import streamlit as st

from melanoma_phd.data_processor.PatientDataFilterer import PatientDataFilterer
from melanoma_phd.data_processor.PatientFilter import PatientFilter
from melanoma_phd.database.PopulationGroup import PopulationGroup
from streamlit_app.AppLoader import AppLoader


def generate_patient_filter() -> PatientDataFilterer:
    filter = PatientFilter()
    with st.sidebar.form("Patients Filter"):
        population_groups = st.multiselect(
            "Population Group",
            [entry.name for entry in PopulationGroup],
        )
        st.form_submit_button("Filter")
        filter.population_groups = [
            entry for entry in PopulationGroup if entry.name in population_groups
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
        for variable in app.database.general_clinical_database.variables_to_analyze:
            label_column_name = variable.name
            label_column_name_labels = f"{label_column_name}_labels"
            new_df = pd.DataFrame()
            new_df[label_column_name_labels] = (
                df_result[label_column_name].dropna().apply(lambda x: variable.get_category_name(x))
            )
            fig = px.pie(
                new_df,
                values=[1] * len(new_df.index),
                names=new_df[label_column_name_labels],
            )
            fig.update_traces(textposition="auto", texttemplate="%{label}<br>%{value} (%{percent})")
            fig.update_layout(showlegend=False)
            fig.update_layout(title="Sexo")
            st.plotly_chart(fig, use_container_width=True)
