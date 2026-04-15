import os
from utils.vertexai import get_model_if_exists, upload_model_to_registry

IMAGE_TAG = os.getenv("IMAGE_TAG", "latest")
PREDICT_ROUTE = "/classify"
HEALTH_ROUTE = "/healthz"
PORTS = 3000


def push_model_workflow(
    model_name: str,
    serving_container_image_uri: str,
) -> str:
    """This workflow pushes model from a Google Artifact Registry to Vertex AI Model registry.
    If the model already exists, it will be updated.

    Args:
        model_name (str): Name of the display model in Google Registry.
        serving_container_image_uri (str): URI of the image in Google Artifact Registry.
            Eg. "eu.gcr.io/gcp-project-id/iris_classifier_svc:latest"
    """
    model = get_model_if_exists(model_name)
    model = upload_model_to_registry(
        model_name,
        serving_container_image_uri,
        parent_model=model.resource_name,
        serving_container_predict_route=PREDICT_ROUTE,
        serving_container_health_route=HEALTH_ROUTE,
        serving_container_ports=[PORTS],
        description="Product classification model, deployed automatically with Vertex AI",
        labels={"image_tag": os.getenv("IMAGE_TAG", "latest")},
        is_default_version=False,    # it safer to perform evaluation and make sure the model is good before setting the model as default
    )
    return model.display_name


if __name__ == "__main__":
    MODEL_NAME = "iris_classifier"
    PROJECT_ID = "gcp_project_id"
    SERVICE_NAME = f"{MODEL_NAME}_svc"
    SERVING_CONTAINER_IMAGE_URI = (
        f"europe-docker.pkg.dev/{PROJECT_ID}/eu.gcr.io/{SERVICE_NAME}:{IMAGE_TAG}"
    )
    push_model_workflow(MODEL_NAME, SERVING_CONTAINER_IMAGE_URI)
