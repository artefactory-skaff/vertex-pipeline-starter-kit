import os
from typing import NamedTuple

import kfp
from kfp.v2 import compiler
import google.cloud.aiplatform as aip
from kfp.v2.dsl import component, Dataset,  Output, Input


from vertex.components.load_data import load_data_component
from vertex.components.save_data import save_data_component
from vertex.components.transform_data import transform_data_component

from vertex.lib.utils.config import load_config

@component(base_image=f'eu.gcr.io/{os.getenv("PROJECT_ID")}/vertex-pipelines-base:latest')
def load_training_data(project_id: str, gcp_region: str, input_table: str, training_data: Output[Dataset]):
    pass

@component(base_image=f'eu.gcr.io/{os.getenv("PROJECT_ID")}/vertex-pipelines-base:latest')
def train_and_evaluate(hyper_parameter: int, training_data: Input[Dataset]) -> NamedTuple("Outputs", [("result", int)]):
    from random import randint
    result = randint(0, 100)
    return (result, )

@component(base_image=f'eu.gcr.io/{os.getenv("PROJECT_ID")}/vertex-pipelines-base:latest')
def save_best_model(grid_search_results: list):
    pass


@component(base_image=f'eu.gcr.io/{os.getenv("PROJECT_ID")}/vertex-pipelines-base:latest')
def dummy_task():
    pass


@kfp.dsl.pipeline(name="divide-and-conquer")
def pipeline(project_id: str, input_table: str):
    first_task = dummy_task()

    parallel_tasks = []
    for _ in range(3):
        parallel_task = dummy_task()
        parallel_task.after(first_task)
        parallel_tasks.append(parallel_task)

    final_task = dummy_task()
    for task in parallel_tasks:
        final_task.after(task)


if __name__ == '__main__':
    PROJECT_ID = os.getenv("PROJECT_ID")
    SELECTED_CONFIGURATION = load_config("my_first_pipeline", "conf_1")
    PIPELINE_NAME = "my_first_vertex_pipeline"
    
    BUCKET_NAME = f"gs://vertex-{PROJECT_ID}"
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
            "input_table": "whatever"
        },
    )

    job.run(service_account=SERVICE_ACCOUNT)
