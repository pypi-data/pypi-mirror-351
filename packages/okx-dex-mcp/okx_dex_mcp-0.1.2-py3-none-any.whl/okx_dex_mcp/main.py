#!/usr/bin/env python3
"""
OKX DEX Trading MCP Server
Main entry point for the Model Context Protocol server providing DEX trading capabilities.
"""

import argparse
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("okx-dex-quotes")

# Import and register tools
from .api.credentials import register_credential_tools
from .api.market_data import register_market_data_tools
from .same_chain.quotes import register_same_chain_quote_tools
from .same_chain.swaps import register_same_chain_swap_tools
from .cross_chain.quotes import register_cross_chain_quote_tools
from .cross_chain.swaps import register_cross_chain_swap_tools
from .utils.blockchain import register_blockchain_tools

def register_all_tools():
    """Register all MCP tools with the server."""
    register_credential_tools(mcp)
    register_market_data_tools(mcp)
    register_same_chain_quote_tools(mcp)
    register_same_chain_swap_tools(mcp)
    register_cross_chain_quote_tools(mcp)
    register_cross_chain_swap_tools(mcp)
    register_blockchain_tools(mcp)

def parse_arguments():
    """Parse command line arguments for wallet credentials."""
    parser = argparse.ArgumentParser(
        description='OKX DEX Trading MCP Server',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--evm-address',
        required=True,
        help='EVM wallet address (e.g., 0x...)'
    )
    parser.add_argument(
        '--evm-private-key',
        required=True,
        help='EVM wallet private key (e.g., 0x...)'
    )
    parser.add_argument(
        '--solana-address',
        required=True,
        help='Solana wallet address (e.g., ...)'
    )
    parser.add_argument(
        '--solana-private-key',
        required=True,
        help='Solana wallet private key (e.g., ...)'
    )
    parser.add_argument(
        '--arbitrum-address',
        required=True,
        help='Arbitrum wallet address (e.g., ...)'
    )
    parser.add_argument(
        '--arbitrum-private-key',
        required=True,
        help='Arbitrum wallet private key (e.g., ...)'
    )
    return parser.parse_args()

def validate_wallet_credentials(args):
    """Validate wallet credentials format."""
    pass

def main():
    """Main entry point for the MCP server."""
    print("🚀 Starting OKX DEX Trading MCP Server...")
    
    # Parse and validate command line arguments
    args = parse_arguments()
    try:
        validate_wallet_credentials(args)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Store wallet credentials globally
    from .utils.wallet import WALLET_CREDENTIALS
    WALLET_CREDENTIALS.update({
        'evm_address': args.evm_address,
        'evm_private_key': args.evm_private_key,
        'solana_address': args.solana_address,
        'solana_private_key': args.solana_private_key,
        'arbitrum_address': args.arbitrum_address,
        'arbitrum_private_key': args.arbitrum_private_key
    })
    
    # Register all tools
    register_all_tools()
    
    # Start MCP server
    print("📡 MCP server running on stdio transport...")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main() 