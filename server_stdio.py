"""
FMP Financial Data MCP Server - STDIO Version for Local Testing
This version runs in STDIO mode for testing with MCP Inspector.
For production deployment, use server.py instead.
"""
import os
import httpx
from typing import Optional
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS, INTERNAL_ERROR
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
FMP_API_KEY = os.environ.get("FMP_API_KEY", "")
FMP_BASE_URL = "https://financialmodelingprep.com/stable"

if not FMP_API_KEY:
    print("WARNING: FMP_API_KEY not set. Server will fail on API calls.")

# Create MCP server in STDIO mode for local testing
mcp = FastMCP(
    "FMP Financial Data Connector",
    instructions="""Custom connector for Financial Modeling Prep (FMP) API.
Use these operations to search for stock symbols and company names,
retrieve real-time stock quotes, historical price/volume data,
company profiles, and key financial statements (income statement,
balance sheet, cash flow).
Copilot Agent should call these operations whenever the user asks
for financial data, stock lookups, company information,
or financial statements."""
)


# Helper function for API calls
async def fmp_api_call(
    endpoint: str,
    params: dict,
    ctx: Optional[Context[ServerSession, None]] = None
) -> dict | list:
    """Make authenticated call to FMP API"""
    try:
        # Add API key to parameters
        params["apikey"] = FMP_API_KEY
        
        url = f"{FMP_BASE_URL}/{endpoint}"
        
        if ctx:
            await ctx.debug(f"Calling FMP API: {endpoint}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            if ctx:
                await ctx.debug(f"FMP API response received")
            
            return data
            
    except httpx.HTTPStatusError as e:
        error_msg = f"FMP API error (HTTP {e.response.status_code}): {e.response.text}"
        if ctx:
            await ctx.error(error_msg)
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=error_msg
        ))
    except httpx.HTTPError as e:
        error_msg = f"HTTP request failed: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=error_msg
        ))
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=error_msg
        ))


# Tool 1: Stock Symbol Search
@mcp.tool()
async def search_symbol(
    query: str,
    ctx: Context[ServerSession, None]
) -> list[dict]:
    """Stock Symbol Search - Use when you have a company name or partial ticker 
    and want to find matching ticker symbols and basic metadata.
    
    Args:
        query: Search text (company name or symbol fragment)
        
    Returns:
        List of matching tickers with symbol, name, currency, stockExchange, exchangeShortName
    """
    await ctx.info(f"Searching for symbol: {query}")
    
    if not query or len(query.strip()) == 0:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Query parameter cannot be empty"
        ))
    
    return await fmp_api_call("search-symbol", {"query": query}, ctx)


# Tool 2: Company Name Search
@mcp.tool()
async def search_name(
    query: str,
    ctx: Context[ServerSession, None]
) -> list[dict]:
    """Company Name Search - Use when you want to search companies or ETFs by name 
    and retrieve associated ticker symbols and exchange information.
    
    Args:
        query: Company or ETF name to search
        
    Returns:
        List of matching companies with symbol, name, currency, stockExchange, exchangeShortName
    """
    await ctx.info(f"Searching for company name: {query}")
    
    if not query or len(query.strip()) == 0:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Query parameter cannot be empty"
        ))
    
    return await fmp_api_call("search-name", {"query": query}, ctx)


# Tool 3: Stock Quote
@mcp.tool()
async def get_quote(
    symbol: str,
    ctx: Context[ServerSession, None]
) -> list[dict]:
    """Stock Quote - Use to fetch current price, volume, market cap, PE ratio, 
    and other real-time trading information for a given stock symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL', 'MSFT')
        
    Returns:
        List containing quote data with price, volume, marketCap, pe, eps, etc.
    """
    await ctx.info(f"Getting quote for: {symbol}")
    
    if not symbol or len(symbol.strip()) == 0:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Symbol parameter cannot be empty"
        ))
    
    return await fmp_api_call("quote", {"symbol": symbol.upper()}, ctx)


# Tool 4: Historical Prices
@mcp.tool()
async def get_historical_prices(
    symbol: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    ctx: Context[ServerSession, None] = None
) -> dict:
    """Historical Stock Prices - Use to retrieve historical daily OHLCV 
    (Open, High, Low, Close, Volume) data for charting or analysis.
    
    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL')
        from_date: Start date in YYYY-MM-DD format (optional)
        to_date: End date in YYYY-MM-DD format (optional)
        
    Returns:
        Dict with symbol and historical array of date, open, high, low, close, volume
    """
    await ctx.info(f"Getting historical prices for: {symbol}")
    
    if not symbol or len(symbol.strip()) == 0:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Symbol parameter cannot be empty"
        ))
    
    params = {}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    
    return await fmp_api_call(f"historical-price-full/{symbol.upper()}", params, ctx)


