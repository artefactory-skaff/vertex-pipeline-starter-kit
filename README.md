# vertex-pipeline-starter-kit
This is a very basic repo template for people to get started building Vertex pipelines. This is not suitable for prod.

# Vertex pipelines

## Repo organisation

```shell
.
├── lib  # Python functions, classes, scripts, etc. These can be used in notebooks, components, and pipelines. All your business and implementation logic should be there
│   ├── bq_connectors.py
│   └── transform_data.py
├── components  # Vertex components. These should only wrap functions from lib with very minimal additional logic.
│   └── template
│       ├── load_data.py
│       ├── save_data.py
│       └── transform_data.py
├── pipelines  # Vertex Pipelines allow you to orchestrate the execution of components and pass input/outputs between them. There is also code there to compile and launch pipelines from your local machine.
│   └── template_pipeline.py
├── configs  # Global project and pipeline configurations and parameters.
│   ├── general_config.py
│   └── template
│       └── configs.py
├── deployment  # Builds the base docker image and makes it available for components.
│   ├── Dockerfile
│   └── cloudbuild.yaml
├── Makefile  # Shortcuts for repetitive commands
├── requirements-dev.txt  # Requirements for local pipeline development. Run `pip install -r requirements-dev.txt` to install everything.
├── requirements.txt  # Pipeline requirements.
└── README.md  # You are here.
```

## Usage

### Setup your GCP project configuration
```shell
export PROJECT_ID=<gcp_project_id>
gcloud config set project $PROJECT_ID
gcloud auth login
gcloud auth application-default login
```

### 🚧 Create some GCP resources
- Create a service account # TODO: specify permissions
- Create a GCS bucket for Vertex
- Enter the correct bucket and SA names in `vertex/pipelines/my_first_pipelie.py`
- Run `make build_image` to initialize a Vertex base image on your project.
- Create sample data in BQ

### Run a pipeline
Running a pipeline is just like running a normal python file.

From the project root, run:
```shell
PYTHONPATH=. python vertex/pipelines/template_pipeline.py 
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
