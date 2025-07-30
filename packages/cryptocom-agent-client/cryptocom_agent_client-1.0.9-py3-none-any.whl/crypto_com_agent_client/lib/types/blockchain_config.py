"""
Blockchain Config Module.

This module defines the `BlockchainConfig` TypedDict, which represents the
configuration for blockchain-related settings and integrations.
"""

# Third-party imports
from typing import Optional

from pydantic import BaseModel, Field


class BlockchainConfig(BaseModel):
    """
    TypedDict for Blockchain configuration.

    Attributes:
        chainId (str): The ID of the blockchain to connect to.
        explorer_api_key (str): The API key for the blockchain explorer.
        private_key (Optional[str]): The private key for blockchain transactions.
        sso_wallet_url (Optional[str]): The URL for the SSO wallet service.

    Example:
        >>> from lib.types.blockchain_config import BlockchainConfig
        >>> blockchain_config: BlockchainConfig = {
        ...     "chainId": "240",
        ...     "explorer_api_key": "blockchain-api-key",
        ...     "sso_wallet_url": "sso-wallet-url"
        ... }
    """

    chainId: str
    explorer_api_key: str = Field(alias="explorer-api-key")
    private_key: Optional[str] = Field(alias="private-key", default=None)
    sso_wallet_url: Optional[str] = Field(alias="sso-wallet-url", default=None)
