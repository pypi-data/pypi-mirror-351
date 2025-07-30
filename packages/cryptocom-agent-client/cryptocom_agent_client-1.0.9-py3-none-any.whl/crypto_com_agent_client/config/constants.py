"""
Service Configuration Module.

This module handles the configuration and environment variable loading required for the application.
It sets up constants such as the default AI service provider, the default AI model, and the API client
key for interacting with Crypto.com services.

Constants:
    PROVIDER_DEFAULT (Provider): The default provider for AI services, set to OpenAI.
    MODEL_DEFAULT (str): The default model for AI operations, set to GPT-4.
    LLAMA4_MODEL (str): The default Llama 4 model for Groq provider.
    VERTEXAI_LOCATION_DEFAULT (str): The default location for Vertex AI operations.
"""

# Third-party imports
from dotenv import load_dotenv

# Internal application imports
from crypto_com_agent_client.lib.enums.provider_enum import Provider

# Load environment variables from a .env file
load_dotenv()


PROVIDER_DEFAULT = Provider.OpenAI
"""
The default provider for AI services.

This constant defines the default provider for AI services in the application. By default,
it is set to OpenAI. This value can be overridden by specifying a different provider during
initialization.

Example:
    >>> from lib.enums.model_enum import Provider
    >>> print(PROVIDER_DEFAULT)
    OpenAI
"""

MODEL_DEFAULT = "gpt-4"
"""
The default model to be used for AI operations.

This constant specifies the default AI model to be used in the application. It is set to GPT-4
for the OpenAI provider. This value can be overridden by specifying a different model during
initialization.

Example:
    >>> print(MODEL_DEFAULT)
    gpt-4
"""

LLAMA4_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

VERTEXAI_LOCATION_DEFAULT = "us-west1"
