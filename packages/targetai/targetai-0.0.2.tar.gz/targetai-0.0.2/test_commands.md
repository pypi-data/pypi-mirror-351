# Test Commands for TargetAI Token Server

After starting demo.py, run these commands in another terminal:

## 1. Health Check
```bash
curl http://localhost:8001/health
```

## 2. Server Information
```bash
curl http://localhost:8001/
```

## 3. Get Token
```bash
curl -X POST http://localhost:8001/token
```

## 4. Swagger UI Documentation
Open in browser: http://localhost:8001/docs

## 5. Detailed Output Check
```bash
# Simple token request
curl -v -X POST http://localhost:8001/token
```

## Expected Responses:

### Successful Response:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Error 401 (Invalid API Key):
```json
{
  "detail": "Invalid API key: ..."
}
```

### Error 429 (Rate Limit Exceeded):
```json
{
  "detail": "Rate limit exceeded: ..."
}
```

### Health Check Response:
```json
{
  "status": "healthy",
  "service": "targetai-token-server"
}
```

## Demo Configuration

By default, TOS backend `https://app.targetai.ai` is used.

To change settings, edit demo.py:
- `TOS_BASE_URL` - leave None for default URL or specify your URL
- `API_KEY` - your API key for TOS backend (optional)
- `PORT` - server port (default 8001)

### Example Custom Settings:
```python
# In demo.py change:
TOS_BASE_URL = "https://your-custom-tos.example.com"  # Your URL
API_KEY = "your-tos-api-key"  # Your API key for TOS backend
```

## Notes:
- The server no longer accepts client API keys via X-API-Key header
- All requests use the server's configured API key for TOS backend
- If no API key is configured, requests will be made without authentication 