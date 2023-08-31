import os

import kfp
from kfp.v2 import compiler
import google.cloud.aiplatform as aip
from kfp.v2.dsl import component


@component(base_image="python3.9")
def dummy_task():
    pass


@kfp.dsl.pipeline(name="parametrized-pipeline")
def pipeline(config_name: str):
    pass


if __name__ == '__main__':
    PROJECT_ID = os.getenv("PROJECT_ID")
    PIPELINE_NAME = "parametrized-pipeline"
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
            "country": "france",
            "start_date": "2022-01-01",
            "end_date": "2022-12-31"
        },
    )

    job.run(service_account=SERVICE_ACCOUNT)
