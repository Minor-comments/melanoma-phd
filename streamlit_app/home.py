import os
import sys

import streamlit as st

from streamlit_app.AppLoader import AppLoader

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


if __name__ == "__main__":
    st.title("Melanoma PHD Statistics")
    with AppLoader() as app:
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
