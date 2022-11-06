import os
import sys

import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from melanoma_phd.MelanomaPhdApp import MelanomaPhdApp, create_melanoma_phd_app


@st.experimental_singleton(show_spinner="Loading the main app...")
def load_app() -> MelanomaPhdApp:
    return create_melanoma_phd_app()


if __name__ == "__main__":
    st.title("Melanoma PHD Statistics")
    app = load_app()
    st.subheader("General Clinical Base")
    st.dataframe(app.database.general_clinical_base)
    st.subheader("Blood Parameters Base")
    st.dataframe(app.database.blood_parameters_base)
    st.subheader("LF-DNA Populations Base")
    st.dataframe(app.database.lf_dna_populations_base)
    st.subheader("Radiological Tests Base")
    st.dataframe(app.database.radiological_tests_base)
    st.subheader("AP Ampliation Base")
    st.dataframe(app.database.ap_ampliation_base)
