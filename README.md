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
- Create a service account which will be used by pipelines. Grant it the `Editor` role.
- Create a GCS bucket that Vertex pipelines will use.
- Enter the correct bucket and SA names in `vertex/pipelines/my_first_pipeline.py`
- Run `make build_image` to initialize a Vertex base image on your project.
- In BigQuery create some sample data that will be used by our example pipeline.
  - Create a dataset
    - `bq --location=EU mk --dataset $PROJECT_ID:vertex_dataset`
  - Create a dummy table with some sample data
    - `bq query --destination_table vertex_dataset.mytable --use_legacy_sql=false 'SELECT 1 AS one, 2 AS two'`
- Edit `conf_1.json` with your new dataset and tables

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

When the pipeline has finished running successfully you shoudl see in your terminal:
```shell
PipelineJob run completed.
```

## Explainations

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