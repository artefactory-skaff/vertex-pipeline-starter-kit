from google.cloud import storage
from google.cloud.devtools import cloudbuild_v1
from loguru import logger


def build_docker_image_with_cloud_build(
    source_code_uri: str,
    docker_image_uri: str,
    project_id: str,
    dockerfile_path: str = "./Dockerfile",
):
    """This function build and push a docker image to GCR / Artifact registry using Cloud Build.
    It's the equivalent of the CLI command: gcloud builds submit --tag $DOCKER_IMAGE_URI --file $DOCKERFILE_PATH $SOURCE_CODE_URI

    Args:
        source_code_uri (str): The archive containing the source code to build the docker image.
            eg. gs://bucket-name/path/to/archive.tar.gz
        docker_image_uri (str): The URI of the docker image to build. (--tag in docker build)
            eg. europe-docker.pkg.dev/project-id/eu.gcr.io/image-name:tag
        project_id (str): The project id where the Cloud Build job will run.
        dockerfile_path (str): The path to the dockerfile to use to build the docker image. (--file in docker build)
            eg. "env/docker/Dockerfile"
    """
    logger.info(f"Building docker image {docker_image_uri} using cloud build")
    # parsing the source code uri to get the bucket name and blob name
    bucket_name, blob_name = (
        storage.Blob.from_string(source_code_uri).bucket.name,
        storage.Blob.from_string(source_code_uri).name,
    )
    client = cloudbuild_v1.CloudBuildClient()
    storage_source = cloudbuild_v1.StorageSource(bucket=str(bucket_name), object=str(blob_name))
    source = cloudbuild_v1.Source(storage_source=storage_source)
    build = cloudbuild_v1.Build(
        source=source,
        steps=[
            {
                "name": "gcr.io/cloud-builders/docker",
                "args": [
                    "build",
                    "-t",
                    docker_image_uri,
                    "-f",
                    dockerfile_path,  # position of the Dockerfile in the Bento directory
                    ".",
                ],
            }
        ],
        images=[docker_image_uri],
    )
    request = cloudbuild_v1.CreateBuildRequest(project_id=project_id, build=build)
    operation = client.create_build(request=request)
    response = operation.result()
    logger.info(f"Build response: {response}")


def upload_file_to_gcs(target_path: str, local_path: str) -> None:
    storage_client = storage.Client()

    bucket_name, blob_name = (
        storage.Blob.from_string(target_path).bucket.name,
        storage.Blob.from_string(target_path).name,
    )

    bucket = storage_client.bucket(bucket_name)
    logger.debug(f"Saving File to {target_path}")
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)