# Building an MCP Server for Copilot Studio

## Complete Lab Guide: Create, Host, and Use an MCP Server

This guide walks you through building a **Model Context Protocol (MCP) server**, hosting it on **Azure App Service**, and integrating it with **Microsoft Copilot Studio** as a tool for your AI agent.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Part 1: Build the MCP Server](#part-1-build-the-mcp-server)
4. [Part 2: Test Locally with MCP Inspector](#part-2-test-locally-with-mcp-inspector)
5. [Part 3: Deploy to Azure App Service](#part-3-deploy-to-azure-app-service)
6. [Part 4: Test Deployment with Postman](#part-4-test-deployment-with-postman)
7. [Part 5: Integrate with Copilot Studio](#part-5-integrate-with-copilot-studio)
8. [References](#references)

---

## Overview

**What You'll Build:**
- An MCP server that wraps the Financial Modeling Prep (FMP) API
- 8 financial data tools for stock quotes, company profiles, and financial statements
- Cloud-hosted server on Azure for Copilot Studio integration
- AI agent in Copilot Studio that can answer financial questions

**What is MCP?**  
Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). It enables AI assistants to securely access data and tools through a unified interface.

---

## Prerequisites

### Required Tools
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/) (for MCP Inspector)
- **Azure CLI** - [Install](https://learn.microsoft.com/cli/azure/install-azure-cli)
- **Postman** - [Download](https://www.postman.com/downloads/) (for API testing)
- **Git** - [Download](https://git-scm.com/downloads)

### Required Accounts
- **FMP API Key** - Free tier available at [financialmodelingprep.com](https://site.financialmodelingprep.com/developer/docs)
- **Azure Subscription** - [Free account](https://azure.microsoft.com/free/)
- **Microsoft Copilot Studio** - [Access here](https://copilotstudio.microsoft.com/)

---

## Part 1: Build the MCP Server

### Step 1: Clone or Create Project

```bash
# Create project directory
mkdir fmp-mcp-server
cd fmp-mcp-server

# Initialize git repository
git init
```

### Step 2: Install Dependencies

Create `requirements.txt`:
```txt
mcp[cli]==1.9.0
httpx==0.27.0
pydantic==2.10.5
uvicorn==0.34.0
starlette==0.41.3
python-dotenv==1.0.0
```

Install packages:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create `.env` file:
```bash
# Copy from example
cp .env.example .env
```

Edit `.env` and add your FMP API key:
```
FMP_API_KEY=your_actual_api_key_here
```

### Step 4: Create the MCP Server

The server code (`server.py`) implements 8 financial data tools using FastMCP:
- `search_symbol` - Search for stock ticker symbols
- `search_name` - Search companies by name
- `get_quote` - Real-time stock quotes
- `get_historical_prices` - Historical price and volume data
- `get_company_profile` - Company overview and metadata
- `get_income_statement` - Income statement data
- `get_balance_sheet` - Balance sheet data
- `get_cash_flow` - Cash flow statement data

**Key Features:**
- Uses `stateless_http=True` for cloud deployment
- Implements proper error handling with MCP error codes
- Provides detailed tool descriptions for AI agents
- Supports Server-Sent Events (SSE) for streaming

---

## Part 2: Test Locally with MCP Inspector

The **MCP Inspector** is a developer tool for testing MCP servers locally before deployment.

### Step 1: Start Your MCP Server

```bash
python server.py
```

Expected output:
```
Starting FMP Financial Data MCP Server...
API Key configured: Yes
Running on http://localhost:8000
MCP Endpoint: http://localhost:8000/mcp/
```

### Step 2: Launch MCP Inspector

In a new terminal:
```bash
npx @modelcontextprotocol/inspector
```

This opens the MCP Inspector UI in your browser (usually http://localhost:5173).

### Step 3: Connect to Your Server

In the MCP Inspector UI:
1. **Transport Type**: Select "Streamable HTTP"
2. **URL**: Enter `http://localhost:8000/mcp/`
3. Click **Connect**

### Step 4: Test Your Tools

Once connected, you'll see all 8 tools listed. Try testing:

**Test 1: Get Stock Quote**
- Tool: `get_quote`
- Parameters: `{"symbol": "AAPL"}`
- Expected: Current Apple stock price and trading data

**Test 2: Search Company**
- Tool: `search_name`
- Parameters: `{"query": "Microsoft"}`
- Expected: List of matching companies with ticker symbols

**Test 3: Get Company Profile**
- Tool: `get_company_profile`
- Parameters: `{"symbol": "TSLA"}`
- Expected: Tesla company information, CEO, industry, etc.

✅ **Success**: If all tools work in MCP Inspector, your server is ready for deployment!

---

## Part 3: Deploy to Azure App Service

### Step 1: Login to Azure

```bash
az login
```

### Step 2: Create Azure Resources

```bash
# Set variables
$resourceGroup = "rg-fmp-mcp-server"
$appName = "fmp-mcp-server-<unique-id>"  # Replace <unique-id> with random numbers
$location = "eastus"

# Create resource group
az group create --name $resourceGroup --location $location

# Create App Service plan (Free tier)
az appservice plan create `
  --name "$appName-plan" `
  --resource-group $resourceGroup `
  --sku B1 `
  --is-linux

# Create web app
az webapp create `
  --resource-group $resourceGroup `
  --plan "$appName-plan" `
  --name $appName `
  --runtime "PYTHON:3.11"
```

### Step 3: Configure App Settings

```bash
# Set environment variables
az webapp config appsettings set `
  --resource-group $resourceGroup `
  --name $appName `
  --settings FMP_API_KEY="your_actual_api_key_here" WEBSITES_PORT=8000

# Configure startup command
az webapp config set `
  --resource-group $resourceGroup `
  --name $appName `
  --startup-file "uvicorn server:app --host 0.0.0.0 --port 8000"
```

### Step 4: Deploy Your Code

```bash
# Create deployment package
Compress-Archive -Path server.py,requirements.txt,.env -DestinationPath deploy.zip -Force

# Deploy via zip
az webapp deployment source config-zip `
  --resource-group $resourceGroup `
  --name $appName `
  --src deploy.zip

# Restart the app
az webapp restart --resource-group $resourceGroup --name $appName
```

### Step 5: Verify Deployment

```bash
# Get the URL
az webapp show --resource-group $resourceGroup --name $appName --query defaultHostName -o tsv
```

Your MCP endpoint will be: `https://<app-name>.azurewebsites.net/mcp/`

---

## Part 4: Test Deployment with Postman

### Step 1: Create a New Request in Postman

**Request Setup:**
- **Method**: POST
- **URL**: `https://<your-app-name>.azurewebsites.net/mcp/`
- **Headers**:
  ```
  Accept: application/json, text/event-stream
  Content-Type: application/json
  ```

### Step 2: Test - List Available Tools

**Body (raw JSON)**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

**Expected Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "search_symbol",
        "description": "Stock Symbol Search...",
        "inputSchema": {...}
      },
      ...
    ]
  }
}
```

### Step 3: Test - Call a Tool

**Body (raw JSON)**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_quote",
    "arguments": {
      "symbol": "AAPL"
    }
  }
}
```

**Expected Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[{\"symbol\":\"AAPL\",\"price\":175.43,...}]"
      }
    ]
  }
}
```

✅ **Success**: If Postman returns proper JSON-RPC responses, your server is working correctly on Azure!

---

## Part 5: Integrate with Copilot Studio

### Step 1: Create a New Agent

1. Go to [Copilot Studio](https://copilotstudio.microsoft.com/)
2. Click **Create** → **New Agent**
3. Name your agent (e.g., "FMP Financial Expert")
4. Click **Create**

### Step 2: Add MCP Server as a Tool

1. In your agent, go to **Actions** → **Add an action**
2. Select **Model Context Protocol server (Preview)**
3. Fill in the form:

   - **Server name**: `FMP Server`
   - **Server description**: `Financial Modeling Prep data server providing stock quotes, company profiles, income statements, balance sheets, and financial metrics for US stocks`
   - **Server URL**: `https://<your-app-name>.azurewebsites.net/mcp/`
   - **Authentication**: Select **None** (API key is in server environment)

4. Click **Create**

### Step 3: Wait for Discovery

Copilot Studio will automatically:
- Connect to your MCP server
- Discover all 8 available tools
- Register them as actions in your agent

This takes 10-30 seconds.

### Step 4: Test Your Agent

In the Copilot Studio test pane, try these prompts:

- "What's the current stock price for Apple?"
- "Show me Microsoft's company profile"
- "Get Tesla's latest income statement"
- "Search for companies with 'bank' in their name"

The agent will automatically call the appropriate MCP tools and present the results!

### Step 5: Publish Your Agent

1. Click **Publish** in Copilot Studio
2. Choose your deployment channels (Teams, Web, etc.)
3. Your financial expert agent is now live!

---

## 🎉 Congratulations!

You've successfully:
✅ Built a custom MCP server with 8 financial data tools  
✅ Tested it locally with MCP Inspector  
✅ Deployed it to Azure App Service  
✅ Verified deployment with Postman  
✅ Integrated it with Copilot Studio as an AI agent tool  

Your agent can now answer financial questions using real-time market data!

---

## References

### Official Documentation
- [Building MCP Servers](https://modelcontextprotocol.io/docs/develop/build-server) - MCP server development guide
- [MCP Inspector Tool](https://modelcontextprotocol.io/docs/tools/inspector) - Local testing tool documentation
- [Azure MCP Sample with Auth](https://github.com/Azure-Samples/remote-mcp-webapp-python-auth) - Azure deployment reference
- [Copilot Studio MCP Integration](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp) - Adding MCP servers to agents

### Additional Resources
- [Financial Modeling Prep API Docs](https://site.financialmodelingprep.com/developer/docs) - FMP API reference
- [Azure App Service Documentation](https://learn.microsoft.com/azure/app-service/) - Azure hosting guide
- [FastMCP Framework](https://github.com/jlowin/fastmcp) - Python MCP framework

---

## Troubleshooting

### Server Won't Start Locally
- Check Python version: `python --version` (needs 3.11+)
- Verify API key is set in `.env` file
- Ensure all dependencies installed: `pip install -r requirements.txt`

### Azure Deployment Issues
- Check logs: `az webapp log tail --resource-group <rg> --name <app-name>`
- Verify startup command is correct
- Ensure `WEBSITES_PORT` is set to 8000

### Copilot Studio Connection Fails
- Test URL in Postman first
- Ensure URL ends with `/mcp/`
- Check Azure app is running: `az webapp show --name <app-name> --query state`

### MCP Inspector Can't Connect
- Verify server is running on port 8000
- Check firewall isn't blocking localhost:8000
- Try accessing http://localhost:8000/mcp/ in browser

---

**Questions or Issues?** Open an issue on GitHub or refer to the [MCP documentation](https://modelcontextprotocol.io/).

**Happy Building! 🚀**

## Testing Strategy

### Stage 1: Local Testing with MCP Inspector

Test the server locally to verify all tools work correctly.

**Start the server:**
```bash
python server.py
```

**In a separate terminal, use MCP Inspector:**
```bash
npx @modelcontextprotocol/inspector python server.py
```

**Testing checklist:**
- ✅ Server initializes successfully
- ✅ All 8 tools appear in the tools list
- ✅ Test `search_symbol` with query: "Apple"
- ✅ Test `search_name` with query: "Microsoft"
- ✅ Test `get_quote` with symbol: "AAPL"
- ✅ Test `get_historical_prices` with symbol: "MSFT"
- ✅ Test `get_company_profile` with symbol: "TSLA"
- ✅ Test `get_income_statement` with symbol: "GOOGL", period: "annual"
- ✅ Test `get_balance_sheet` with symbol: "AMZN", period: "quarter"
- ✅ Test `get_cash_flow` with symbol: "NVDA"
- ✅ Verify error handling with invalid symbol: "INVALID123"

**Expected behavior:**
- All tools return JSON data from FMP API
- Errors are properly caught and returned as MCP errors
- Logs show API calls and responses

### Stage 2: Azure Deployment

Deploy to Azure App Service for cloud hosting.

**Create Azure App Service:**
```bash
# Login to Azure
az login

# Create resource group
az group create --name fmp-mcp-rg --location eastus

# Create App Service plan (Linux, Python 3.11)
az appservice plan create \
  --name fmp-mcp-plan \
  --resource-group fmp-mcp-rg \
  --is-linux \
  --sku B1

# Create web app
az webapp create \
  --resource-group fmp-mcp-rg \
  --plan fmp-mcp-plan \
  --name fmp-mcp-server \
  --runtime "PYTHON:3.11"

# Configure API key as environment variable
az webapp config appsettings set \
  --resource-group fmp-mcp-rg \
  --name fmp-mcp-server \
  --settings FMP_API_KEY="your_api_key_here"

# Set startup command
az webapp config set \
  --resource-group fmp-mcp-rg \
  --name fmp-mcp-server \
  --startup-file "startup.txt"

# Deploy code
az webapp up \
  --resource-group fmp-mcp-rg \
  --name fmp-mcp-server \
  --runtime "PYTHON:3.11"
```

**Alternative: Deploy via VS Code:**
1. Install Azure App Service extension
2. Right-click on workspace folder
3. Select "Deploy to Web App"
4. Follow prompts to create/select App Service
5. After deployment, add `FMP_API_KEY` in Azure Portal → Configuration → Application Settings

**Verify deployment:**
```bash
# Check if app is running
az webapp browse --resource-group fmp-mcp-rg --name fmp-mcp-server

# View logs
az webapp log tail --resource-group fmp-mcp-rg --name fmp-mcp-server
```

### Stage 3: Testing with Postman

Test the deployed Azure endpoint using Postman to verify HTTP transport.

**Get your Azure URL:**
```
https://fmp-mcp-server.azurewebsites.net
```

**Test 1: Initialize**
```http
POST https://fmp-mcp-server.azurewebsites.net/
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "postman",
      "version": "1.0.0"
    }
  }
}
```

**Expected response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "FMP Financial Data Connector",
      "version": "1.0.0"
    }
  }
}
```

**Test 2: List Tools**
```http
POST https://fmp-mcp-server.azurewebsites.net/
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**Expected response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "search_symbol",
        "description": "Stock Symbol Search - Use when you have a company name...",
        "inputSchema": {
          "type": "object",
          "properties": {
            "query": {
              "type": "string"
            }
          },
          "required": ["query"]
        }
      },
      // ... 7 more tools
    ]
  }
}
```

**Test 3: Call Tool (Get Quote)**
```http
POST https://fmp-mcp-server.azurewebsites.net/
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_quote",
    "arguments": {
      "symbol": "AAPL"
    }
  }
}
```

**Expected response:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[{\"symbol\":\"AAPL\",\"price\":185.50,\"volume\":52000000,...}]"
      }
    ]
  }
}
```

**Postman Testing Checklist:**
- ✅ `initialize` method works
- ✅ `tools/list` returns all 8 tools
- ✅ `tools/call` with `search_symbol` (query: "Tesla")
- ✅ `tools/call` with `get_quote` (symbol: "AAPL")
- ✅ `tools/call` with `get_company_profile` (symbol: "MSFT")
- ✅ `tools/call` with `get_income_statement` (symbol: "GOOGL")
- ✅ Error handling: Call with invalid symbol
- ✅ Response times are reasonable (<2 seconds)

### Stage 4: Copilot Studio Integration

Connect the MCP server to Copilot Studio.

**Add MCP Server to Copilot Studio:**

1. **Open Copilot Studio** (https://copilotstudio.microsoft.com)

2. **Navigate to your Copilot:**
   - Select or create a copilot
   - Go to "Settings" → "Advanced" → "Model Context Protocol"

3. **Register MCP Server:**
   - Click "Add MCP Server"
   - Enter details:
     - **Name:** FMP Financial Data
     - **URL:** `https://fmp-mcp-server.azurewebsites.net`
     - **Transport:** HTTP/Streamable
     - **Authentication:** None (API key is server-side)
   - Save configuration

4. **Verify Tools Discovery:**
   - Check that all 8 tools appear in Copilot Studio
   - Review tool descriptions and parameters

**Test with Natural Language:**

Ask your Copilot these questions:

1. **Symbol Search:**
   - "Find the stock symbol for Apple"
   - "What's the ticker for Microsoft?"

2. **Stock Quote:**
   - "What's the current price of AAPL?"
   - "Get me a quote for Tesla stock"

3. **Company Profile:**
   - "Tell me about Microsoft as a company"
   - "What industry is Apple in?"

4. **Historical Data:**
   - "Show me historical prices for NVDA"
   - "Get price history for Amazon"

5. **Financial Statements:**
   - "Show me Apple's income statement"
   - "What's Microsoft's latest balance sheet?"
   - "Get Tesla's cash flow statement"

6. **Complex Queries:**
   - "Compare the revenue of Apple and Microsoft"
   - "What's the PE ratio of Google?"
   - "Show me quarterly earnings for Amazon"

**Copilot Studio Testing Checklist:**
- ✅ All 8 tools discovered by Copilot Studio
- ✅ Natural language triggers correct tool calls
- ✅ Responses are formatted properly in chat
- ✅ Multi-turn conversations work (follow-up questions)
- ✅ Error messages are user-friendly
- ✅ Multiple symbols can be queried in same conversation
- ✅ Financial data is accurate and up-to-date

## Troubleshooting

### Local Testing Issues

**Server won't start:**
```bash
# Check Python version
python --version  # Should be 3.11+

# Verify dependencies
pip install -r requirements.txt --upgrade

# Check API key
echo $env:FMP_API_KEY  # PowerShell
echo $FMP_API_KEY      # bash
```

**API calls fail:**
- Verify FMP API key is correct
- Check API key has not exceeded rate limits (250 calls/day for free tier)
- Test API directly: `https://financialmodelingprep.com/stable/quote?symbol=AAPL&apikey=YOUR_KEY`

### Azure Deployment Issues

**Deployment fails:**
```bash
# Check deployment logs
az webapp log tail --resource-group fmp-mcp-rg --name fmp-mcp-server

# Check app settings
az webapp config appsettings list --resource-group fmp-mcp-rg --name fmp-mcp-server

# Restart app
az webapp restart --resource-group fmp-mcp-rg --name fmp-mcp-server
```

**App starts but tools don't work:**
- Verify `FMP_API_KEY` is set in Application Settings (Azure Portal)
- Check startup command is: `python -m uvicorn server:app --host 0.0.0.0 --port 8000`
- Review application logs in Azure Portal

### Copilot Studio Issues

**Tools not discovered:**
- Verify MCP server URL is accessible from internet
- Check Azure App Service is running (not stopped)
- Test server with Postman first
- Ensure URL uses HTTPS (Azure provides this by default)

**Tool calls fail:**
- Check Azure logs for errors
- Verify FMP API key is valid and has remaining quota
- Test individual tools with Postman to isolate issue

## API Rate Limits

**FMP Free Tier:**
- 250 API calls per day
- Rate limit resets at midnight UTC

**Recommendations:**
- Monitor usage in Azure Application Insights
- Consider upgrading to paid FMP tier for production use
- Implement caching for frequently requested data (future enhancement)

## Project Structure

```
FMP_MCP_VSCode/
├── server.py              # Main MCP server implementation
├── requirements.txt       # Python dependencies
├── startup.txt           # Azure startup command
├── package.json          # Node.js metadata (for MCP Inspector)
├── .env.example          # Example environment variables
├── .env                  # Your API keys (git-ignored)
├── .gitignore           # Git ignore patterns
├── .vscode/
│   └── launch.json      # VS Code debug configuration
└── README.md            # This file
```

## Development

**Run in development mode:**
```bash
python server.py
```

**Debug in VS Code:**
1. Set breakpoints in [server.py](server.py)
2. Press F5 or Run → Start Debugging
3. Use MCP Inspector to trigger tool calls

## Security Notes

- Never commit `.env` file with real API keys
- Use Azure Key Vault for production API key storage
- Consider implementing authentication for the MCP server endpoint
- Monitor and set rate limiting in Azure App Service

## Support & Resources

- **FMP API Docs:** https://site.financialmodelingprep.com/developer/docs
- **MCP Protocol:** https://modelcontextprotocol.io
- **MCP Python SDK:** https://github.com/modelcontextprotocol/python-sdk
- **Copilot Studio MCP:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-create-new-server

## License

MIT License - Feel free to modify and use for your projects.

## Next Steps

1. ✅ Complete local testing with MCP Inspector
2. ✅ Deploy to Azure App Service
3. ✅ Validate with Postman
4. ✅ Integrate with Copilot Studio
5. 🚀 Build amazing financial copilot experiences!
