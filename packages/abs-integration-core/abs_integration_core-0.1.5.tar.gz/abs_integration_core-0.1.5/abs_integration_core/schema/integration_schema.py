from abs_repository_core.schemas import ModelBaseInfo, make_optional
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime
    
    class Config:
        extra = "allow"


class Integration(make_optional(ModelBaseInfo), TokenData):
    provider_name: str


class IsConnectedResponse(BaseModel):
    provider: str
    connected: bool
    
    class Config:
        extra = "allow"


class CreateIntegration(BaseModel):
    """Model for creating a new integration"""
    provider_name: str
    access_token: str
    refresh_token: str
    expires_at: datetime


class UpdateIntegration(BaseModel):
    """Model for updating an existing integration"""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None

    class Config:
        extra = "ignore"
