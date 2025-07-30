"""
Crypto.com developer platform Module.

This module provides tools for interacting with the Crypto.com developer platform.
These tools enable operations such as wallet creation, token balance retrieval,
transaction lookups, token transfers, and ERC20 balance queries. Each tool is
decorated with the `@tool` decorator, making it compatible with LangChain workflows.

Tools:
    - create_wallet: Create a new blockchain wallet.
    - get_native_balance: Retrieve the native token balance of an address.
    - get_transaction_by_hash: Fetch transaction details by hash.
    - transfer_token: Transfer tokens to a specific address.
    - get_erc20_balance: Retrieve the ERC20 token balance for an address.

Example:
    >>> from core.tools import create_wallet, get_native_balance
    >>> wallet_info = create_wallet()
    >>> print(wallet_info)
    Wallet created! Address: 0x123..., Private Key: abcd...
    
    >>> balance = get_native_balance("0x123...")
    >>> print(balance)
    The native balance for address 0x123... is 100.0.
"""

from .block import get_block_by_tag
from .contract import get_contract_abi
from .cronosid import lookup_cronosid_address, resolve_cronosid_name
from .defi import get_all_farms, get_farm_by_symbol, get_whitelisted_tokens
from .exchange import get_all_tickers, get_ticker_by_instrument
from .token import (
    get_erc20_balance,
    get_native_balance,
    swap_token,
    transfer_erc20_token,
    transfer_native_token,
    wrap_token,
)
from .transaction import (
    get_transaction_by_hash,
    get_transaction_status,
    get_transactions_by_address,
)
from .wallet import create_wallet, get_wallet_balance, send_ssowallet

# List of available tools
built_in_tools = [
    create_wallet,
    get_native_balance,
    get_transaction_by_hash,
    transfer_native_token,
    transfer_erc20_token,
    get_erc20_balance,
    wrap_token,
    swap_token,
    get_transactions_by_address,
    get_transaction_status,
    get_wallet_balance,
    get_all_tickers,
    get_ticker_by_instrument,
    get_whitelisted_tokens,
    get_all_farms,
    get_farm_by_symbol,
    get_block_by_tag,
    get_contract_abi,
    resolve_cronosid_name,
    lookup_cronosid_address,
    send_ssowallet,
]

__all__ = [
    'create_wallet',
    'get_native_balance',
    'get_transaction_by_hash',
    'transfer_token',
    'get_erc20_balance',
    'wrap_token',
    'swap_token',
    'get_transactions_by_address',
    'get_transaction_status',
    'get_wallet_balance',
    'get_all_tickers',
    'get_ticker_by_instrument',
    'get_whitelisted_tokens',
    'get_all_farms',
    'get_farm_by_symbol',
    'get_block_by_tag',
    'get_contract_abi',
    'resolve_cronosid_name',
    'lookup_cronosid_address',
    'send_ssowallet',

    'built_in_tools'
]
