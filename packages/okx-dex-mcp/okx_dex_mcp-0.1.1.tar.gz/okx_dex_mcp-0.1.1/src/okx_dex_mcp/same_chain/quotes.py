"""
Same-chain DEX quote operations.
"""

from ..utils.constants import OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE, OKX_API_BASE
from ..utils.okx_client import make_okx_request
from ..utils.formatters import format_dex_quote, get_slippage_recommendation


def convert_decimal_to_minimal_units(decimal_amount: str, decimals: int) -> str:
    """Convert decimal amount to minimal divisible units.
    
    Args:
        decimal_amount: Amount in decimal format (e.g., "1.5" for 1.5 tokens)
        decimals: Number of decimals for the token (e.g., 18 for most ERC20 tokens, 6 for USDC)
    
    Returns:
        str: Amount in minimal divisible units (e.g., "1500000000000000000" for 1.5 ETH)
    
    Examples:
        convert_decimal_to_minimal_units("1.0", 18) -> "1000000000000000000"  # 1 ETH
        convert_decimal_to_minimal_units("1.0", 6) -> "1000000"  # 1 USDC
        convert_decimal_to_minimal_units("0.1", 6) -> "100000"  # 0.1 USDC
    """
    try:
        # Convert to float first to handle decimal input
        amount_float = float(decimal_amount)
        # Multiply by 10^decimals to get minimal units
        minimal_units = int(amount_float * (10 ** decimals))
        return str(minimal_units)
    except (ValueError, OverflowError) as e:
        raise ValueError(f"Invalid decimal amount '{decimal_amount}': {str(e)}")


async def get_dex_quote_internal(from_token: str, to_token: str, amount: str, chain_id: str, 
                               decimal_amount: str = None, from_token_decimals: int = None) -> str:
    """Get a DEX trading quote for token swap with improved slippage recommendations.
    
    Args:
        from_token: From token contract address
        to_token: To token contract address  
        amount: Amount to swap (in minimal divisible units) - used if decimal_amount is None
        chain_id: Chain ID (e.g., "1" for Ethereum, "56" for BSC)
        decimal_amount: Optional decimal amount (e.g., "0.1" for 0.1 tokens)
        from_token_decimals: Required if decimal_amount is provided - decimals of the from_token
    """
    if not all([OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE]):
        return "❌ OKX API credentials not configured. Please set OKX_API_KEY, OKX_SECRET_KEY, and OKX_PASSPHRASE in .env file."
    
    # Convert decimal amount to minimal units if provided
    if decimal_amount is not None:
        if from_token_decimals is None:
            return "❌ from_token_decimals is required when using decimal_amount parameter."
        try:
            amount = convert_decimal_to_minimal_units(decimal_amount, from_token_decimals)
        except ValueError as e:
            return f"❌ Error converting decimal amount: {str(e)}"
    
    # Build URL for quote endpoint
    base_url = f"{OKX_API_BASE}/api/v5/dex/aggregator/quote"
    params = [
        f"chainId={chain_id}",
        f"fromTokenAddress={from_token}",
        f"toTokenAddress={to_token}",
        f"amount={amount}"
    ]
    full_url = f"{base_url}?{'&'.join(params)}"
    
    data = await make_okx_request(full_url)

    if not data:
        return f"❌ Unable to get quote for {from_token} -> {to_token}."

    if data.get("code") != "0":
        return f"❌ API Error: {data.get('msg', 'Unknown error')}"

    if not data.get("data"):
        return "❌ No quote data available for this token pair."

    quote_info = data["data"][0] if isinstance(data["data"], list) else data["data"]
    
    # Enhanced quote formatting with slippage recommendations
    formatted_quote = format_dex_quote(quote_info)
    slippage_guidance = get_slippage_recommendation(quote_info)
    
    return formatted_quote + slippage_guidance

def register_same_chain_quote_tools(mcp):
    """Register same-chain quote related MCP tools."""
    
    @mcp.tool()
    async def get_dex_quote(from_token: str, to_token: str, amount: str, chain_id: str, 
                          decimal_amount: str = None, from_token_decimals: int = None) -> str:
        """Get a DEX trading quote for token swap with improved slippage recommendations.

        Args:
            from_token: From token contract address
            to_token: To token contract address  
            amount: Amount to swap (in minimal divisible units) - used if decimal_amount is None
            chain_id: Chain ID (e.g., "1" for Ethereum, "56" for BSC)
            decimal_amount: Optional decimal amount (e.g., "0.1" for 0.1 tokens)
            from_token_decimals: Required if decimal_amount is provided - decimals of the from_token
        """
        return await get_dex_quote_internal(from_token, to_token, amount, chain_id, decimal_amount, from_token_decimals) 