# Handling Vertex AI Pipelines Failures

In Vertex AI Pipelines, failures can occur during the execution of a pipeline. To handle these failures, you can use Exit Handlers.

## Exit Handlers

Official documentation for Exit Handlers is available [here](https://www.kubeflow.org/docs/components/pipelines/v2/pipelines/control-flow/#exit-handling-dslexithandler).

Exit Handlers are special steps that are executed whenever a pipeline exits, regardless of whether the pipeline’s steps have completed successfully or have failed.
You can use them to  send notifications, or perform any other action that you want to occur when a pipeline exits with a certain status (e.g. failure).

Here is an example of how to use Exit Handlers:

```python
import kfp.dsl

@kfp.dsl.pipeline(name="my-pipeline")
def my_pipeline():

    my_exit_task = ...  # Define your exit task here. (instanciated component)

    with kfp.dsl.ExitHandler(my_exit_task, name="Exit Handler"):
        # Add your pipeline tasks here.
```

## Sending Notifications

### Email notification using `VertexNotificationEmailOp`

Official documentation for this component is available [here](https://cloud.google.com/vertex-ai/docs/pipelines/email-notifications).

Vertex AI Pipelines provides a built-in component to send email notifications.
This component is called `VertexNotificationEmailOp`.
It is available in the `google_cloud_pipeline_components` package.
You can use it as an exit handler in your pipeline to send email notifications when the pipeline exits.

```python
import kfp.dsl
from google_cloud_pipeline_components.v1.vertex_notification_email import VertexNotificationEmailOp

@kfp.dsl.pipeline(name="my-pipeline")
def my_pipeline():

    notification_email_task = VertexNotificationEmailOp(recipients=["john.doe@foo-bar.com"])

    with kfp.dsl.ExitHandler(notification_email_task, name="Exit Handler"):
        # Add your pipeline tasks here.
```

### Slack notification using custom component

You can also use a custom component to send notifications.
Here is an example of a custom component that sends a notification to a Slack channel when a pipeline job ends.

!!! success "Prerequisites"
    To use this component, you need:
    - to create a Slack app and a Slack webhook URL. Official documentation for this is available [here](https://api.slack.com/messaging/webhooks).
    - to create a secret in Secret Manager containing the Slack webhook URL. Official documentation for this is available [here](https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets).


```python
from typing import Optional

from kfp.dsl import PipelineTaskFinalStatus, component


@component(
    base_image="python:3.10-slim-buster",
    packages_to_install=["google-cloud-aiplatform", "requests", "google-cloud-secret-manager"],
)
def vertex_pipelines_notification_slack(
    project_id: str,
    pipeline_task_final_status: PipelineTaskFinalStatus,
    slack_webhook_url_secret_name: Optional[str] = None,
):
    """KFP Component that sends a notification to a Slack channel when a pipeline job ends.
    To be used as an exit handler in a pipeline.

    Args:
        pipeline_task_final_status (PipelineTaskFinalStatus): The status of the pipeline job.
        slack_webhook_url_secret_name (str, optional): The name of the secret containing the
            Slack webhook URL. Defaults to None. If None or empty string, the notification will
            be printed to stdout instead of being sent to Slack.
    """
    import logging
    from zoneinfo import ZoneInfo

    import requests
    from google.cloud import aiplatform
    from google.cloud.secretmanager import SecretManagerServiceClient

    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    pipeline_job = aiplatform.PipelineJob.get(
        resource_name=pipeline_task_final_status.pipeline_job_resource_name
    )

    emojis = {
        "SUCCEEDED": ["✅", ":risibeer:"],
        "FAILED": ["❌", ":risicry:"],
        "CANCELLED": ["🚫", "🚫"],
    }

    TIMEZONE = "Europe/Paris"

    status = pipeline_task_final_status.state
    project = pipeline_task_final_status.pipeline_job_resource_name.split("/")[1]
    pipeline_name = pipeline_task_final_status.pipeline_job_resource_name.split("/")[5]
    pipeline_job_id = pipeline_task_final_status.pipeline_job_resource_name
    start_time = (
        f"{pipeline_job.create_time.astimezone(tz=ZoneInfo(TIMEZONE)).isoformat()} {TIMEZONE}"
    )
    console_link = pipeline_job._dashboard_uri()

    title_str = f"{emojis[status][0]} Vertex Pipelines job *{pipeline_name}* ended with the following state: *{status}* {emojis[status][1]}."  # noqa: E501

    additional_details = f"""*Additional details:*
    - *Project:* {project}
    - *Pipeline name:* {pipeline_name}
    - *Pipeline job ID:* {pipeline_job_id}
    - *Start time:* {start_time}

To view this pipeline job in Cloud Console, use the following link: {console_link}
"""

    notification_json = {
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": title_str}},
            {"type": "section", "text": {"type": "mrkdwn", "text": additional_details}},
        ]
    }

    def get_secret_value(project_id, secret_name) -> str:
        client = SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")

    if slack_webhook_url_secret_name:
        slack_webhook_url = get_secret_value(project_id, slack_webhook_url_secret_name)

        response = requests.post(
            slack_webhook_url,
            json=notification_json,
            headers={"Content-type": "application/json"},
        )

        response.raise_for_status()
    else:
        logging.info(title_str + "\n" + additional_details)
```

Then you can use this component as an exit handler in your pipeline:

```python
import kfp.dsl

from my_custom_components import vertex_pipelines_notification_slack

@kfp.dsl.pipeline(name="my-pipeline")
def my_pipeline(project_id: str, slack_webhook_url_secret_name: str):
    notification_task = vertex_pipelines_notification_slack(
        project_id=project_id,
        slack_webhook_url_secret_name=slack_webhook_url_secret_name
    )

    with kfp.dsl.ExitHandler(notification_task, name="Exit Handler"):
        # Add your pipeline tasks here.
```
