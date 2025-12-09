from pydantic import BaseModel, validator, model_validator
from typing import Optional

class Point(BaseModel):
    name: str

    @validator('name')
    def validate_name(cls, name) -> str:
        if not name or not isinstance(name, str) or name.strip() == "":
            raise ValueError("Name cannot be empty")
        return name

class Edge(BaseModel):
    vert1: Point
    vert2: Point
    length: Optional[float] = None

    @validator('vert1', 'vert2')
    def validate_vertex_not_null(cls, v) -> Point:
        if v is None:
            raise ValueError("vertex cannot be null")
        return v

    @model_validator(mode='after')
    def validate_vertex_names(self):
        if self.vert1.name == self.vert2.name:
            raise ValueError("Vertex names cannot be the same")
        return self

    @validator('length')
    def validate_length(cls, v) -> float:
        if v is not None and v <= 0:
            raise ValueError("length cannot be negative or zero")
        return v