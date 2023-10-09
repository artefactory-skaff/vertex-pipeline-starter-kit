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
    To use this component, you need to:

    * Create a Slack app and a Slack webhook URL. [Official documentation](https://api.slack.com/messaging/webhooks).
    * Create a secret and secret version in Secret Manager containing the Slack webhook URL. [Official documentation](https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets).



=== "1. Create message to be sent to Slack"

    Message creation includes:

    * Retrieving information about the job
    * Creating the string template
    * Creating the JSON payload to be sent to Slack

    ```python hl_lines="34-71"
    --8<-- "docs/assets/how_to_act_on_failure.py"
    ```

=== "2. Retrieve Slack webhook URL from Secret Manager"

    If the Slack webhook URL secret name is provided, the Slack webhook URL is retrieved from Secret Manager.

    ```python hl_lines="73-80"
    --8<-- "docs/assets/how_to_act_on_failure.py"
    ```

=== "3. Send message or log message"

    Depending on whether the Slack Webhook URL secret name is provided, the message will be sent to Slack or logged to stdout.
    This is useful for testing purposes, to avoid being spammed with notifications.

    ```python hl_lines="79-90"
    --8<-- "docs/assets/how_to_act_on_failure.py"
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
