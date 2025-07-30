"""
Constants and configuration for OKX DEX Trading MCP.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OKX API Configuration
OKX_API_BASE = os.getenv("OKX_API_BASE", "https://web3.okx.com")
OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_SECRET_KEY = os.getenv("OKX_API_SECRET")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")
OKX_PROJECT_ID = os.getenv("OKX_PROJECT_ID")
OKX_SANDBOX = os.getenv("OKX_SANDBOX", "false").lower() == "true"
USER_AGENT = "okx-dex-quotes-app/1.0"

# Default Wallet Configuration
SOLANA_WALLET_ADDRESS = os.getenv("SOLANA_WALLET_ADDRESS")
SOLANA_PRIVATE_KEY = os.getenv("SOLANA_PRIVATE_KEY")
EVM_WALLET_ADDRESS = os.getenv("EVM_WALLET_ADDRESS")
EVM_PRIVATE_KEY = os.getenv("EVM_PRIVATE_KEY")

# Chain ID to RPC URL mapping with backup RPC endpoints
RPC_URLS = {
    "1": ["https://eth.llamarpc.com", "https://rpc.ankr.com/eth", "https://ethereum.publicnode.com"],  # Ethereum
    "56": ["https://bsc-dataseed.binance.org/", "https://rpc.ankr.com/bsc", "https://bsc.publicnode.com"],  # BSC
    "137": ["https://polygon-rpc.com/", "https://rpc.ankr.com/polygon", "https://polygon.publicnode.com"],  # Polygon
    "43114": ["https://api.avax.network/ext/bc/C/rpc", "https://rpc.ankr.com/avalanche", "https://avalanche.publicnode.com"],  # Avalanche
    "42161": ["https://arb1.arbitrum.io/rpc", "https://rpc.ankr.com/arbitrum", "https://arbitrum.publicnode.com"],  # Arbitrum
    "10": ["https://mainnet.optimism.io", "https://rpc.ankr.com/optimism", "https://optimism.publicnode.com"],  # Optimism
    "8453": ["https://mainnet.base.org", "https://rpc.ankr.com/base", "https://base.publicnode.com"],  # Base
    "501": ["https://api.mainnet-beta.solana.com", "https://rpc.ankr.com/solana", "https://solana.publicnode.com"],  # Solana
}

# Native token addresses for each chain
NATIVE_TOKENS = {
    "1": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",  # ETH
    "56": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",  # BNB
    "137": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",  # MATIC
    "43114": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",  # AVAX
    "42161": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",  # ETH on Arbitrum
    "10": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",  # ETH on Optimism
    "8453": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",  # ETH on Base
    "501": "So11111111111111111111111111111111111111112",  # SOL (Wrapped SOL)
}

# Chain names for display
CHAIN_NAMES = {
    "1": "Ethereum",
    "56": "BSC",
    "137": "Polygon",
    "43114": "Avalanche",
    "42161": "Arbitrum",
    "10": "Optimism",
    "8453": "Base",
    "324": "zkSync Era",
    "59144": "Linea",
    "5000": "Mantle",
    "501": "Solana",
}

# Block explorer URLs
EXPLORER_URLS = {
    "1": "https://etherscan.io/tx/",
    "56": "https://bscscan.com/tx/",
    "137": "https://polygonscan.com/tx/",
    "43114": "https://snowtrace.io/tx/",
    "42161": "https://arbiscan.io/tx/",
    "10": "https://optimistic.etherscan.io/tx/",
    "8453": "https://basescan.org/tx/",
    "501": "https://solscan.io/tx/",
}

# Common bridge tokens by chain
BRIDGE_TOKENS = {
    "1": {  # Ethereum
        "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "WETH": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
        "DAI": "0x6b175474e89094c44da98b954eedeac495271d0f"
    },
    "56": {  # BSC
        "USDC": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
        "USDT": "0x55d398326f99059ff775485246999027b3197955",
        "WBNB": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",
        "BUSD": "0xe9e7cea3dedca5984780bafc599bd69add087d56"
    },
    "137": {  # Polygon
        "USDC": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359",
        "USDC.e": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174",
        "USDT": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f",
        "WMATIC": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",
        "WETH": "0x7ceb23fd6c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c"
    },
    "43114": {  # Avalanche
        "USDC": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
        "USDC.e": "0xa7d7079b0fead91f3e65f86e8915cb59c1a4c664",
        "USDT": "0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7",
        "WAVAX": "0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7"
    },
    "42161": {  # Arbitrum
        "USDC": "0xaf88d065e77c8cc2239327c5edb3a432268e5831",
        "USDC.e": "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8",
        "USDT": "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",
        "WETH": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1"
    },
    "10": {  # Optimism
        "USDC": "0x0b2c639c533813f4aa9d7837caf62653d097ff85",
        "USDC.e": "0x7f5c764cbc14f9669b88837ca1490cca17c31607",
        "USDT": "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58",
        "WETH": "0x4200000000000000000000000000000000000006"
    },
    "8453": {  # Base
        "USDC": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
        "WETH": "0x4200000000000000000000000000000000000006"
    },
    "501": {  # Solana
        "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        "SOL": "So11111111111111111111111111111111111111112",
        "WSOL": "So11111111111111111111111111111111111111112",
        "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
        "SRM": "SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt"
    }
}

# Default gas prices by chain (in wei)
DEFAULT_GAS_PRICES = {
    "1": 20000000000,    # 20 gwei for Ethereum
    "137": 30000000000,  # 30 gwei for Polygon
    "56": 5000000000,    # 5 gwei for BSC
    "42161": 100000000,  # 0.1 gwei for Arbitrum
    "10": 1000000,       # 0.001 gwei for Optimism
    "8453": 1000000,     # 0.001 gwei for Base
}

# Stablecoin symbols for slippage calculations
STABLECOINS = ['USDC', 'USDT', 'DAI', 'BUSD', 'FRAX', 'LUSD'] 