# TargetAI Python SDK - Installation & Quick Start

## 🚀 Quick Installation

```bash
cd sdk/python
pip install -e .
```

## ⚡ Quick Test

1. **Start the demo server:**
```bash
python demo.py
```

2. **In another terminal, test it:**
```bash
curl -X POST http://localhost:8001/token
```

3. **Check Swagger UI:**
Open http://localhost:8001/docs in your browser

## 📚 Usage Examples

### Simple Token Client
```python
from targetai import TargetAITokenClient

async def get_token():
    async with TargetAITokenClient() as client:
        token = await client.get_token()
        print(token.token)
```

### Simple Token Server
```python
from targetai import TargetAITokenServer

def run_server():
    server = TargetAITokenServer(port=8001)
    server.run()
```

## 🔧 Configuration

### Demo Server Settings
Edit `demo.py`:
- `TOS_BASE_URL` - TOS backend URL (default: https://app.targetai.ai)
- `API_KEY` - Your TOS API key (optional)
- `PORT` - Server port (default: 8001)

### Production Usage
```python
# With custom settings
server = TargetAITokenServer(
    tos_base_url="https://your-tos.example.com",
    api_key="your-api-key",
    host="0.0.0.0",
    port=8001
)
server.run()
```

## 📖 Documentation

- **README.md** - Full documentation
- **test_commands.md** - Test commands and examples
- **Swagger UI** - Available at http://localhost:8001/docs when server is running

## 🔑 Key Features

- ✅ Default TOS backend: https://app.targetai.ai
- ✅ Optional API key authentication
- ✅ Simple async/await client
- ✅ FastAPI server with automatic docs
- ✅ Health check endpoints
- ✅ Proper error handling 