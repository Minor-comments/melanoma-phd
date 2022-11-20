import os
import sys

import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app.AppLoader import AppLoader  # isort: skip <- Force to be after workaround


def reload_database(app: AppLoader):
    with st.spinner("Reloading database..."):
        app.database.reload()


def create_database_section(app: AppLoader):
    with st.expander(f"Database source file"):
        st.text(f"{app.database.file_info}")
        st.button(label="Reload", on_click=lambda app=app: reload_database(app))


if __name__ == "__main__":
    st.title("Melanoma PHD Statistics")
    with AppLoader() as app:
        create_database_section(app)
        st.subheader("General Clinical Base")
        st.dataframe(app.database.general_clinical_database.dataframe)
        st.subheader("Blood Parameters Base")
        st.dataframe(app.database.blood_parameters_database.dataframe)
        st.subheader("LF-DNA Populations Base")
        st.dataframe(app.database.lf_dna_populations_database.dataframe)
        st.subheader("Radiological Tests Base")
        st.dataframe(app.database.radiological_tests_database.dataframe)
        st.subheader("AP Ampliation Base")
        st.dataframe(app.database.ap_ampliation_database.dataframe)
