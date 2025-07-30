from pydantic import BaseModel
from typing import Optional


class TokenResponse(BaseModel):
    """Token response from TOS backend"""
    token: str


class TokenRequest(BaseModel):
    """Token request to TOS backend"""