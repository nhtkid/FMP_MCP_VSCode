#+#+#+#+######################################################################
# FMP MCP Server (Copilot Studio)
#+#+#+#+######################################################################

An HTTP **Model Context Protocol (MCP)** server that exposes Financial Modeling Prep (FMP) market-data endpoints as MCP tools so **Microsoft Copilot Studio** can discover and call them.

## What you get

- **8 MCP tools** backed by the FMP API:
  - `search_symbol`, `search_name`
  - `get_quote`, `get_historical_prices`
  - `get_company_profile`
  - `get_income_statement`, `get_balance_sheet`, `get_cash_flow`
- **Streamable HTTP** transport at `POST /mcp/` (JSON-RPC)
- Designed for **Copilot Studio tool discovery** (stateless HTTP)

## Prerequisites

- Python 3.11+
- An FMP API key (free tier available): https://site.financialmodelingprep.com/developer/docs
- Optional (for local UI testing): Node.js 18+ (MCP Inspector)

## Quickstart (local)

1) Install deps

```powershell
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

2) Configure your API key

```powershell
Copy-Item .env.example .env
# Edit .env and set FMP_API_KEY
```

3) Run the server

```powershell
python server.py
```

It will listen on:

- `http://localhost:8000/mcp/`

### Test with MCP Inspector (HTTP mode)

```powershell
npx @modelcontextprotocol/inspector
```

In the Inspector UI:

- Transport: **Streamable HTTP**
- URL: `http://localhost:8000/mcp/`

### Test with curl (tools/list)

```bash
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

## Deploy to Azure App Service (Linux)

High-level steps:

1) Create a Python 3.11 Linux Web App
2) Set app settings:
   - `FMP_API_KEY` (do not deploy your `.env`)
   - `WEBSITES_PORT=8000`
3) Set startup command:

```text
python -m uvicorn server:app --host 0.0.0.0 --port 8000
```

### Why `deploy.zip` exists

This repo is commonly deployed using **Azure App Service Zip Deploy** (`az webapp deployment source config-zip`).

- `deploy.zip` is a **local deployment artifact** created by packaging the files you want to upload.
- The Azure CLI uploads that zip to the Web App, App Service unpacks it, then builds/installs dependencies.
- `deploy.zip` is intentionally **gitignored** (it should not be committed).

This repo includes a `.deployment` file that sets `SCM_DO_BUILD_DURING_DEPLOYMENT=true`, which tells App Service to run a build during deployment (e.g., install from `requirements.txt`).

Example (PowerShell):

```powershell
Remove-Item deploy.zip -Force -ErrorAction SilentlyContinue
Compress-Archive -Path .deployment,requirements.txt,server.py,README.md -DestinationPath deploy.zip -Force

az webapp deployment source config-zip `
  --resource-group <rg> `
  --name <app-name> `
  --src .\deploy.zip
```

Your MCP endpoint will be:

- `https://<your-app-name>.azurewebsites.net/mcp/`

## Test the deployed endpoint (Postman)

- Method: `POST`
- URL: `https://<your-app-name>.azurewebsites.net/mcp/`
- Headers:
  - `Accept: application/json, text/event-stream`
  - `Content-Type: application/json`

**List tools**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

**Call a tool**

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

More examples: see `POSTMAN_TESTING.md`.

## Copilot Studio setup

1) In Copilot Studio, add an action: **Model Context Protocol server (Preview)**
2) Use your server URL (must end with `/mcp/`)
3) Authentication: **None** (the FMP API key is configured server-side)
4) Wait for tool discovery, then test prompts like:
   - "What is the current stock price of MSFT?"
   - "Show me the latest annual income statement for AAPL"

## Repo notes

- `server.py` is the **HTTP** MCP server used for Azure deployment.
- `server_stdio.py` is a **STDIO** variant intended for local testing scenarios that require STDIO transport.


## Troubleshooting

- If API calls fail, confirm `FMP_API_KEY` is set and you have remaining quota.
- If Copilot Studio can’t discover tools, first verify `tools/list` works against the public `/mcp/` URL.

## References

- MCP: https://modelcontextprotocol.io/
- Copilot Studio MCP: https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp
- FMP docs: https://site.financialmodelingprep.com/developer/docs

