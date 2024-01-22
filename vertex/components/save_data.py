from kfp.dsl import component, Dataset, Input
import os

# This is an example of an example of final component that saves data into a specific storage system (here a BQ table)
@component(base_image=f'eu.gcr.io/{os.getenv("PROJECT_ID")}/vertex-pipelines-base:latest')
def save_data_component(
    df_transformed: Input[Dataset],
    project_id: str,
    output_table: str,
):
    import pandas as pd
    from vertex.lib.connectors.bigquery import save_data_bq

    # this is a vertex specific way of loading data so it is not included in save_data_bq function
    df_transformed = pd.read_csv(df_transformed.uri)

    # saving data into BQ, note that contrarily to other components we are not using the vertex specific file system
    # for saving our data
    save_data_bq(df_transformed, project_id, output_table)
