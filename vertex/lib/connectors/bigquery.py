import os

from google.cloud import bigquery
import pandas_gbq
import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
import logging


def save_data_bq(df, project_id, output_table, bq_table_schema=None):

    pandas_gbq.to_gbq(
        df,
        output_table,
        if_exists="replace",
        project_id=project_id,
        table_schema=bq_table_schema,
        api_method="load_csv"
    )
    logging.info(f"saved_data_in {output_table}")


def load_data_bq(project_id, gcp_region, input_table):
    query = f"""
    SELECT * FROM `{project_id}.{input_table}`
    """
    client = bigquery.Client(location=gcp_region, project=project_id)
    df = client.query(query, location=gcp_region).to_dataframe()
    logging.info(f"Size of df: {df.shape}")
    return df


if __name__ == '__main__':
    # You can run this code locally to quickly iterate
    load_data_bq(
        project_id=os.getenv("PROJECT_ID"),
        gcp_region="europe-west1",
        input_table="vertex.my-table"
    )
