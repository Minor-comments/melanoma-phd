import streamlit as st

from streamlit_app.AppLoader import AppLoader

if __name__ == "__main__":
    st.title("Clinical General Database")
    with AppLoader() as app:
        st.dataframe(app.database.general_clinical_database.dataframe)
