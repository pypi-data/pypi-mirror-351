"""
Cross-chain DEX swap execution operations using local HTTP endpoints.
"""

import httpx
import json
from typing import Dict, Any
from ..same_chain.quotes import convert_decimal_to_minimal_units
from ..utils.wallet import WALLET_CREDENTIALS

def get_private_key_for_address(wallet_address: str) -> str:
    """Get the corresponding private key for a wallet address."""
    if wallet_address == WALLET_CREDENTIALS['evm_address']:
        return WALLET_CREDENTIALS['evm_private_key']
    elif wallet_address == WALLET_CREDENTIALS['arbitrum_address']:
        return WALLET_CREDENTIALS['arbitrum_private_key']
    elif wallet_address == WALLET_CREDENTIALS['solana_address']:
        return WALLET_CREDENTIALS['solana_private_key']
    return None

async def execute_cross_chain_swap_internal(from_chain: str, to_chain: str, from_token: str, to_token: str, 
                                  amount: str, user_wallet_address: str, slippage: str = "0.5",
                                  to_wallet_address: str = None, decimal_amount: str = None, 
                                  from_token_decimals: int = None, slippage_mode: str = "percentage") -> str:
    """Execute a cross-chain DEX token swap using local HTTP endpoint.
    
    Args:
        from_chain: Source chain ID
        to_chain: Destination chain ID
        from_token: From token contract address
        to_token: To token contract address
        amount: Amount to swap (in minimal divisible units) - used if decimal_amount is None
        user_wallet_address: User's wallet address for the swap (source address)
        slippage: Slippage tolerance (e.g., "0.5" for 0.5%, default: "0.5")
        to_wallet_address: Destination wallet address (default: None, uses user_wallet_address)
        decimal_amount: Optional decimal amount (e.g., "0.1" for 0.1 tokens)
        from_token_decimals: Required if decimal_amount is provided - decimals of the from_token
        slippage_mode: Mode for slippage handling ("percentage" or "decimal", default: "percentage")
    
    Returns:
        str: Success message with transaction details or error message
    """
    
    # Get the corresponding private key
    private_key = get_private_key_for_address(user_wallet_address)
    if private_key is None:
        return f"❌ No private key found for wallet address {user_wallet_address}"
    
    # Convert decimal amount to minimal units if provided
    if decimal_amount is not None:
        if from_token_decimals is None:
            return "❌ from_token_decimals is required when using decimal_amount parameter."
        try:
            amount = convert_decimal_to_minimal_units(decimal_amount, from_token_decimals)
        except ValueError as e:
            return f"❌ Error converting decimal amount: {str(e)}"
    
    # Use user_wallet_address as default destination if to_wallet_address is not provided
    destination_address = to_wallet_address if to_wallet_address is not None else user_wallet_address
    
    # Convert slippage from percentage format to decimal format
    try:
        slippage_float = float(slippage)
        if slippage_mode.lower() == "percentage":
            slippage_decimal = slippage_float / 100
        elif slippage_mode.lower() == "decimal":
            slippage_decimal = slippage_float
        else:
            return f"❌ Invalid slippage_mode: {slippage_mode}. Must be either 'percentage' or 'decimal'"
    except ValueError:
        return f"❌ Invalid slippage format: {slippage}. Please provide a numeric value."
    
    endpoint = "https://mcp-node-server-264441234562.us-central1.run.app/evm/crossChainSwap"
    payload = {
        "fromTokenAddress": from_token,
        "toTokenAddress": to_token,
        "fromAddress": user_wallet_address,
        "amount": amount,
        "fromChainIndex": from_chain,
        "slippage": slippage_decimal,
        "privateKey": private_key,
        "toAddress": destination_address,
        "toChainIndex": to_chain
    }

    print(payload)
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                endpoint,
                headers={"Content-Type": "application/json"},
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("code") == 200:
                    data = result.get("data", {})
                    
                    return f"""
✅ CROSS-CHAIN SWAP EXECUTED SUCCESSFULLY!

=== TRANSACTION DETAILS ===
{json.dumps(data, indent=2)}

🎉 Your cross-chain swap has been initiated successfully!
⏳ Cross-chain transactions may take several minutes to complete.
"""
                else:
                    return f"❌ Cross-chain swap failed: {result.get('msg', 'Unknown error')}"
            else:
                return f"❌ HTTP Error {response.status_code}: {response.text}"
                
    except httpx.TimeoutException:
        return "❌ Request timeout. Cross-chain swaps can take longer. Please try again."
    except httpx.ConnectError:
        return "❌ Cannot connect to swap service. Please ensure the service is running on localhost:8735"
    except Exception as e:
        return f"❌ Error executing cross-chain swap: {str(e)}"


def register_cross_chain_swap_tools(mcp):
    """Register cross-chain swap related MCP tools."""
    
    @mcp.tool()
    async def execute_cross_chain_swap(from_chain: str, to_chain: str, from_token: str, to_token: str, 
                                           amount: str, user_wallet_address: str, slippage: str = "0.5",
                                           to_wallet_address: str = None, decimal_amount: str = None, 
                                           from_token_decimals: int = None, slippage_mode: str = "percentage") -> str:
        """Execute a cross-chain DEX token swap using local HTTP endpoint.

        Args:
            from_chain: Source chain ID
            to_chain: Destination chain ID
            from_token: From token contract address
            to_token: To token contract address
            amount: Amount to swap (in minimal divisible units) - used if decimal_amount is None
            user_wallet_address: User's wallet address for the swap (required)
            slippage: Slippage tolerance (e.g., "0.5" for 0.5%, default: "0.5")
            to_wallet_address: Destination wallet address (default: None, uses user_wallet_address)
            decimal_amount: Optional decimal amount (e.g., "0.1" for 0.1 tokens)
            from_token_decimals: Required if decimal_amount is provided - decimals of the from_token
            slippage_mode: Mode for slippage handling ("percentage" or "decimal", default: "percentage")
        """
        return await execute_cross_chain_swap_internal(from_chain, to_chain, from_token, to_token, amount, 
                                                     user_wallet_address, slippage, to_wallet_address, 
                                                     decimal_amount, from_token_decimals, slippage_mode)