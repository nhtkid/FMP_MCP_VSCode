# Building an MCP Server for Copilot Studio

## Complete Lab Guide: Create, Host, and Use an MCP Server

Build a **Model Context Protocol (MCP) server**, host it on **Azure App Service**, and integrate it with **Microsoft Copilot Studio**.

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
- MCP server wrapping the Financial Modeling Prep (FMP) API with 8 financial data tools
- Cloud-hosted server on Azure for production use
- AI agent in Copilot Studio that answers financial questions using your MCP server

**What is MCP?**  
Model Context Protocol standardizes how applications provide context to LLMs, enabling AI assistants to securely access data and tools.

---

## Prerequisites

### Required Tools
- **VS Code** - [Download](https://code.visualstudio.com/)
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/) (for MCP Inspector)
- **Azure CLI** - [Install](https://learn.microsoft.com/cli/azure/install-azure-cli)
- **Postman** - [Download](https://www.postman.com/downloads/)
- **Git** - [Download](https://git-scm.com/downloads)

### Required Accounts
- **FMP API Key** - Free tier available at [financialmodelingprep.com](https://site.financialmodelingprep.com/developer/docs)
- **Azure Subscription** - [Free account](https://azure.microsoft.com/free/)
- **Microsoft Copilot Studio** - [Access here](https://copilotstudio.microsoft.com/)

---

## Part 1: Build the MCP Server

### Step 1: Set Up Project

```bash
# Create and navigate to project directory
mkdir fmp-mcp-server && cd fmp-mcp-server
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

Install:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
cp .env.example .env
# Edit .env and add your FMP API key
```

### Step 4: Understand the Server

The `server.py` implements 8 financial tools:
- `search_symbol`, `search_name` - Search stocks/companies
- `get_quote` - Real-time stock quotes
- `get_historical_prices` - Historical data
- `get_company_profile` - Company information
- `get_income_statement`, `get_balance_sheet`, `get_cash_flow` - Financial statements

**Key features**: Stateless HTTP mode, error handling, detailed tool descriptions for AI.

---

## Part 2: Test Locally with MCP Inspector

### Start Server
```bash
python server.py
# Server runs on http://localhost:8000/mcp/
```

### Launch MCP Inspector
```bash
npx @modelcontextprotocol/inspector
# Opens in browser at http://localhost:5173
```

### Connect and Test
1. **Transport**: Streamable HTTP
2. **URL**: `http://localhost:8000/mcp/`
3. **Click Connect**

Test examples:
- `get_quote` with `{"symbol": "AAPL"}`
- `search_name` with `{"query": "Microsoft"}`
- `get_company_profile` with `{"symbol": "TSLA"}`

✅ All tools working? Ready for deployment!

---

## Part 3: Deploy to Azure App Service

### Create Resources
```bash
az login

# Set variables
$resourceGroup = "rg-fmp-mcp-server"
$appName = "fmp-mcp-server-<unique-id>"  # Use random numbers
$location = "eastus"

# Create resource group and app service
az group create --name $resourceGroup --location $location

az appservice plan create `
  --name "$appName-plan" `
  --resource-group $resourceGroup `
  --sku B1 `
  --is-linux

az webapp create `
  --resource-group $resourceGroup `
  --plan "$appName-plan" `
  --name $appName `
  --runtime "PYTHON:3.11"
```

### Configure App
```bash
# Set environment variables
az webapp config appsettings set `
  --resource-group $resourceGroup `
  --name $appName `
  --settings FMP_API_KEY="your_api_key" WEBSITES_PORT=8000

# Set startup command
az webapp config set `
  --resource-group $resourceGroup `
  --name $appName `
  --startup-file "uvicorn server:app --host 0.0.0.0 --port 8000"
```

### Deploy
```bash
Compress-Archive -Path server.py,requirements.txt,.env -DestinationPath deploy.zip -Force

az webapp deployment source config-zip `
  --resource-group $resourceGroup `
  --name $appName `
  --src deploy.zip

az webapp restart --resource-group $resourceGroup --name $appName
```

Your MCP endpoint: `https://<app-name>.azurewebsites.net/mcp/`

---

## Part 4: Test Deployment with Postman

### Setup Request
- **Method**: POST
- **URL**: `https://<your-app-name>.azurewebsites.net/mcp/`
- **Headers**:
  ```
  Accept: application/json, text/event-stream
  Content-Type: application/json
  ```

### Test 1: List Tools
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

### Test 2: Call a Tool
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_quote",
    "arguments": {"symbol": "AAPL"}
  }
}
```

✅ Getting JSON-RPC responses? Server is working on Azure!

See [POSTMAN_TESTING.md](POSTMAN_TESTING.md) for detailed examples.

---

## Part 5: Integrate with Copilot Studio

### Create Agent
1. Go to [Copilot Studio](https://copilotstudio.microsoft.com/)
2. **Create** → **New Agent** → Name it "FMP Financial Expert"

### Add MCP Server
1. **Actions** → **Add an action** → **Model Context Protocol server (Preview)**
2. Fill in:
   - **Server name**: `FMP Server`
   - **Description**: `Financial data server for stock quotes, company profiles, and financial statements`
   - **URL**: `https://<your-app-name>.azurewebsites.net/mcp/`
   - **Authentication**: None
3. **Create** (discovery takes 10-30 seconds)

### Test Agent
Try these prompts:
- "What's the current stock price for Apple?"
- "Show me Microsoft's company profile"
- "Get Tesla's latest income statement"

### Publish
Click **Publish** and choose deployment channels (Teams, Web, etc.)

---

## 🎉 Congratulations!

You've successfully:
✅ Built an MCP server with 8 financial tools  
✅ Tested locally with MCP Inspector  
✅ Deployed to Azure App Service  
✅ Verified with Postman  
✅ Integrated with Copilot Studio  

---

## References

### Official Documentation
- [Building MCP Servers](https://modelcontextprotocol.io/docs/develop/build-server) - MCP server development guide
- [MCP Inspector Tool](https://modelcontextprotocol.io/docs/tools/inspector) - Local testing tool documentation
- [Azure MCP Sample with Auth](https://github.com/Azure-Samples/remote-mcp-webapp-python-auth) - Azure deployment reference
- [Copilot Studio MCP Integration](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp) - Adding MCP servers to agents

### APIs & Data Sources
- [Financial Modeling Prep (FMP)](https://financialmodelingprep.com/) - Real-time stock market data API
- [FMP API Documentation](https://site.financialmodelingprep.com/developer/docs) - Complete API reference and endpoints

### Additional Resources
- [Azure App Service Documentation](https://learn.microsoft.com/azure/app-service/) - Azure hosting guide
- [FastMCP Framework](https://github.com/jlowin/fastmcp) - Python MCP framework

---

## Troubleshooting

**Server won't start locally**
- Check Python version: `python --version` (needs 3.11+)
- Verify API key in `.env`
- Reinstall: `pip install -r requirements.txt`

**Azure deployment fails**
- View logs: `az webapp log tail --resource-group <rg> --name <app>`
- Verify `WEBSITES_PORT=8000` is set
- Check startup command is correct

**Copilot Studio can't connect**
- Test URL in Postman first
- Ensure URL ends with `/mcp/`
- Verify app is running on Azure

**MCP Inspector connection issues**
- Confirm server runs on port 8000
- Check firewall settings
- Try accessing http://localhost:8000/mcp/ in browser

---

**Questions?** Refer to the [MCP documentation](https://modelcontextprotocol.io/) or open an issue.

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
