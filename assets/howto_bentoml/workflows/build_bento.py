from loguru import logger
import bentoml
from utils.bentoml import delete_bento_models_if_exists, save_model_to_bento, delete_bento_service_if_exists
from utils.gcp import build_docker_image_with_cloud_build, upload_file_to_gcs


PROJECT_ID = 'gcp_project_id'


def save_model_workflow(model_path: str, model_name: str) -> str:
    """This function is used to save the model to BentoML and push it to GCR

    It's an equivalent to these commands:
    ```bash
    bentoml build -f "$YAML_PATH" ./ --version $VERSION
    bentoml containerize $SERVICE:$VERSION -t "$IMAGE_URI"
    docker push "$IMAGE_URI"
    ```

    Args:
        model_path (str): the path to the model artifact (eg. pickle).
            Eg. "gs://bucket-name/model_dirpath/"
        model_name (str): The name of the model. Eg. "iris_classifier"

    Returns:
        str: the URI of the pushed image
            eg. "gcr.io/project-id/iris-classifier:latest"
    """
    bento_filepath = "path/to/bento/file/bento.yaml"
    service_name = f"{model_name}_svc"
    delete_bento_models_if_exists(model_name)
    save_model_to_bento(model_path, model_name)
    logger.info(f"Model saved: {bentoml.models.list()}")
    delete_bento_service_if_exists(service_name)

    logger.info(f"Building Bento service {service_name} from {bento_filepath}")
    bento_build = bentoml.bentos.build_bentofile(
        bento_filepath,
        build_ctx=".",
        version="latest",
    )
    logger.info(f"Bento Service saved: {bentoml.bentos.list()}")
    service_name_tagged = f"{bento_build.tag.name}:{bento_build.tag.version}"
    export_filename = f"{service_name_tagged.replace(':', '_')}.zip"
    # `local_export_path` is the local file path where the Bento service is exported as a
    # zip file. It is the output path where the exported Bento service is saved on the
    # local machine before being uploaded to Google Cloud Storage (GCS).
    local_export_path = bentoml.bentos.export_bento(
        tag=service_name_tagged, path=f"outputs/{export_filename}", output_format="zip"
    )
    logger.info(f"Bento exported to {local_export_path}")
    export_gcs_uri = f"{model_path}/{export_filename}"
    logger.info(f"Uploading Bento to GCS to {export_gcs_uri}")
    upload_file_to_gcs(target_path=export_gcs_uri, local_path=local_export_path)
    docker_image_uri = f"europe-docker.pkg.dev/{PROJECT_ID}/eu.gcr.io/{service_name_tagged}"
    # Build Dockerfile of the Bento with cloud build, as an alternative to bentoml.container.build()
    # which is not working with Vertex AI.
    # the image is also pushed to the container registry (GAR)
    build_docker_image_with_cloud_build(
        export_gcs_uri,
        docker_image_uri,
        project_id=PROJECT_ID,
        dockerfile_path="env/docker/Dockerfile",  # Path to the Dockerfile in the Bento archive
    )
    logger.success(f"Pushed docker image {docker_image_uri}")
    return docker_image_uri


if __name__ == "__main__":
    MODEL_PATH = 'path_to_model_artifact.pkl'
    MODEL_NAME = 'iris_classifier'

    docker_image_uri = save_model_workflow(
        model_path=MODEL_PATH,
        model_name=MODEL_NAME,
    )
