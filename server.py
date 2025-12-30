"""
FMP Financial Data MCP Server
Wraps Financial Modeling Prep (FMP) API for use with Copilot Studio.
Provides stock quotes, company profiles, financial statements, and more.
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

# Create MCP server with stateless HTTP for Copilot Studio
mcp = FastMCP(
    "FMP Financial Data Connector",
    instructions="""Custom connector for Financial Modeling Prep (FMP) API.
Use these operations to search for stock symbols and company names,
retrieve real-time stock quotes, historical price/volume data,
company profiles, and key financial statements (income statement,
balance sheet, cash flow).
Copilot Agent should call these operations whenever the user asks
for financial data, stock lookups, company information,
or financial statements.""",
    stateless_http=True,
    json_response=True
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
    """Stock Quote API - Retrieves real-time stock price, change, and volume for a given ticker.
    Copilot should use this when the user asks for the current stock price.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        
    Returns:
        List with quote data including price, change, volume, marketCap, etc.
    """
    await ctx.info(f"Getting quote for: {symbol}")
    
    if not symbol or len(symbol.strip()) == 0:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Symbol parameter cannot be empty"
        ))
    
    return await fmp_api_call("quote", {"symbol": symbol.upper()}, ctx)


# Tool 4: Historical Price & Volume Data
@mcp.tool()
async def get_historical_prices(
    symbol: str,
    ctx: Context[ServerSession, None]
) -> dict:
    """Historical Price & Volume Data - Retrieves full end-of-day historical price and volume.
    Use for charts, trend analysis, or backtesting.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        
    Returns:
        Object with symbol and historical array containing date, open, high, low, close, volume
    """
    await ctx.info(f"Getting historical prices for: {symbol}")
    
    if not symbol or len(symbol.strip()) == 0:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Symbol parameter cannot be empty"
        ))
    
    # Note: The endpoint is /historical-price-eod/full/{symbol}
    return await fmp_api_call(f"historical-price-eod/full/{symbol.upper()}", {}, ctx)


# Tool 5: Company Profile
@mcp.tool()
async def get_company_profile(
    symbol: str,
    ctx: Context[ServerSession, None]
) -> list[dict]:
    """Company Profile (SEC) - Retrieves detailed company profile such as industry, sector,
    CEO, market cap, website, and more.
    Copilot should call this when the user asks about a company overview.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        
    Returns:
        List with company profile including name, industry, sector, CEO, website, description, etc.
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
    ctx: Context[ServerSession, None],
    period: str = "annual",
    limit: int = 5
) -> list[dict]:
    """Income Statement - Retrieves annual or quarterly income statements for a company.
    Use for revenue, gross profit, operating income, and net income analysis.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        period: "annual" or "quarter" (default: "annual")
        limit: Number of periods to return (default: 5)
        
    Returns:
        List of income statements with revenue, expenses, profit metrics, EPS, etc.
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
    
    if limit < 1 or limit > 100:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Limit must be between 1 and 100"
        ))
    
    return await fmp_api_call(
        "income-statement",
        {"symbol": symbol.upper(), "period": period, "limit": limit},
        ctx
    )


# Tool 7: Balance Sheet Statement
@mcp.tool()
async def get_balance_sheet(
    symbol: str,
    ctx: Context[ServerSession, None],
    period: str = "annual",
    limit: int = 5
) -> list[dict]:
    """Balance Sheet Statement - Retrieves balance sheet data including assets, liabilities,
    and shareholder equity. Copilot should use this when the user
    asks for a balance sheet or financial position.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        period: "annual" or "quarter" (default: "annual")
        limit: Number of periods to return (default: 5)
        
    Returns:
        List of balance sheets with assets, liabilities, equity, etc.
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
    
    if limit < 1 or limit > 100:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Limit must be between 1 and 100"
        ))
    
    return await fmp_api_call(
        "balance-sheet-statement",
        {"symbol": symbol.upper(), "period": period, "limit": limit},
        ctx
    )


# Tool 8: Cash Flow Statement
@mcp.tool()
async def get_cash_flow(
    symbol: str,
    ctx: Context[ServerSession, None],
    period: str = "annual",
    limit: int = 5
) -> list[dict]:
    """Cash Flow Statement - Retrieves cash flow statements (operating, investing, financing).
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)
        period: "annual" or "quarter" (default: "annual")
        limit: Number of periods to return (default: 5)
        
    Returns:
        List of cash flow statements with operating, investing, and financing activities
    """
    await ctx.info(f"Getting cash flow statement for: {symbol} ({period})")
    
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
    
    if limit < 1 or limit > 100:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Limit must be between 1 and 100"
        ))
    
    return await fmp_api_call(
        "cash-flow-statement",
        {"symbol": symbol.upper(), "period": period, "limit": limit},
        ctx
    )


# Get ASGI app for Azure deployment
app = mcp.streamable_http_app()


# Main entry point for local testing
if __name__ == "__main__":
    print("Starting FMP Financial Data MCP Server...")
    print(f"API Key configured: {'Yes' if FMP_API_KEY else 'No'}")
    print("Running on http://localhost:8000")
    print("MCP Endpoint: http://localhost:8000/mcp/")
    print("\nTest with MCP Inspector:")
    print("  Transport Type: Streamable HTTP")
    print("  URL: http://localhost:8000/mcp/")
    print("\nReady for Azure App Service deployment!")
    
    mcp.run(transport="streamable-http")
