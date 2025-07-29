import pandas as pd

# from ..model_server_core.base_model_client import BaseDockerModelClient
from AutoImblearn.components.model_server_core.base_transformer import BaseTransformer
import os


class RunHyperImpute(BaseTransformer):
    # TODO make model parameter work

    def __init__(self, model="median"):
        super().__init__(
            image_name=f"hyperimpute-api",
            container_name=f"{model}_container",
            container_port=8080,
            volume_mounts={
                os.path.join(os.path.dirname(os.path.abspath(__file__)), model):
                    "/code/AutoImblearn/Docker",
            },  # mount current dir
            dockerfile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hyperimputebased"),
        )

    @property
    def payload(self):
        return {
            "metric": self.args.metric,
            "model": self.args.model,
        }

