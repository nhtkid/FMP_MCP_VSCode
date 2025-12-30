# FMP MCP Server for Copilot Studio

A **Model Context Protocol (MCP)** server that connects **Microsoft Copilot Studio** to the **Financial Modeling Prep (FMP) API**. This enables AI agents to access real-time stock data, historical prices, company profiles, and financial statements.

## 🚀 Features

Provides 8 financial tools for AI agents:
- **Search**: `search_symbol`, `search_name`
- **Market Data**: `get_quote`, `get_historical_prices`
- **Company Info**: `get_company_profile`
- **Financials**: `get_income_statement`, `get_balance_sheet`, `get_cash_flow`

## 📋 Prerequisites

- **Python 3.11+**
- **FMP API Key** (Get a free key at [financialmodelingprep.com](https://site.financialmodelingprep.com/developer/docs))
- **Azure CLI** (for deployment)
- **Azure Subscription**

## 📂 Project Structure

```
FMP_MCP_VSCode/
├── server.py              # Main MCP server implementation
├── requirements.txt       # Python dependencies
├── startup.sh             # Azure startup command
├── openapi-spec.yaml      # OpenAPI specification
├── .env                   # Environment variables (not committed)
└── README.md              # Documentation
```

## 🛠️ Local Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/nhtkid/FMP_MCP_VSCode.git
    cd FMP_MCP_VSCode
    ```

2.  **Install dependencies**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\Activate.ps1
    # macOS/Linux
    source venv/bin/activate
    
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```env
    FMP_API_KEY=your_api_key_here
    ```

4.  **Run Locally**
    ```bash
    python server.py
    ```
    The server will start at `http://localhost:8000/mcp/`.

## 🧪 Testing

You can use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to test the tools locally.

```bash
npx @modelcontextprotocol/inspector
```
- **Transport Type**: HTTP (SSE)
- **URL**: `http://localhost:8000/mcp/`

## ☁️ Deployment to Azure

1.  **Create Azure Resources**
    ```bash
    # Create Resource Group
    az group create --name rg-fmp-mcp --location eastus

    # Create App Service Plan
    az appservice plan create --name plan-fmp-mcp --resource-group rg-fmp-mcp --sku B1 --is-linux

    # Create Web App
    az webapp create --resource-group rg-fmp-mcp --plan plan-fmp-mcp --name <your-unique-app-name> --runtime "PYTHON:3.11"
    ```

2.  **Configure Settings**
    ```bash
    az webapp config appsettings set --resource-group rg-fmp-mcp --name <your-unique-app-name> --settings FMP_API_KEY=<your_key> SCM_DO_BUILD_DURING_DEPLOYMENT=true
    ```

3.  **Deploy Code**
    ```powershell
    # Windows PowerShell
    Compress-Archive -Path . -DestinationPath deploy.zip -Force
    az webapp deployment source config-zip --resource-group rg-fmp-mcp --name <your-unique-app-name> --src deploy.zip
    ```

## 🤖 Copilot Studio Integration

1.  Go to **Microsoft Copilot Studio**.
2.  Open your agent and navigate to **Actions**.
3.  Click **+ Add an action**.
4.  Select **"Add from URL"** (or "MCP Server").
5.  Enter your Azure App Service URL: `https://<your-unique-app-name>.azurewebsites.net/mcp/`.
6.  The server will be detected, and the 8 financial tools will be available for your agent.

## ❓ Troubleshooting

-   **Server won't start**: Check Python version (3.11+) and `FMP_API_KEY`.
-   **Deployment fails**: Check Azure logs: `az webapp log tail --resource-group rg-fmp-mcp --name <your-app-name>`.
-   **Tools not discovered**: Ensure the URL ends with `/mcp/` and is accessible publicly.

## 📚 Resources

-   [Financial Modeling Prep API Docs](https://site.financialmodelingprep.com/developer/docs)
-   [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
-   [Microsoft Copilot Studio](https://copilotstudio.microsoft.com/)

## License

MIT
