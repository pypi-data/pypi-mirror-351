"""Shared test fixtures"""

import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import pytest
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session")
def aoai_client() -> AzureOpenAI:
    """Azure OpenAI client"""
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
    client = AzureOpenAI(
        azure_ad_token_provider=token_provider,
        azure_endpoint=os.environ["AOAI_ENDPOINT"],
        api_version=os.environ["AOAI_API_VERSION"],
    )
    return client
