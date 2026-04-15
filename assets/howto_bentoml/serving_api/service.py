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