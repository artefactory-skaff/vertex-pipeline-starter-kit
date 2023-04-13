from kfp.v2.dsl import component, Dataset, Input, Output
import os


@component(base_image=f'eu.gcr.io/{os.getenv("PROJECT_ID")}/vertex-pipelines-base:latest')
def transform_data_component(
    df: Input[Dataset],
    column_name: str,
    constant_value: str,
    df_transformed_dataset: Output[Dataset]
):
    import pandas as pd
    from vertex.lib.processors.transform_data import add_constant_column

    df = pd.read_csv(df.uri)
    df_transformed = add_constant_column(df, column_name, constant_value)
    df_transformed.to_csv(df_transformed_dataset.uri, index=False)



