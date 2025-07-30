import aiohttp
from typing import Optional
from .schemas import TokenResponse


class TargetAITokenClientError(Exception):
    """Base exception for TargetAITokenClient errors"""
    pass


class TargetAITokenClient:
    """
    Client for retrieving tokens from TOS backend.
    
    Used for requesting tokens with or without API key.
    """
    
    def __init__(self, tos_base_url: str = "https://app.targetai.ai", api_key: Optional[str] = None):
        """
        Initialize the client.
        
        Args:
            tos_base_url: Base URL of TOS backend (default: https://app.targetai.ai)
            api_key: API key for authentication (optional)
        """
        self.tos_base_url = tos_base_url.rstrip('/')
        self.api_key = api_key
        self._session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        """Ensures HTTP session exists"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

    async def get_token(self) -> TokenResponse:
        """
        Retrieves token from TOS backend.
        
        Returns:
            TokenResponse: Object with token
            
        Raises:
            TargetAITokenClientError: On token retrieval errors
        """
        await self._ensure_session()
        
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        url = f"{self.tos_base_url}/api/token/generate"
        
        try:
            async with self._session.post(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return TokenResponse(token=data["token"])
                elif response.status == 401:
                    error_text = await response.text()
                    raise TargetAITokenClientError(f"Invalid API key: {error_text}")
                elif response.status == 429:
                    error_text = await response.text()
                    raise TargetAITokenClientError(f"Rate limit exceeded: {error_text}")
                else:
                    error_text = await response.text()
                    raise TargetAITokenClientError(f"Token retrieval error ({response.status}): {error_text}")
                    
        except aiohttp.ClientError as e:
            raise TargetAITokenClientError(f"Network error during token retrieval: {str(e)}")

    async def close(self):
        """Closes HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    def __del__(self):
        """Resource cleanup on object deletion"""
        if self._session and not self._session.closed:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
                else:
                    loop.run_until_complete(self.close())
            except:
                pass  # Ignore cleanup errors 