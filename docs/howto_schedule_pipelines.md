Your business needs may require you to run your pipelines every month, week, or day. This is not directly supported in Vertex pipelines yet.

## Use the dedicated Skaff accelerator

https://artefact.roadie.so/catalog/default/component/scheduled-pipelines

## Do it yourself

Use Cloud Scheduler and a Cloud function to run a pre-compiled pipeline.

This is the GCP recommended way. Compile your pipelines locally or in your CI/CD, and store the json output somewhere on GCP. Set up a job on Cloud Scheduler to trigger a Cloud Function (or Cloud Run) to load a compiled pipeline and run it.

There is no Artefact accelerator for this at the moment, but one will be available some time soon™️.

[Follow the docs to deploy that yourself.](https://cloud.google.com/vertex-ai/docs/pipelines/schedule-cloud-scheduler)