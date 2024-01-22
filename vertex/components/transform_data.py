from kfp.dsl import component, Dataset, Input, Output
import os

# This is a component add a constant column to pandas dataframe
# This is an example of intermediary component that loads data from a previous component and saves data for next one.
@component(base_image=f'eu.gcr.io/{os.getenv("PROJECT_ID")}/vertex-pipelines-base:latest')
def transform_data_component(
    df: Input[Dataset],
    column_name: str,
    constant_value: str,
    df_transformed_dataset: Output[Dataset]
):
    import pandas as pd
    from vertex.lib.processors.transform_data import add_constant_column

    # this is a vertex specific way of loading data so it is not included in add_constant_column function
    df = pd.read_csv(df.uri)

    df_transformed = add_constant_column(df, column_name, constant_value)

    # this is a vertex specific way of saving data so it is not included in add_constant_column function
    df_transformed.to_csv(df_transformed_dataset.uri, index=False)



