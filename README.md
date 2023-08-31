# vertex-pipeline-starter-kit
This is a very basic repo template for people to get started building Vertex pipelines. This is not suitable for prod.

## Usage

### Setup your local configuration
```shell
export PROJECT_ID=<gcp_project_id>
gcloud config set project $PROJECT_ID
gcloud auth login
gcloud auth application-default login
```

### Create some resources in the target GCP project
- Create a service account which will be used by pipelines.
  ```shell
  gcloud iam service-accounts create vertex
  ```
- Grant it the `Editor` role.
  ```shell
  gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:vertex@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/editor"
  ```
- Create a GCS bucket that Vertex pipelines will use to store artifacts under the hood.
  ```shell
  gcloud storage buckets create gs://vertex-$PROJECT_ID --location=europe-west1
  ```
- Initialize a Vertex base image on your project. While it builds, take a look at [this cloudbuild file](vertex/deployment/cloudbuild.yaml) to see what is inside the base image.
  ```shell
  make build_image
  ```
- In BigQuery create some sample data that will be used by our example pipeline.
  ```shell
  bq --location=europe-west1 mk --dataset $PROJECT_ID:vertex_dataset
  bq query --destination_table vertex_dataset.mytable --use_legacy_sql=false 'SELECT 1 AS one, 2 AS two'
  ```

### Run a pipeline
Running a pipeline is just like running a normal python file.

From the project root, run:
```shell
PYTHONPATH=. python vertex/pipelines/my_first_pipeline.py 
```

In the terminal you should see

```shell
Creating PipelineJob
PipelineJob created.
https://console.cloud.google.com/vertex-ai/locations/europe-west1/pipelines/runs/.......
PipelineState.PIPELINE_STATE_RUNNING
```

When you click on the console.cloud.google.com link it should direct you to GCP and you should be able to see the 
pipeline running. It will take few minutes to finish depending on your pipeline.

This pipeline will load the BigQuery table we created earlier, add a new column to it, and save it as a new table. Take a look at [the pipeline code](vertex/pipelines/my_first_pipeline.py) and at the [configuration file](vertex/configs/my_first_pipeline/conf_1.json) that is injected at compile time. 

When the pipeline has finished running successfully you should see in your terminal:
```shell
PipelineJob run completed.
```

## Why build pipelines _this_ way and not _that_ way?

[For Artefactors, go read the techdocs on Roadie to get a recap of why we chose to use Vertex like this.
](https://artefact.roadie.so/docs/default/Component/vertex-pipeline-starter-kit)

Otherwise, you can render the mkdocs locally:
```shell
mkdocs serve
```

## Repo organisation

```shell
.
├── vertex
│   ├── lib  # Python functions, classes, scripts, etc. These can be used in notebooks, components, and pipelines. All your business and implementation logic should be there
│   │   ├── connectors
│   │   │   └── bigquery.py
│   │   └── processors
│   │       └── transform_data.py
│   ├── components  # Vertex components. These should only wrap functions from lib with very minimal additional logic.
│   │   ├── load_data.py
│   │   ├── save_data.py
│   │   └── transform_data.py
│   ├── pipelines  # Vertex Pipelines allow you to orchestrate the execution of components and pass input/outputs between them. There is also code there to compile and launch pipelines from your local machine.
│   │   └── my_first_pipeline.py
│   ├── configs  # Global project and pipeline configurations and parameters.
│   │   └── my_first_pipeline
│   │       ├── config_1.json
│   │       └── config_2.json
│   └── deployment  # Builds the base docker image and makes it available for components.
│       ├── Dockerfile
│       └── cloudbuild.yaml
├── Makefile  # Shortcuts for repetitive commands
├── requirements-dev.txt  # Requirements for local pipeline development. Run `pip install -r requirements-dev.txt` to install everything.
├── requirements.txt  # Pipeline requirements.
└── README.md  # You are here.
```