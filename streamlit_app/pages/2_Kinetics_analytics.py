import os
import sys

import pandas as pd
import streamlit as st

from melanoma_phd.database.variable.BaseVariable import BaseVariable

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from melanoma_phd.database.PatientDatabase import PatientDatabase

from streamlit_app.AppLoader import AppLoader  # isort: skip <- Force to be after workaround


def select_patient(database: PatientDatabase) -> pd.DataFrame:
    with st.container():
        patient_id = st.selectbox(label="Select a patient", options=database.patient_ids)
        return database.get_patient_dataframe(patient_id)


if __name__ == "__main__":
    st.title("Kinetics Analytics")
    with AppLoader() as app:
        st.dataframe(select_patient(app.database))
