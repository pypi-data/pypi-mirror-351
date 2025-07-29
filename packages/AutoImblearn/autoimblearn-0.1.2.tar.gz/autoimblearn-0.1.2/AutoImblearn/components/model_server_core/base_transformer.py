import requests
from .base_model_client import BaseDockerModelClient


class BaseTransformer(BaseDockerModelClient):
    """ Abstract base class for sklearn-like transformers.
    fit          : Ensure the container is running
    transform    : Post the transform request through RESTful API
    fit_transform: Perform both fit and transform
    """

    def transform(self, X, y=None, dockerfile_dir="."):
        """Transform the training data"""
        try:
            self.ensure_container_running()
            payload = {

            }
            response = requests.post(f"{self.api_url}/transform", json=payload)
            response.raise_for_status()
            return response.json()
        finally:
            self.stop_container()

    def fit_transform(self, X, y=None, dockerfile_dir="."):
        self.fit(X, y, dockerfile_dir)
        return self.transform(X, y, dockerfile_dir)
