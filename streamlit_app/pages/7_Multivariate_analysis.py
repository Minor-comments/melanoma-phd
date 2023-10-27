import os
import sys
from typing import List, Type, cast

import numpy as np
import pandas as pd
import streamlit as st

# workaround for Streamlit Cloud for importing `melanoma_phd` module correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # isort: skip
from melanoma_phd.database.statistics.CatboostModel import CatboostModel
from melanoma_phd.database.statistics.PreProcessor import NanTreatment, PreProcessor
from melanoma_phd.database.variable.BaseVariable import BaseVariable
from melanoma_phd.database.variable.CategoricalVariable import CategoricalVariable
from melanoma_phd.database.variable.ScalarVariable import ScalarVariable
from melanoma_phd.visualizer.RocAucPlotter import RocAucPlotter
from streamlit_app.AppLoader import (
    AppLoader,
    SelectVariableConfig,
    create_database_section,
    filter_database_section,
    select_filters_sidebar,
    select_several_variables_by_checkbox,
)


def concat_variables(
    df: pd.DataFrame, variables: List[BaseVariable], variable_type: Type[BaseVariable]
) -> pd.DataFrame:
    variables_data = [
        variable.get_series(df) for variable in variables if isinstance(variable, variable_type)
    ]
    if len(variables_data) > 0:
        return pd.concat(
            variables_data,
            axis=1,
        )
    else:
        return pd.DataFrame(None, index=df.index)


if __name__ == "__main__":
    st.set_page_config(page_title="Melanoma PHD Statistics", layout="wide")
    st.title("Multivariate Analysis")
    with AppLoader() as app:
        database = app.database
        create_database_section(database)

        filters = select_filters_sidebar(database)
        db_view = filter_database_section(database=database, filters=filters)
        filtered_df = db_view.dataframe

        st.subheader("Variable selection")
        independent_variables, target_variables = select_several_variables_by_checkbox(
            database,
            SelectVariableConfig(
                variable_selection_name="Independent variables",
                unique_form_title="Variables used for multivariate analysis",
                variable_types=[ScalarVariable, CategoricalVariable],
            ),
            SelectVariableConfig(
                variable_selection_name="Target variables",
                unique_form_title="Varibles to make analysis on",
                variable_types=[
                    ScalarVariable,
                    CategoricalVariable,
                ],
            ),
        )

        N_FOLDS = 5
        SEED = 42

        st.subheader("Training options")
        N_FOLDS = st.slider("Number of folds", value=5, min_value=1, max_value=10)
        SEED = st.slider("Seed", value=42, min_value=1, max_value=100)
        iterations = st.slider("Number of iterations", value=300, min_value=1, max_value=5000)
        depth = st.slider("Depth", value=3, min_value=1, max_value=10)
        od_pval = st.select_slider(
            "Overfit detector - p-value", options=np.logspace(-10, 2, 12, base=10), value=0.001
        )
        od_wait = st.slider(
            "Overfit detector - wait iterations", value=50, min_value=1, max_value=500
        )

        model_params = dict(
            od_pval=od_pval,
            od_wait=od_wait,
            iterations=iterations,
            depth=depth,
            eval_metric="AUC",
        )

        if independent_variables and target_variables:
            preprocessor = PreProcessor(
                transform_floats=True,
                substring_transform_columns=["Fluo", "Abs", "Tcm/Teff", "Teff/Treg", "EDAD"],
            )

            numerical_independent_df = preprocessor.preprocess(
                concat_variables(filtered_df, independent_variables, ScalarVariable)
            )
            categorical_independent_df = preprocessor.preprocess(
                concat_variables(filtered_df, independent_variables, CategoricalVariable),
                nan_treatment=NanTreatment.KEEP_AS_VALID_VALUE,
            )
            independent_df = pd.concat(
                [numerical_independent_df, categorical_independent_df], axis=1, join="inner"
            )

            for target_variable in target_variables:
                target_variable = cast(CategoricalVariable, target_variable)
                target_series = target_variable.get_series(filtered_df)
                target_df = preprocessor.preprocess(
                    pd.DataFrame(target_series, index=target_series.index),
                    nan_treatment=NanTreatment.DROP,
                )
                target_df = pd.DataFrame(
                    target_variable.get_numeric(
                        target_df.iloc[:, 0], categories=target_variable.categories
                    ),
                    index=target_df.index,
                )
                model = CatboostModel(
                    kfolds=N_FOLDS,
                    random_state=SEED,
                    categorical_independent_columns=list(categorical_independent_df.columns),
                    **model_params,
                )
                results = model.fit(
                    independent_df=independent_df,
                    target_df=target_df,
                )

                st.header(f"Multivariate analysis for {target_variable.name}")

                st.subheader(f"Metrics")
                st.write(f"Using {N_FOLDS} folds with num samples: {len(target_df)}")
                # st.write(results.metrics.style.apply(lambda x: f"{x:.3%}"))
                st.write(results.metrics)

                roc_auc_plotter = RocAucPlotter()
                st.plotly_chart(roc_auc_plotter.plot(results=results))

                st.divider()

                st.subheader(f"Feature Importance")
                st.bar_chart(results.feature_importance)
                st.write(results.feature_importance)
                st.divider()

                st.subheader(f"Probabilities")
                results.probabilities.columns = [
                    target_variable.get_category_name(column)
                    for column in results.probabilities.columns
                ]
                st.write(results.probabilities)
