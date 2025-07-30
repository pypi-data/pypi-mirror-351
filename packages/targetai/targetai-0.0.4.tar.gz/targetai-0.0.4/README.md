# TargetAI Python SDK

Python SDK for working with TargetAI tokens. Provides simple tools for retrieving tokens from TOS backend and deploying token distribution endpoints.

## Installation

```bash
pip install targetai
```

## Quick Start

### TargetAITokenClient - Token Retrieval

```python
from targetai import TargetAITokenClient

# Simplest way - uses default URL https://app.targetai.ai
async def example_simple():
    async with TargetAITokenClient() as client:
        token_response = await client.get_token()
        print(f"Token: {token_response.token}")

# With API key
async def example_with_api_key():
    async with TargetAITokenClient(api_key="your-api-key") as client:
        token_response = await client.get_token()
        print(f"Token: {token_response.token}")

# With custom URL
async def example_custom_url():
    async with TargetAITokenClient("https://your-tos.example.com", api_key="your-api-key") as client:
        token_response = await client.get_token()
        print(f"Token: {token_response.token}")
```

### TargetAITokenServer - Token Distribution Server

```python
from targetai import TargetAITokenServer

# Simplest startup (uses default URL)
def run_server():
    server = TargetAITokenServer(port=8001)
    server.run()  # Blocking startup

# With API key for TOS backend
def run_server_with_key():
    server = TargetAITokenServer(api_key="your-tos-api-key", port=8001)
    server.run()

# With custom TOS backend URL
def run_server_custom():
    server = TargetAITokenServer(
        tos_base_url="https://your-tos.example.com",
        api_key="your-api-key",
        port=8001
    )
    server.run()

# Or asynchronously
async def run_server_async():
    async with TargetAITokenServer(port=8001) as server:
        await server.start()
```

After starting the server, the following endpoints are available:
- `POST /token` - token retrieval
- `GET /health` - health check
- `GET /docs` - Swagger documentation

## Using the /token endpoint

```bash
# Simple token request
curl -X POST http://localhost:8001/token

# Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## API Reference

### TargetAITokenClient

```python
class TargetAITokenClient:
    def __init__(self, 
                 tos_base_url: str = "https://app.targetai.ai",
                 api_key: Optional[str] = None)
    async def get_token(self) -> TokenResponse
    async def close(self)
```

### TargetAITokenServer

```python
class TargetAITokenServer:
    def __init__(self, 
                 tos_base_url: str = "https://app.targetai.ai", 
                 api_key: Optional[str] = None,
                 host: str = "0.0.0.0",
                 port: int = 8001)
    async def start(self)
    async def stop(self)
    def run(self)  # synchronous version
```

### Data Schemas

```python
class TokenResponse:
    token: str
```

## Error Handling

```python
from targetai import TargetAITokenClient, TargetAITokenClientError

try:
    async with TargetAITokenClient() as client:  # Uses default URL
        token = await client.get_token()
except TargetAITokenClientError as e:
    print(f"Error: {e}")
```

Possible errors:
- `TargetAITokenClientError` - base client error
- `TargetAITokenServerError` - base server error

## Requirements

- Python 3.8+
- aiohttp >= 3.8.0
- pydantic >= 2.0.0
- fastapi >= 0.100.0
- uvicorn >= 0.20.0

## License

MIT 