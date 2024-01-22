from kfp.dsl import component, Dataset,  Output
import os



# This is an example of a starting component that loads a table from BQ and saves it as a csv in vertex file system
# (included in GCS) so it can be used by next component
@component(base_image=f'europe-west1-docker.pkg.dev/{os.getenv("PROJECT_ID")}/vertex-pipelines-docker/vertex-pipelines-base:latest')
def load_data_component(
    project_id: str,
    gcp_region: str,
    input_table: str,
    df_dataset: Output[Dataset]
):
    from vertex.lib.connectors.bigquery import load_data_bq

    df = load_data_bq(project_id, gcp_region, input_table)

    # this is a vertex specific way of saving data so it is not included in load_data_bq function
    df.to_csv(df_dataset.uri, index=False)
