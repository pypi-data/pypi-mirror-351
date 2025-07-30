"""
Cross-chain DEX quote operations.
"""

import aiohttp
import json
from ..utils.wallet import WALLET_CREDENTIALS

async def get_cross_chain_quote_internal(
    from_token_address: str,
    to_token_address: str,
    amount: str,
    from_wallet_address: str,
    from_chain_index: str,
    to_chain_index: str,
    to_wallet_address: str = None,
    slippage: str = "1",
    slippage_mode: str = "percentage",
) -> str:
    """Get a cross-chain DEX trading quote.
    
    Args:
        from_token_address: Source token address
        to_token_address: Destination token address
        amount: Amount to swap (in minimal divisible units)
        from_wallet_address: Source wallet address for the swap (your wallet address)
        from_chain_index: Source chain index
        to_chain_index: Destination chain index
        to_wallet_address: Destination wallet address for receiving tokens (defaults to from_wallet_address if None)
        slippage: Allowed slippage value (default: "1")
        slippage_mode: Mode of slippage value - "percentage" or "float" (default: "percentage")
    """
    
    endpoint = "https://mcp-node-server-264441234562.us-central1.run.app/evm/crossChainQuote"
    
    # Set to_wallet_address to from_wallet_address if not provided
    if to_wallet_address is None:
        to_wallet_address = from_wallet_address
    
    # Handle slippage based on mode and convert to float
    try:
        slippage_float = float(slippage)
        if slippage_mode == "percentage":
            if slippage_float < 0 or slippage_float > 100:
                return "❌ Invalid slippage percentage. Must be between 0 and 100."
            # Convert percentage to float (e.g., 1% -> 0.01)
            slippage_float = slippage_float / 100
        elif slippage_mode == "float":
            if slippage_float < 0 or slippage_float > 1:
                return "❌ Invalid slippage float. Must be between 0 and 1."
        else:
            return "❌ Invalid slippage_mode. Must be either 'percentage' or 'float'."
    except ValueError:
        return "❌ Invalid slippage value. Must be a valid number."
    
    params = {
        "fromTokenAddress": from_token_address,
        "toTokenAddress": to_token_address,
        "amount": amount,
        "fromAddress": from_wallet_address,
        "fromChainIndex": from_chain_index,
        "toChainIndex": to_chain_index,
        "toAddress": to_wallet_address,
        "slippage": str(slippage_float),  # Convert back to string for API
        "slippageMode": "float"  # Always send as float mode to API
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=params) as response:
                if response.status != 200:
                    return f"❌ API Error: HTTP {response.status}"
                
                data = await response.json()
                
                if not data:
                    return "❌ No data received from API"

                result = f"""✅ CROSS-CHAIN DEX QUOTE FOUND

=== ROUTE DETAILS ===
From Chain: {from_chain_index}
To Chain: {to_chain_index}

=== TOKEN DETAILS ===
From Token Address: {from_token_address}
To Token Address: {to_token_address}

=== TRANSACTION DETAILS ===
Amount: {amount}
From Address: {from_wallet_address}
To Address: {to_wallet_address}
Slippage: {slippage} ({slippage_mode}) -> {slippage_float} (float)

=== API RESPONSE ===
{json.dumps(data, indent=2)}

💡 This quote is for cross-chain swapping. Please verify all details before proceeding.
"""
                return result
                
    except Exception as e:
        return f"""❌ ERROR FETCHING CROSS-CHAIN QUOTE

Error details: {str(e)}

Please verify:
• All addresses are valid
• Chain IDs are supported
• Amount is in correct format
• Network connection is stable
"""

def register_cross_chain_quote_tools(mcp):
    """Register cross-chain quote related MCP tools."""
    
    @mcp.tool()
    async def get_cross_chain_quote(
        from_token_address: str,
        to_token_address: str,
        amount: str,
        from_wallet_address: str,
        from_chain_index: str,
        to_chain_index: str,
        to_wallet_address: str = None,
        slippage: str = "1",
        slippage_mode: str = "percentage"
    ) -> str:
        """Get a cross-chain DEX trading quote.

        Args:
            from_token_address: Source token address
            to_token_address: Destination token address
            amount: Amount to swap (in minimal divisible units)
            from_wallet_address: Source wallet address (required)
            from_chain_index: Source chain index
            to_chain_index: Destination chain index
            to_wallet_address: Destination wallet address (optional, uses from_wallet_address if not provided)
            slippage: Allowed slippage value (default: "1")
            slippage_mode: Mode of slippage value - "percentage" or "float" (default: "percentage")
        """
        return await get_cross_chain_quote_internal(
            from_token_address,
            to_token_address,
            amount,
            from_wallet_address,
            from_chain_index,
            to_chain_index,
            to_wallet_address,
            slippage,
            slippage_mode
        ) 