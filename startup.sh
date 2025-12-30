#!/bin/bash
# Startup script for Azure App Service

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Start the server using uvicorn
python -m uvicorn server:mcp.run_with_cors --host 0.0.0.0 --port 8000
