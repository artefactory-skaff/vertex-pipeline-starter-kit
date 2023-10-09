# How to deploy a BentoML bundle to VertexAI

[BentoML](https://github.com/bentoml/BentoML) is a library that allows you to build the online serving API to serve your model.
The purpose of this tutorial is to show you how to deploy a BentoML bundle to a VertexAI Endpoint.

Along with this tutorial, an example is provided, with some useful function to perform this process in a VertexAI pipeline.
Check it out: [docs/assets/howto_bentoml](assets/howto_bentoml/)

## Table of contents

- [How to deploy a BentoML bundle to VertexAI](#how-to-deploy-a-bentoml-bundle-to-vertexai)
  - [Table of contents](#table-of-contents)
  - [Should you use BentoML?](#should-you-use-bentoml)
  - [Key ressources](#key-ressources)
  - [Steps](#steps)
    - [1. Save the model to BentoML registry](#1-save-the-model-to-bentoml-registry)
    - [2. Create the API service](#2-create-the-api-service)
    - [3. Write the bentofile.yaml file](#3-write-the-bentofileyaml-file)
    - [4. Build the Docker image](#4-build-the-docker-image)
    - [5. Testing the service locally](#5-testing-the-service-locally)
    - [6. Upload the model to Google Artifact Regitry (GAR)](#6-upload-the-model-to-google-artifact-regitry-gar)
    - [7.Import image to VertexAI model registry](#7import-image-to-vertexai-model-registry)
    - [8.Deploy model to VertexAI endpoint](#8deploy-model-to-vertexai-endpoint)
    - [9.Test the endpoint](#9test-the-endpoint)

## Should you use BentoML?

When not using the build-in algorithms, model deployment on VertexAI requires users to build their own container image and API server.
BentoML is a library that allows you to turn your ML model into production API endpoint with just a few lines of code.
It will handle the creation of the serving API and the Docker image. It can be an alternative to [Tensorflow Serving](https://www.tensorflow.org/tfx/guide/serving) or [TorchServe](https://github.com/pytorch/serve/tree/master/examples).

!!! quote
  Shipping ML models to production is broken. Data Scientists may not have all the expertise in building production services and the trained models they delivered are very hard to test and deploy. This often leads to a time consuming and error-prone workflow, where a pickled model or weights file is handed over to a software engineering team.
  BentoML is an end-to-end solution for model serving, making it possible for Data Science teams to ship their models as prediction services, in a way that is easy to test, easy to deploy, and easy to integrate with other DevOps tools.

Please read these ressources to go further:

- [Reddit thread](https://www.reddit.com/r/MachineLearning/comments/g1cfre/p_bentoml_an_opensource_platform_for/)
- [Official documentation](https://docs.bentoml.com/en/latest/overview/what-is-bentoml.html#why-bentoml)

## Key ressources

This tutorial assume you already know the basics of BentoML.
Please read these ressources first:

- [Quickstart BentoML Latest version >1.0](https://colab.research.google.com/github/bentoml/BentoML/blob/main/examples/quickstart/iris_classifier.ipynb)
- [Quicktart <0.3 LTS](https://colab.research.google.com/github/bentoml/BentoML/blob/0.13-LTS/guides/quick-start/bentoml-quick-start-guide.ipynb)
- [Deploying on VertexAI Workbench <0.3 LTS](https://web.archive.org/web/20220818073753/https://docs.bentoml.org/en/0.13-lts/deployment/google_cloud_ai_platform.html)
- [GCP - How to deploy PyTorch models on Vertex AI using TorchServe](https://cloud.google.com/blog/topics/developers-practitioners/pytorch-google-cloud-how-deploy-pytorch-models-vertex-ai)

## Steps

Here are the steps to deploy a BentoML bundle to VertexAI:

- 1. Save the model to BentoML registry
- 2. Create the API service
- 3. Write the bentofile.yaml file
- 4. Build the Docker image
- 5. Testing the service locally
- 6. Upload the model to Google Artifact Regitry (GAR)
- 7. Import image to VertexAI model registry
- 8. Deploy model to VertexAI endpoint
- 9. Test the endpoint

Steps 1 to 5 are pure BentoML development steps. Here is a high-level overview of what they do:

- 1. Save the model to BentoML registry: In this step, you save the trained model from your ML framework (scikit, pytorch) to a BentoML model registry.
- 2. Create the API service: Create a `service.py` file to wrap your model and lay out the serving logic.
- 3. Write the bentofile.yaml file: Package your model and the BentoML Service into a Bento through a configuration YAML file. Each Bento corresponds to a directory that contains all the source code, dependencies, and model files required to serve the Bento, and an auto-generated Dockerfile for containerization.
- 4. Build the Docker image: This will build the Docker image and push it.
- 5. Testing the service locally: In this step, you test that the prediction service works locally.

If you want to understand what is done at these steps, read the [BentoML quick start](https://colab.research.google.com/github/bentoml/BentoML/blob/main/examples/quickstart/iris_classifier.ipynb).

In steps 6 to 9, we will deploy the serving API to VertexAI:

- 6. Upload the model to Google Artifact Regitry (GAR): This will upload the Docker image of the serving API to Google Artifact Regitry.
- 7. Import image to VertexAI model registry: Import the Docker Image as a custom model in Vertex AI model registry.
- 8. Deploy model to VertexAI endpoint: Deploy the model from the registry to an online-prediction endpoint on VertexAI.
- 9. Test the endpoint: Send a request to the VertexAI endpoint to test it.


### 1. Save the model to BentoML registry

Here is an example using Sklearn, but bentoml [supports many frameworks](https://docs.bentoml.com/en/latest/frameworks/index.html).

```py title="bin/save_model.py" hl_lines="14"
from sklearn import svm, datasets
import bentoml

MODEL_NAME = "iris_clf"

# Load training data
iris = datasets.load_iris()
X, y = iris.data, iris.target

# Model Training
clf = svm.SVC()
clf.fit(X, y)

# Save the model to BentoML format
saved_model = bentoml.sklearn.save_model(MODEL_NAME, clf)
print(saved_model.path)
```

Once the model is saved, you can access it thought the CLI command: `bentoml models get iris_clf:latest`

### 2. Create the API service

One specificity here is that VertexAI endpoints only accept JSON input and output, formated in a specific way.
Inputs must be formated as a JSON object with a key "instances" containing a list of lists of values.
Outputs must be formated as a JSON object with a key "predictions" containing a list of values.

Example of input:

```json title="query.json"
{
  "instances": [
    [5.1, 3.5, 1.4, 0.2],
    [4.9, 3.0, 1.4, 0.2]
  ]
}
```

Example of response:

```json
{
  "predictions": [
    "setosa",
    "setosa"
  ]
}
```

So we need to write a service that will take the input, format it to a list of lists, and then call the BentoML bundle.
Then, we need to format the output to the VertexAI format.

You can use pydantic to validate the input and output of your API.
This will also enrich the API Swagger documentation that is automatically generated.

```py title="service.py"
import bentoml
from bentoml.io import JSON
from pydantic import BaseModel
from typing import List

# write data model in a separate file for better code readability
class Query(BaseModel):
    instances: List[List[float]]

class Response(BaseModel):
    predictions: List[str]

# Load the BentoML bundle
iris_clf_runner = bentoml.sklearn.get("iris_clf:latest").to_runner()
input_schema = JSON(pydantic_model=Query)
output_schema = JSON(pydantic_model=Response)

svc = bentoml.Service("iris_classifier", runners=[iris_clf_runner])

@svc.api(input=input_schema, output=output_schema)
def classify(input_series: dict) -> dict:
    input_series = input_series["instances"]
    return {"predictions": iris_clf_runner.predict.run(input_series)}
```

You can test the service locally using the following command: `bentoml serve service.py:svc --reload`

### 3. Write the bentofile.yaml file

```yaml title="bentofile.yaml"
service: "service.py:svc"
labels:
  owner: bentoml-team
  project: gallery
include:
  - "*.py"
python:
  packages:
    - scikit-learn
    - pandas
```

### 4. Build the Docker image

Here are the steps to build the Docker image and run it locally:

```bash
VERSION="0.0.1"
GCP_PROJECT="my-gcp-project"
SERVICE="iris_classifier"
YAML_PATH="bentofile.yaml"
IMAGE_URI=eu.gcr.io/$GCP_PROJECT/$SERVICE:$VERSION

bentoml build -f $YAML_PATH ./src/ --version $VERSION
bentoml serve $SERVICE:latest --production
bentoml containerize $SERVICE:$VERSION -t $IMAGE_URI
```

However, it's not handy to use the CLI if you want to do this step in a Python Script, and there is a lack of documentation on that.
So I wrote a [Python script](assets/howto_bentoml/workflows/build_bento.py) to do this step, that can be used in a VertexAI component.

Under the hood, when you do the `bentoml containerize` command, docker actually builds the image.
If you want to use this as a VertexAI component, you cannot rely on Docker as you are already in a container. 
The workaround here is to use Cloud Build to build the image.

Check it out: [assets/howto_bentoml/workflows/build_bento.py](assets/howto_bentoml/workflows/build_bento.py)

### 5. Testing the service locally

On a terminal, launch the prediction service:

```bash
bentoml serve $SERVICE:$VERSION
```

Then, do a query:

```python
import requests
import json

query = json.load(open("query.json"))

response = requests.post(
    "http://0.0.0.0:3000/classify",
    json=query,
)
print(response.text)
```

Also, try to run the container:

```bash
docker run -it --rm -p 3000:3000 eu.gcr.io/$GCP_PROJECT_ID/$SERVICE:$VERSION serve --production
```

Then do the query again.

If it doesn't work at this step, it won't work on VertexAI either.
So make sure you fix the errors before going further.

### 6. Upload the model to Google Artifact Regitry (GAR)

```bash
docker push $IMAGE_URI`
```

Or once again using the [Python script](docs/assets/howto_bentoml/utils/gcp.py), you can rely on Cloud Run to do this step.

### 7.Import image to VertexAI model registry

Now that your image is in Google Artifact Registry, you can import it to VertexAI model registry.

Pay attention to:

* the predict route, it must be the same as your service (`/classify` in this example).
* the port, by default BentoML uses 3000 so stick to that

Here is a bash script to do this step:

```bash
PREDICT_ROUTE="/classify"
HEALTH_ROUTE="/healthz"
PORTS=3000

echo "Import as VertexAI model"
MODEL_ID="$(gcloud ai models list --region $LOCATION --filter="DISPLAY_NAME: ${MODEL_NAME}" --format="value(MODEL_ID)")"
if [ -z "${MODEL_ID:=}" ]; then
  echo "No existing model found for ${MODEL_NAME}. Importing model."
  gcloud ai models upload \
    --region=$LOCATION \
    --display-name=$MODEL_NAME \
    --container-image-uri=$IMAGE_URI \
    --container-ports=$PORTS \
    --container-health-route=$HEALTH_ROUTE \
    --container-predict-route=$PREDICT_ROUTE \
    --project=$GCP_PROJECT
else
  echo "Existing model found for ${MODEL_NAME} (${MODEL_ID}). Importing new version"
  gcloud ai models upload \
    --region=$LOCATION \
    --display-name=$MODEL_NAME \
    --container-image-uri=$IMAGE_URI \
    --project=$GCP_PROJECT \
    --container-ports=$PORTS \
    --container-health-route=$HEALTH_ROUTE \
    --container-predict-route=$PREDICT_ROUTE \
    --parent-model=projects/${GCP_PROJECT}/locations/${LOCATION}/models/${MODEL_ID}
fi
```

And the Python Equivalent: [assets/howto_bentoml/workflows/import_model.py](assets/howto_bentoml/workflows/push_model.py)

### 8.Deploy model to VertexAI endpoint

The final step is to deploy the model to a VertexAI "online prediction" endpoint.

To do it manually, follow the following step.
To do it programatically, check out the [Python script](docs/assets/howto_bentoml/workflows/deploy_model.py).

Manual steps:

* Go to [VertexAI model registry](https://console.cloud.google.com/vertex-ai/locations/europe-west1/models/)
* Click on the model you want to deploy
* Click on the burger menu at the right on the latest version, then click on "Set as Default"
* Go to the [VertexAI endpoint page](https://console.cloud.google.com/vertex-ai/locations/europe-west1/endpoints/) and select the endpoint you want to deploy the model to
* Select the model you want to undeploy, and click on the burger menu at the right, then click on "Undeploy model from endpoint"
* Click on the burger menu at the right on the latest version, then click on "Deploy to Endpoint"
* "Add to existing endpoint" and select the endpoint
* Set traffic split to 100%, and define machine type
* Deploy

It takes approximatively 15 minutes. Then you get an email. If the deployment failed, you get an email (Object: "Vertex AI was unable to deploy model") with a link to the [stackdriver logs](https://console.cloud.google.com/logs/).
To find the error in the logs, filter on severity="error".

You will have to fix the error, then go thought the whole process again.

To know more, check out the [official documentation](https://cloud.google.com/vertex-ai/docs/predictions/use-custom-container#examples).

### 9.Test the endpoint

```bash
# Get the endpoint ID from the endpoint name
ENDPOINT_NAME="iris_classifier_endpoint"
ENDPOINT_ID=$(gcloud ai endpoints list --filter DISPLAY_NAME=$ENDPOINT_NAME --region=$LOCATION --format="value(ENDPOINT_ID)")

# OR uncomment the following line to set the endpoint ID manually:
# ENDPOINT_ID="123456789"

INPUT_DATA_FILE="query.json"

echo "Sendind a request to the endpoint ${ENDPOINT_NAME} with ID: ${ENDPOINT_ID}"

curl \
-X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/endpoints/${ENDPOINT_ID}:predict \
-d "@${INPUT_DATA_FILE}"

```
