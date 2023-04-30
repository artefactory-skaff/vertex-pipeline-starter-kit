import json
import os
from pathlib import Path
from typing import Dict

import kfp
from kfp.v2 import compiler
import google.cloud.aiplatform as aip
from kfp.v2.dsl import component


@component(base_image=f'eu.gcr.io/{os.getenv("PROJECT_ID")}/vertex-pipelines-base:latest')
def dummy_task(project_id: str, country: str, start_date: str, end_date: str):
    pass


@kfp.dsl.pipeline(name="parametrized-pipeline")
def pipeline(project_id: str, country: str, start_date: str, end_date: str):
    dummy_task(
        project_id=project_id,
        country=country,
        start_date=start_date,
        end_date=end_date
    )


def load_config(config_name: str) -> Dict:
    with open(Path(__file__).parent.parent / "configs" / f"{config_name}.json") as f:
        config = json.load(f)
    return config


if __name__ == '__main__':
    PROJECT_ID = os.getenv("PROJECT_ID")
    PIPELINE_NAME = "parametrized-pipeline"
    BUCKET_NAME = f"gs://vertex-artifacts"
    SERVICE_ACCOUNT = f"vertex@{PROJECT_ID}.iam.gserviceaccount.com"

    compiler.Compiler().compile(pipeline_func=pipeline, package_path="./pipeline.json")
    aip.init(project=PROJECT_ID, staging_bucket=BUCKET_NAME)

    job = aip.PipelineJob(
        display_name=PIPELINE_NAME,
        template_path="pipeline.json".replace(" ", "_"),
        pipeline_root=f"{BUCKET_NAME}/root",
        location="europe-west1",
        enable_caching=False,

        parameter_values={**load_config("config_1")},
    )

    job.run(service_account=SERVICE_ACCOUNT)
