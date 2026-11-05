from typing import List, Optional

from pydantic import BaseModel, Field


class MMCRAGRequestDTO(BaseModel):
    query: str = Field(..., description="La consulta del usuario (min 10 caracters)", min_length=10)



class MMCRAGResponseDTO(BaseModel):
    images: Optional[List[str]]
    content: Optional[str]
    error: Optional[bool]
    cause: Optional[str]
    http_status_code: int
