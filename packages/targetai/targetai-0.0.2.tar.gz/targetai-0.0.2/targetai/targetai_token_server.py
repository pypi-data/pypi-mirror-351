import asyncio
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from .targetai_token_client import TargetAITokenClient, TargetAITokenClientError
from .schemas import TokenResponse


class TargetAITokenServerError(Exception):
    """Base exception for TargetAITokenServer errors"""
    pass


class TargetAITokenServer:
    """
    HTTP server for providing token distribution endpoints.
    
    Creates FastAPI application with /token endpoint that proxies
    requests to TOS backend and returns tokens to clients.
    """
    
    def __init__(self, 
                 tos_base_url: str = "https://app.targetai.ai", 
                 api_key: Optional[str] = None,
                 host: str = "0.0.0.0",
                 port: int = 8001):
        """
        Initialize the server.
        
        Args:
            tos_base_url: URL of TOS backend for token retrieval (default: https://app.targetai.ai)
            api_key: API key for TOS backend (optional)
            host: Host to bind the server
            port: Port to bind the server
        """
        self.tos_base_url = tos_base_url
        self.api_key = api_key
        self.host = host
        self.port = port
        
        # Create FastAPI application
        self.app = FastAPI(
            title="TargetAI Token Server",
            description="Server for issuing tokens from TOS backend",
            version="1.0.0"
        )
        
        # Create client for TOS backend
        self.token_client = TargetAITokenClient(tos_base_url, api_key)
        
        # Setup routes
        self._setup_routes()
        
        # Uvicorn server
        self._server = None

    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.post("/token", response_model=TokenResponse)
        async def generate_token(request: Request) -> TokenResponse:
            """
            Endpoint for token retrieval.
            
            Uses the server's configured API key for TOS backend authentication.
            """
            try:
                async with self.token_client:
                    token_response = await self.token_client.get_token()
                    return token_response
                    
            except TargetAITokenClientError as e:
                # Convert client errors to HTTP errors
                if "Invalid API key" in str(e):
                    raise HTTPException(status_code=401, detail=str(e))
                elif "Rate limit exceeded" in str(e):
                    raise HTTPException(status_code=429, detail=str(e))
                else:
                    raise HTTPException(status_code=500, detail=f"Token retrieval error: {str(e)}")

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "service": "targetai-token-server"}

        @self.app.get("/")
        async def root():
            """Root endpoint with service information"""
            return {
                "service": "TargetAI Token Server",
                "version": "1.0.0",
                "endpoints": {
                    "token": "POST /token - get token",
                    "health": "GET /health - health check"
                }
            }

    async def start(self):
        """
        Start the server.
        
        Raises:
            TargetAITokenServerError: On server startup errors
        """
        try:
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
            self._server = uvicorn.Server(config)
            
            print(f"🚀 Starting TargetAI Token Server on http://{self.host}:{self.port}")
            print(f"📡 TOS Backend: {self.tos_base_url}")
            print(f"🔑 API Key: {'✅ configured' if self.api_key else '❌ not configured'}")
            print(f"📖 Documentation: http://{self.host}:{self.port}/docs")
            
            await self._server.serve()
            
        except Exception as e:
            raise TargetAITokenServerError(f"Server startup error: {str(e)}")

    async def stop(self):
        """Stop the server"""
        if self._server:
            self._server.should_exit = True
            await self.token_client.close()

    def run(self):
        """Synchronous server startup (blocking)"""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            print("\n🛑 Server stopped...")
        except Exception as e:
            print(f"❌ Error: {e}")

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop() 