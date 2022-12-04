import streamlit as st

from streamlit_app.AppLoader import AppLoader

if __name__ == "__main__":
    st.title("AP Ampliation Database")
    with AppLoader() as app:
        st.dataframe(app.database.ap_ampliation_database.dataframe)
