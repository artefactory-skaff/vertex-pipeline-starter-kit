import json
import os
from pathlib import Path
from typing import Dict

import kfp
from kfp.v2 import compiler
import google.cloud.aiplatform as aip


from vertex.components.load_data import load_data_component
from vertex.components.save_data import save_data_component
from vertex.components.transform_data import transform_data_component


# This is a pipeline that performs a simple ETL operation, adding a column to a BQ table with a default value
@kfp.dsl.pipeline(name="starter-pipeline")
def pipeline(
    project_id: str,

    input_table: str,
    output_table: str,

    new_column_name: str,
    new_column_value: str
):

    load_data_task = load_data_component(
        project_id=project_id,
        gcp_region="europe-west1",
        input_table=input_table,
    )

    transform_data_task = transform_data_component(
        df=load_data_task.outputs["df_dataset"],
        column_name=new_column_name,
        constant_value=new_column_value
    )

    save_data_component(
        df_transformed=transform_data_task.outputs["df_transformed_dataset"],
        project_id=PROJECT_ID,
        output_table=output_table
    )


def load_config(config_name: str) -> Dict:
    with open(Path(__file__).parent.parent / "configs" / "my_first_pipeline" / f"{config_name}.json") as f:
        config = json.load(f)
    return config


if __name__ == '__main__':
    PROJECT_ID = os.getenv("PROJECT_ID")
    SELECTED_CONFIGURATION = load_config("conf_1")
    PIPELINE_NAME = "my_first_vertex_pipeline"

    BUCKET_NAME = f"gs://artifact-vertex-template-264a"
    SERVICE_ACCOUNT = f"vertex@{PROJECT_ID}.iam.gserviceaccount.com"

    compiler.Compiler().compile(pipeline_func=pipeline, package_path="./pipeline.json")
    aip.init(project=PROJECT_ID, staging_bucket=BUCKET_NAME)

    job = aip.PipelineJob(
        display_name=PIPELINE_NAME,
        template_path="pipeline.json".replace(" ", "_"),
        pipeline_root=f"{BUCKET_NAME}/root",
        location="europe-west1",
        enable_caching=False,

        parameter_values={
            "project_id": PROJECT_ID,
            "input_table": SELECTED_CONFIGURATION["INPUT_TABLE"],
            "output_table": SELECTED_CONFIGURATION["OUTPUT_TABLE"],
            "new_column_name": SELECTED_CONFIGURATION["NEW_COLUMN_NAME"],
            "new_column_value": SELECTED_CONFIGURATION["NEW_COLUMN_VALUE"]
        },
    )

    job.run(service_account=SERVICE_ACCOUNT)
