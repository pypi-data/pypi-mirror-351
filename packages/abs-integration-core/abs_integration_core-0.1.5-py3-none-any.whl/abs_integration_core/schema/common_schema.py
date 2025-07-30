from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
from fastapi import status

T = TypeVar('T')


class ResponseSchema(BaseModel, Generic[T]):
    """
    Standard response schema for all API endpoints
    """
    status: int = status.HTTP_200_OK
    message: str = "Success"
    data: Optional[T] = None

    class Config:
        arbitrary_types_allowed = True
