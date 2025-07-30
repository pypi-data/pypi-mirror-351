"""
Same-chain DEX swap execution operations using local HTTP endpoints.
"""

import httpx
from ..utils.blockchain import get_explorer_url
from .quotes import convert_decimal_to_minimal_units
from ..utils.wallet import WALLET_CREDENTIALS

def get_private_key_for_address(wallet_address: str, chain_id: str) -> str:
    """Get the corresponding private key for a wallet address based on chain type."""
    if chain_id == "501":  # Solana
        if wallet_address == WALLET_CREDENTIALS['solana_address']:
            return WALLET_CREDENTIALS['solana_private_key']
    else:  # EVM chains
        if wallet_address == WALLET_CREDENTIALS['evm_address']:
            return WALLET_CREDENTIALS['evm_private_key']
    return None

async def execute_dex_swap_internal(from_token: str, to_token: str, amount: str, chain_id: str, 
                          user_wallet_address: str, slippage: str = "0.5", 
                          to_wallet_address: str = None, decimal_amount: str = None, 
                          from_token_decimals: int = None, slippage_mode: str = "percentage") -> str:
    """Execute a DEX token swap using local HTTP endpoints.
    
    Args:
        from_token: From token contract address
        to_token: To token contract address  
        amount: Amount to swap (in minimal divisible units) - used if decimal_amount is None
        chain_id: Chain ID (e.g., "1" for Ethereum, "56" for BSC, "501" for Solana)
        user_wallet_address: User's wallet address for the swap (source address)
        slippage: Slippage tolerance (e.g., "0.5" for 0.5% in percentage mode, "0.005" for 0.5% in decimal mode)
        to_wallet_address: Destination wallet address (default: None, uses user_wallet_address)
        decimal_amount: Optional decimal amount (e.g., "0.1" for 0.1 tokens)
        from_token_decimals: Required if decimal_amount is provided - decimals of the from_token
        slippage_mode: Mode for slippage handling ("percentage" or "decimal", default: "percentage")
    
    Returns:
        str: Success message with transaction details or error message
    """
    
    # Get the corresponding private key
    private_key = get_private_key_for_address(user_wallet_address, chain_id)
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
    
    # Convert slippage based on mode
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
    
    # Determine if this is Solana or EVM based on chain_id
    if chain_id == "501":  # Solana
        endpoint = "https://mcp-node-server-264441234562.us-central1.run.app/sol/swap"
        payload = { 
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token,
            "userWalletAddress": user_wallet_address,
            "amount": amount,
            "chainIndex": chain_id,
            "slippage": str(slippage_decimal),
            "privateKey": private_key,
            "toAddress": destination_address
        }
    else:  # EVM chains
        endpoint = "https://mcp-node-server-264441234562.us-central1.run.app/evm/swap"
        payload = {
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token,
            "fromAddress": user_wallet_address,
            "amount": amount,
            "chainIndex": chain_id,
            "slippage": str(slippage_decimal),
            "privateKey": private_key,
            "toAddress": destination_address
        }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                endpoint,
                headers={"Content-Type": "application/json"},
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("code") == 200:
                    data = result.get("data", {})
                    
                    if chain_id == "501":  # Solana response format
                        tx_hash = data.get("txHash") or data.get("data")
                        explorer_url = get_explorer_url(chain_id, tx_hash)
                        return f"""
✅ SOLANA SWAP EXECUTED SUCCESSFULLY!

=== TRANSACTION DETAILS ===
Transaction Hash: {tx_hash}
Status: {data.get("status", "success")}
Message: {data.get("mag", "Swap completed successfully!")}

=== EXPLORER LINK ===
{explorer_url}

🎉 Your Solana swap has been completed successfully!
"""
                    else:  # EVM response format
                        return f"""
✅ EVM SWAP EXECUTED SUCCESSFULLY!

=== TRANSACTION DETAILS ===
{data}

🎉 Your swap has been completed successfully!
"""
                else:
                    return f"❌ Swap failed: {result.get('msg', 'Unknown error')}"
            else:
                return f"❌ HTTP Error {response.status_code}: {response.text}"
                
    except httpx.TimeoutException:
        return "❌ Request timeout. The swap service may be busy. Please try again."
    except httpx.ConnectError:
        return "❌ Cannot connect to swap service. Please ensure the service is running on localhost:8735"
    except Exception as e:
        return f"❌ Error executing swap: {str(e)}"


def register_same_chain_swap_tools(mcp):
    """Register same-chain swap related MCP tools."""
    
    @mcp.tool()
    async def execute_dex_swap(from_token: str, to_token: str, amount: str, chain_id: str, 
                                   user_wallet_address: str, slippage: str = "0.5",
                                   to_wallet_address: str = None, decimal_amount: str = None, 
                                   from_token_decimals: int = None, slippage_mode: str = "percentage") -> str:
        """Execute a DEX token swap using local HTTP endpoints.
        Supports both Solana and EVM chains through different endpoints.

        Args:
            from_token: From token contract address
            to_token: To token contract address  
            amount: Amount to swap (in minimal divisible units) - used if decimal_amount is None
            chain_id: Chain ID (e.g., "1" for Ethereum, "56" for BSC, "501" for Solana)
            user_wallet_address: User's wallet address for the swap (required)
            slippage: Slippage tolerance (e.g., "0.5" for 0.5% in percentage mode, "0.005" for 0.5% in decimal mode)
            to_wallet_address: Destination wallet address (default: None, uses user_wallet_address)
            decimal_amount: Optional decimal amount (e.g., "0.1" for 0.1 tokens)
            from_token_decimals: Required if decimal_amount is provided - decimals of the from_token
            slippage_mode: Mode for slippage handling ("percentage" or "decimal", default: "percentage")
        """
        if not user_wallet_address:
            return "❌ user_wallet_address is required. Please provide the wallet address that will execute the swap."
        return await execute_dex_swap_internal(from_token, to_token, amount, chain_id, 
                                             user_wallet_address, slippage, 
                                             to_wallet_address, decimal_amount, 
                                             from_token_decimals, slippage_mode) 