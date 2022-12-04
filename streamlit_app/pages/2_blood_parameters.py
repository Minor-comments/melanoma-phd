import streamlit as st

from streamlit_app.AppLoader import AppLoader

if __name__ == "__main__":
    st.title("Blood Parameters Database")
    with AppLoader() as app:
        st.dataframe(app.database.blood_parameters_database.dataframe)
