import os

import weaviate
from dotenv import load_dotenv
from weaviate.classes.init import AdditionalConfig, Timeout
from weaviate.connect import ConnectionParams
from env_config import api_config

load_dotenv(override=True)


def get_weaviate_client():
    return weaviate.WeaviateAsyncClient(
        connection_params=ConnectionParams.from_params(
            http_host=api_config.WEAVIATE_HOST,
            http_port=8080,
            http_secure=False,
            grpc_host=api_config.WEAVIATE_HOST,
            grpc_port=50051,
            grpc_secure=False,
        ),
        additional_config=AdditionalConfig(timeout=Timeout(init=30, query=60, insert=120)),
        skip_init_checks=True,
    )
    # return weaviate.use_async_with_weaviate_cloud(
    #     cluster_url=os.getenv("WEAVIATE_CLUSTER_URI"),
    #     auth_credentials=Auth.api_key(os.getenv("WEAVIATE_CLUSTER_API_KEY")),
    #     headers={"X-Openai-Api-Key": os.getenv("OPENAI_API_KEY")},
    # )
