import streamlit as st

from streamlit_app.AppLoader import AppLoader

if __name__ == "__main__":
    st.title("Radiological Test Database")
    with AppLoader() as app:
        st.dataframe(app.database.radiological_tests_database.dataframe)
