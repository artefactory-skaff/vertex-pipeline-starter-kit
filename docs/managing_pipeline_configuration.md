It is a very good practice to make your pipeline parameterizable. That means replacing all hardcoded values by variables that you are going to pass to the pipeline and eventually to the components.

Examples of pipeline parameters:

- Model training parameters
- Start date and end date of the data you want to work with
- Product categories
- Geography (country, region, stores, ...)
- Customer segments
- ...

Leveraging parametrized pipelines will allow you to run the same pipeline with different parameter sets. This is much more practical to deploy than multiple pipelines with slightly different hardcoded values.

The number of configurations and parameters can get substantial, so how do you properly manage them?

## Passing config values to the pipeline

### Basic pipeline parametrization
In most cases, just passing values to your pipeline as parameters is the simplest and best way to go.

````python3
import os

import kfp
from kfp.v2 import compiler
import google.cloud.aiplatform as aip
from kfp.v2.dsl import component


@component(base_image=f'eu.gcr.io/{os.getenv("PROJECT_ID")}/vertex-pipelines-base:latest')
def dummy_task(project_id: str, country: str, start_date: str, end_date: str):
    pass


# Pipeline and its parameters are defined here
@kfp.dsl.pipeline(name="parametrized-pipeline")
def pipeline(project_id: str, country: str, start_date: str, end_date: str):
    dummy_task(
        project_id=project_id,
        country=country,
        start_date=start_date,
        end_date=end_date
    )


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
        
        # Parameters values are passed from here to the pipeline
        parameter_values={
            "project_id": PROJECT_ID,
            "country": "france",
            "start_date": "2022-01-01",
            "end_date": "2022-12-31"
        },
    )

    job.run(service_account=SERVICE_ACCOUNT)
````

The parameters will be clearly displayed in the UI:
![](assets/parametrized_pipeline.png)

### Dynamically loading pipeline parameters

!!! warning "Dynamically loading a config in the pipeline"

    Unfortunately, pipeline parameters values are rendered when passed to components. That means you can not easily load configuration in the pipeline body.
    
    ````python3
    @kfp.dsl.pipeline(name="parametrized-pipeline")
    def pipeline(config_name: str):
        print(config_name)  # Result: {{pipelineparam:op=;name=config_name}} -> not rendered
    ````

    You would need a dedicated component to load your configuration and then output the values to downstream tasks. At this point it becomes too complex for no benefits and is not worth it.

!!! example "Instead, load the values before compiling the pipeline"

    ````python3
    job = aip.PipelineJob(
        display_name=PIPELINE_NAME,
        template_path="pipeline.json".replace(" ", "_"),
        pipeline_root=f"{BUCKET_NAME}/root",
        location="europe-west1",
        enable_caching=False,

        parameter_values={**load_config("config_1")},
    )
    ````

    ??? note "`load_config` function"
        
        ````python3
        def load_config(config_name: str) -> Dict:
            with open(Path(__file__).parent.parent.parent / "configs" / f"{config_name}.json") as f:
                config = json.load(f)
            return config
        ````

    ??? note "`config_1.json`"
        
        ````json
        {
          "project_id": "ocmlf-vial-16",
          "country": "france",
          "start_date": "2022-01-01",
          "end_date": "2022-12-31"
        }
        ````

## Storing configs