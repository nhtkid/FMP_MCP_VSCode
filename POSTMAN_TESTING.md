# Testing the FMP MCP Server with Postman

This server exposes MCP **JSON-RPC** over **streamable HTTP** at `POST /mcp/`.

## What you need

- Your deployed endpoint, e.g. `https://<your-app-name>.azurewebsites.net/mcp/`
- Or local endpoint: `http://localhost:8000/mcp/`

## Postman request setup

- Method: `POST`
- URL: `https://<your-app-name>.azurewebsites.net/mcp/`
- Headers:

```
Accept: application/json, text/event-stream
Content-Type: application/json
```

## 1) List tools

Body (raw JSON):

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

## 2) Call a tool (examples)

### Search for a symbol

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "search_symbol",
    "arguments": {
      "query": "Apple"
    }
  }
}
```

### Get a quote

```json
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

### Get historical prices

Note: in this repo, `get_historical_prices` currently accepts **only** `symbol` and returns full end-of-day history from FMP.

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "get_historical_prices",
    "arguments": {
      "symbol": "AAPL"
    }
  }
}
```

### Financial statements (annual)

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "get_income_statement",
    "arguments": {
      "symbol": "AAPL",
      "period": "annual",
      "limit": 5
    }
  }
}
```

## Expected response shape

- Success responses return a `result.content` array.
- Each content entry is typically `{ "type": "text", "text": "..." }` containing JSON returned from FMP.

## Common issues

- `tools/list` works but tool calls fail: verify `FMP_API_KEY` is set on the server and the key has remaining quota.
- 5xx from Azure: check App Service logs and confirm the startup command is `python -m uvicorn server:app --host 0.0.0.0 --port 8000`.
```

---

### 6. Get Income Statement

**Method**: POST  
**URL**: `https://fmp-mcp-server-2917.azurewebsites.net/mcp/`  
**Headers**:
```
Accept: application/json, text/event-stream
Content-Type: application/json
```

**Body** (raw JSON):
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "get_income_statement",
    "arguments": {
      "symbol": "AAPL",
      "period": "annual",
      "limit": 5
    }
  }
}
```

---

### 7. Get Balance Sheet

**Method**: POST  
**URL**: `https://fmp-mcp-server-2917.azurewebsites.net/mcp/`  
**Headers**:
```
Accept: application/json, text/event-stream
Content-Type: application/json
```

**Body** (raw JSON):
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "get_balance_sheet",
    "arguments": {
      "symbol": "MSFT",
      "period": "annual",
      "limit": 3
    }
  }
}
```

---

### 8. Get Cash Flow Statement

**Method**: POST  
**URL**: `https://fmp-mcp-server-2917.azurewebsites.net/mcp/`  
**Headers**:
```
Accept: application/json, text/event-stream
Content-Type: application/json
```

**Body** (raw JSON):
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "tools/call",
  "params": {
    "name": "get_cash_flow",
    "arguments": {
      "symbol": "TSLA",
      "period": "quarter",
      "limit": 4
    }
  }
}
```

---

## Important Notes

### Setting Your FMP API Key
Before the MCP server can successfully call the FMP API, you need to set your actual API key:

```bash
az webapp config appsettings set \
  --resource-group rg-fmp-mcp-server \
  --name fmp-mcp-server-2917 \
  --settings FMP_API_KEY="YOUR_ACTUAL_FMP_API_KEY"
```

Replace `YOUR_ACTUAL_FMP_API_KEY` with your real API key from [Financial Modeling Prep](https://site.financialmodelingprep.com/developer/docs).

### Error Handling

If you receive errors, check:

1. **401 Unauthorized**: Your FMP_API_KEY is not set or invalid
2. **404 Not Found**: Check the endpoint URL is correct (should end with `/mcp/`)
3. **500 Internal Server Error**: Check the app logs with:
   ```bash
   az webapp log tail --resource-group rg-fmp-mcp-server --name fmp-mcp-server-2917
   ```

### View Logs
```bash
# Stream logs
az webapp log tail --resource-group rg-fmp-mcp-server --name fmp-mcp-server-2917

# Download logs
az webapp log download --resource-group rg-fmp-mcp-server --name fmp-mcp-server-2917
```

---

## Postman Collection

You can import all these requests as a Postman collection. Save this JSON as `FMP_MCP_Server.postman_collection.json`:

```json
{
  "info": {
    "name": "FMP MCP Server",
    "description": "Test collection for FMP Financial Data MCP Server",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "List Tools",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Accept",
            "value": "application/json, text/event-stream"
          },
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"jsonrpc\": \"2.0\",\n  \"id\": 1,\n  \"method\": \"tools/list\"\n}"
        },
        "url": {
          "raw": "https://fmp-mcp-server-2917.azurewebsites.net/mcp/",
          "protocol": "https",
          "host": ["fmp-mcp-server-2917", "azurewebsites", "net"],
          "path": ["mcp", ""]
        }
      }
    },
    {
      "name": "Search Symbol",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Accept",
            "value": "application/json, text/event-stream"
          },
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"jsonrpc\": \"2.0\",\n  \"id\": 2,\n  \"method\": \"tools/call\",\n  \"params\": {\n    \"name\": \"search_symbol\",\n    \"arguments\": {\n      \"query\": \"Apple\"\n    }\n  }\n}"
        },
        "url": {
          "raw": "https://fmp-mcp-server-2917.azurewebsites.net/mcp/",
          "protocol": "https",
          "host": ["fmp-mcp-server-2917", "azurewebsites", "net"],
          "path": ["mcp", ""]
        }
      }
    },
    {
      "name": "Get Quote",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Accept",
            "value": "application/json, text/event-stream"
          },
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"jsonrpc\": \"2.0\",\n  \"id\": 3,\n  \"method\": \"tools/call\",\n  \"params\": {\n    \"name\": \"get_quote\",\n    \"arguments\": {\n      \"symbol\": \"AAPL\"\n    }\n  }\n}"
        },
        "url": {
          "raw": "https://fmp-mcp-server-2917.azurewebsites.net/mcp/",
          "protocol": "https",
          "host": ["fmp-mcp-server-2917", "azurewebsites", "net"],
          "path": ["mcp", ""]
        }
      }
    }
  ]
}
```

---

## Next Steps

1. **Set your FMP API key** using the Azure CLI command above
2. **Import the Postman collection** or manually create the requests
3. **Test each endpoint** starting with "List Tools"
4. **Monitor logs** if you encounter any issues
5. **Integrate with Copilot Studio** or other MCP clients

## Resources
- [Azure App Service MCP Documentation](https://learn.microsoft.com/en-us/azure/app-service/overview-ai-integration?tabs=python#app-service-as-model-context-protocol-mcp-servers)
- [MCP Python Tutorial](https://learn.microsoft.com/en-us/azure/app-service/tutorial-ai-model-context-protocol-server-python)
- [Sample MCP Server with Auth](https://github.com/Azure-Samples/remote-mcp-webapp-python-auth)
- [Financial Modeling Prep API](https://site.financialmodelingprep.com/developer/docs)
