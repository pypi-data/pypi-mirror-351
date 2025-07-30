"""
Simplified blockchain utilities for basic chain information.
"""

from .constants import CHAIN_NAMES, EXPLORER_URLS, RPC_URLS, NATIVE_TOKENS
import httpx
import json
from typing import Optional, Dict, Any


def get_chain_name(chain_id: str) -> str:
    """Get the display name for a chain ID."""
    return CHAIN_NAMES.get(chain_id, f"Chain {chain_id}")


def get_explorer_url(chain_id: str, tx_hash: str) -> str:
    """Get the block explorer URL for a transaction."""
    base_url = EXPLORER_URLS.get(chain_id)
    if base_url:
        return f"{base_url}{tx_hash}"
    return f"Transaction: {tx_hash}"


def is_supported_chain(chain_id: str) -> bool:
    """Check if a chain ID is supported."""
    return chain_id in CHAIN_NAMES


def register_blockchain_tools(mcp):
    """Register blockchain-related MCP tools. (Wallet balance tool removed)"""
    pass 