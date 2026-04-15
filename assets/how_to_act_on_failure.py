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
