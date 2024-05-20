from typing import Optional
from utils.vertexai import (
        get_model_if_exists,
        get_model_versions,
        get_last_model_and_set_to_default,
        get_endpoint_if_exists,
        create_endpoint,
        deploy_model_to_endpoint,
        MACHINE_TYPE,
        MAX_REPLICA_COUNT,
        ENABLE_ACCESS_LOGGING,
        ENABLE_REQUEST_RESPONSE_LOGGING,
        REQUEST_RESPONSE_LOGGING_SAMPLING_RATE,
    )

def deploy_model_workflow(
    model_name,
    endpoint_name,
    machine_type: str = MACHINE_TYPE,
    max_replica_count: str = MAX_REPLICA_COUNT,
    enable_request_response_logging: bool = ENABLE_REQUEST_RESPONSE_LOGGING,
    request_response_logging_sampling_rate: Optional[
        float
    ] = REQUEST_RESPONSE_LOGGING_SAMPLING_RATE,
    enable_access_logging: bool = ENABLE_ACCESS_LOGGING,
):
    model = get_model_if_exists(model_name)
    registry, versions = get_model_versions(model)
    model = get_last_model_and_set_to_default(registry, versions)
    endpoint = get_endpoint_if_exists(endpoint_name)
    if endpoint is None:
        endpoint = create_endpoint(
            endpoint_name,
            enable_request_response_logging=enable_request_response_logging,
            request_response_logging_sampling_rate=request_response_logging_sampling_rate,
        )
    deployed_model = deploy_model_to_endpoint(
        model,
        endpoint,
        machine_type=machine_type,
        max_replica_count=max_replica_count,
        enable_access_logging=enable_access_logging,
    )
    return deployed_model


if __name__ == "__main__":
    MODEL_NAME = "iris_classifier"
    ENDPOINT_NAME = f"{MODEL_NAME}_endpoint"

    deploy_model_workflow(
        model_name=MODEL_NAME,
        endpoint_name=ENDPOINT_NAME,
    )
