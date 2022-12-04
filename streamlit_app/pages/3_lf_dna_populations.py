import streamlit as st

from streamlit_app.AppLoader import AppLoader

if __name__ == "__main__":
    st.title("LF_DNA Populations Database")
    with AppLoader() as app:
        st.dataframe(app.database.lf_dna_populations_database.dataframe)
