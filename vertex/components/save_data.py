from kfp.v2.dsl import component, Dataset, Input
import os


@component(base_image=f'eu.gcr.io/{os.getenv("PROJECT_ID")}/vertex-pipelines-base:latest')
def save_data_component(
    df_transformed: Input[Dataset],
    project_id: str,
    output_table: str,
):
    import pandas as pd
    from vertex.lib.connectors.bigquery import save_data_bq

    df_transformed = pd.read_csv(df_transformed.uri)
    save_data_bq(df_transformed, project_id, output_table)