# Tool 5: Company Profile
@mcp.tool()
async def get_company_profile(
    symbol: str,
    ctx: Context[ServerSession, None]
) -> list[dict]:
    """Company Profile - Use to get comprehensive company details including 
    description, sector, industry, CEO, website, address, and key metrics.
    
    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL')
        
    Returns:
        List containing company profile with description, industry, CEO, website, etc.
    """
    await ctx.info(f"Getting company profile for: {symbol}")
    
    if not symbol or len(symbol.strip()) == 0:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Symbol parameter cannot be empty"
        ))
    
    return await fmp_api_call("profile", {"symbol": symbol.upper()}, ctx)


# Tool 6: Income Statement
@mcp.tool()
async def get_income_statement(
    symbol: str,
    period: str = "annual",
    limit: int = 5,
    ctx: Context[ServerSession, None] = None
) -> list[dict]:
    """Income Statement - Use to retrieve revenue, expenses, net income, 
    EPS and other P&L data for fundamental analysis.
    
    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL')
        period: 'annual' or 'quarter' (default: 'annual')
        limit: Number of periods to return (default: 5)
        
    Returns:
        List of income statements with revenue, netIncome, eps, etc.
    """
    await ctx.info(f"Getting income statement for: {symbol} ({period})")
    
    if not symbol or len(symbol.strip()) == 0:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Symbol parameter cannot be empty"
        ))
    
    if period not in ["annual", "quarter"]:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Period must be 'annual' or 'quarter'"
        ))
    
    return await fmp_api_call(
        f"income-statement/{symbol.upper()}",
        {"period": period, "limit": limit},
        ctx
    )


# Tool 7: Balance Sheet
@mcp.tool()
async def get_balance_sheet(
    symbol: str,
    period: str = "annual",
    limit: int = 5,
    ctx: Context[ServerSession, None] = None
) -> list[dict]:
    """Balance Sheet - Use to get assets, liabilities, equity, and other 
    balance sheet data for financial health analysis.
    
    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL')
        period: 'annual' or 'quarter' (default: 'annual')
        limit: Number of periods to return (default: 5)
        
    Returns:
        List of balance sheets with totalAssets, totalLiabilities, totalEquity, etc.
    """
    await ctx.info(f"Getting balance sheet for: {symbol} ({period})")
    
    if not symbol or len(symbol.strip()) == 0:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Symbol parameter cannot be empty"
        ))
    
    if period not in ["annual", "quarter"]:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Period must be 'annual' or 'quarter'"
        ))
    
    return await fmp_api_call(
        f"balance-sheet-statement/{symbol.upper()}",
        {"period": period, "limit": limit},
        ctx
    )


# Tool 8: Cash Flow Statement
@mcp.tool()
async def get_cash_flow(
    symbol: str,
    period: str = "annual",
    limit: int = 5,
    ctx: Context[ServerSession, None] = None
) -> list[dict]:
    """Cash Flow Statement - Use to retrieve operating, investing, and 
    financing cash flows for liquidity and cash management analysis.
    
    Args:
        symbol: Stock ticker symbol (e.g. 'AAPL')
        period: 'annual' or 'quarter' (default: 'annual')
        limit: Number of periods to return (default: 5)
        
    Returns:
        List of cash flow statements with operatingCashFlow, freeCashFlow, etc.
    """
    await ctx.info(f"Getting cash flow for: {symbol} ({period})")
    
    if not symbol or len(symbol.strip()) == 0:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Symbol parameter cannot be empty"
        ))
    
    if period not in ["annual", "quarter"]:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Period must be 'annual' or 'quarter'"
        ))
    
    return await fmp_api_call(
        f"cash-flow-statement/{symbol.upper()}",
        {"period": period, "limit": limit},
        ctx
    )


if __name__ == "__main__":
    print("Starting FMP Financial Data MCP Server (STDIO mode for testing)...")
    print(f"API Key configured: {'Yes' if FMP_API_KEY else 'No'}")
    print("\nTest with MCP Inspector:")
    print("  Transport Type: STDIO")
    print("  Command: python")
    print("  Arguments: server_stdio.py")
    print()
    
    # Run in STDIO mode
    mcp.run()
