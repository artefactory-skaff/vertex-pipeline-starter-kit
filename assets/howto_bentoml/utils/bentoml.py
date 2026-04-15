import bentoml
from loguru import logger
import pickle


def delete_bento_models_if_exists(model_name: str):
    try:
        bentoml.models.delete(tag=model_name)
    except bentoml.exceptions.NotFound:
        logger.info(f"No Bento model {model_name} found to delete")


def delete_bento_service_if_exists(service_name: str):
    try:
        bentoml.bentos.delete(tag=service_name)
    except bentoml.exceptions.NotFound:
        logger.info(f"No Bento file {service_name} found to delete")

def save_model_to_bento(model_path, model_name):
    """load model from a pickle file, and save it as a BentoML model"""
    with open(model_path, 'rb') as file:  
        clf = pickle.load(file)
    bentoml.sklearn.save_model(name=model_name, pipeline=clf)

