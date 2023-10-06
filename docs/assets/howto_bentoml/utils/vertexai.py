from typing import Dict, Optional, Sequence, Tuple
from loguru import logger
import google.cloud.aiplatform as aip
import pandas as pd


LOCATION = "gcp-location"   # eg. "europe-west4"
PROJECT_ID = "gcp-project-id"   # eg. "my-project-id"
MACHINE_TYPE = "n1-standard-4"
MAX_REPLICA_COUNT = 4
ENABLE_ACCESS_LOGGING = False


def get_model_if_exists(model_name: str) -> Optional[aip.Model]:
    model = aip.Model.list(location=LOCATION, filter=f'display_name="{model_name}"')

    if len(model) == 0:
        logger.warning(f"No previous model found with name {model_name}")
        return None
    else:
        if len(model) > 1:
            logger.warning(
                f"Multiple models found with name {model_name}. Taking the first one arbitrarily."
            )
        model = model[0]
        logger.info(f"Found existing model: {model.resource_name}")
        return model


def upload_model_to_registry(
    display_name: str,
    serving_container_image_uri: str,
    parent_model: Optional[str] = None,
    is_default_version: bool = True,
    artifact_uri: Optional[str] = None,
    serving_container_predict_route: Optional[str] = None,
    serving_container_health_route: Optional[str] = None,
    description: Optional[str] = None,
    serving_container_command: Optional[Sequence[str]] = None,
    serving_container_args: Optional[Sequence[str]] = None,
    serving_container_environment_variables: Optional[Dict[str, str]] = None,
    serving_container_ports: Optional[Sequence[int]] = None,
    instance_schema_uri: Optional[str] = None,
    parameters_schema_uri: Optional[str] = None,
    prediction_schema_uri: Optional[str] = None,
    sync: bool = True,
    labels: Optional[Dict[str, str]] = None,
):
    """Inspired from: https://cloud.google.com/vertex-ai/docs/model-registry/import-model#aiplatform_upload_model_sample-python"""

    model = aip.Model.upload(
        parent_model=parent_model,
        display_name=display_name,
        serving_container_image_uri=serving_container_image_uri,
        serving_container_predict_route=serving_container_predict_route,
        serving_container_health_route=serving_container_health_route,
        artifact_uri=artifact_uri,
        instance_schema_uri=instance_schema_uri,
        parameters_schema_uri=parameters_schema_uri,
        prediction_schema_uri=prediction_schema_uri,
        description=description,
        serving_container_command=serving_container_command,
        serving_container_args=serving_container_args,
        serving_container_environment_variables=serving_container_environment_variables,
        serving_container_ports=serving_container_ports,
        sync=sync,
        labels=labels,
        is_default_version=is_default_version,
        location=LOCATION,
    )
    model.wait()

    logger.info(
        f"{model.display_name} has been uploaded to Vertex AI Model registry\
        with URI name: {model.resource_name}"
    )
    return model


def get_endpoint_if_exists(endpoint_name: str) -> Optional[aip.Endpoint]:
    parent_endpoint = aip.Endpoint.list(
        location=LOCATION, filter=f'display_name="{endpoint_name}"'
    )

    if len(parent_endpoint) == 0:
        logger.warning(f"No previous endpoint found with name {endpoint_name}")
        return None
    else:
        if len(parent_endpoint) > 1:
            logger.warning(
                f"Multiple endpoints found with name {endpoint_name}. Taking the first one arbitrarily."
            )
        parent_endpoint = parent_endpoint[0]
        return parent_endpoint


def create_endpoint(
    endpoint_name: str,
    enable_request_response_logging: bool = False,
    request_response_logging_sampling_rate: Optional[float] = None,
) -> aip.Endpoint:
    """Create a vertex AI endpoint"""
    BQ_DESTINATION_TABLE = (
        f"bq://{PROJECT_ID}.vertex_ai_endpoint_logs.request_response_logs_{endpoint_name}"
    )
    endpoint = aip.Endpoint.create(
        display_name=endpoint_name,
        project=PROJECT_ID,
        location=LOCATION,
        description="Product classification endpoint, deployed automatically with Vertex AI",
        enable_request_response_logging=enable_request_response_logging,
        request_response_logging_sampling_rate=request_response_logging_sampling_rate,
        request_response_logging_bq_destination_table=BQ_DESTINATION_TABLE,
    )
    endpoint.wait()

    logger.info(f"Created endpoint {endpoint.display_name} with ID {endpoint.resource_name}")
    return endpoint


def deploy_model_to_endpoint(
    model: aip.Model,
    endpoint: aip.Endpoint,
    machine_type=MACHINE_TYPE,
    max_replica_count=MAX_REPLICA_COUNT,
    enable_access_logging=ENABLE_ACCESS_LOGGING,
) -> str:
    """deploy a Vertex AI model to an endpoint"""
    deployed_model = model.deploy(
        endpoint=endpoint,
        traffic_percentage=100,
        machine_type=machine_type,
        min_replica_count=1,
        max_replica_count=max_replica_count,
        enable_access_logging=enable_access_logging,
    )
    deployed_model.wait()

    logger.info(f"Deployed model {model.display_name} to endpoint {endpoint.display_name}")
    return deployed_model


def get_model_versions(model: aip.Model) -> Tuple[aip.ModelRegistry, pd.DataFrame]:
    registry = aip.models.ModelRegistry(model.resource_name, location=LOCATION)
    model_versions = pd.DataFrame(registry.list_versions())
    return registry, model_versions


def get_last_model_and_set_to_default(
    registry: aip.models.ModelRegistry, versions: pd.DataFrame
) -> aip.Model:
    last_version_id = versions.sort_values("version_create_time", ascending=False).iloc[0][
        "version_id"
    ]
    registry.add_version_aliases(["default", "production"], version=last_version_id)
    logger.info(f"Set version {last_version_id} as default and production version")
    model = registry.get_model(version="production")
    return model
