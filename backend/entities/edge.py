from pydantic import BaseModel, validator, model_validator
from typing import Optional

class Edge(BaseModel):
    vert1: str 
    vert2: str  
    length: Optional[float] = None

    @validator('vert1', 'vert2')
    def validate_vertex_not_null(cls, v) -> str:
        if v is None:
            raise ValueError("vertex cannot be null")
        return v

    @model_validator(mode='after')
    def validate_vertex_names(self):
        if self.vert1 == self.vert2:
            raise ValueError("Vertex names cannot be the same")
        return self

    @validator('length')
    def validate_length(cls, v) -> float:
        if v is not None and v <= 0:
            raise ValueError("length cannot be negative or zero")
        return v