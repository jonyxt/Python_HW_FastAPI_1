# app/schemas.py
from pydantic import BaseModel


class CreateAdvRequest(BaseModel):
    title: str
    description: str
    price: int
    owner: str

class CreateAdvResponse(BaseModel):
    id: int

class GetAdvResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    owner: str
    created_at: str

class UpdateAdvRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    owner: str | None = None

class UpdateAdvResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    owner: str
    created_at: str

class OKResponse(BaseModel):
    status: str = 'ok'