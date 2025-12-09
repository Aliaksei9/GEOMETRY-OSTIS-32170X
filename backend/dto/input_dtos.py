from typing import Optional, List, Union
from pydantic import BaseModel

class LengthInput(BaseModel):
    way_of_measurement: str
    value: Union[float, str]

class AngleInput(BaseModel):
    way_of_measurement: str
    value: Union[float, str]

class EdgeInput(BaseModel):
    vert1: str
    vert2: str
    length: Optional[LengthInput] = None

class PolygonInput(BaseModel):
    name: Optional[str] = None
    type: str
    vertices: Optional[List[str]] = None
    edges: Optional[List[EdgeInput]] = None

class CircleInput(BaseModel):
    name: Optional[str] = None
    type: str = "circle"
    center: str
    diameter: Optional[EdgeInput] = None

class ConstructionElementInput(BaseModel):
    type: str
    vert1: Optional[str] = None
    vert2: Optional[str] = None
    vert3: Optional[str] = None
    name: Optional[str] = None
    angle: Optional[AngleInput] = None

class RelationshipInput(BaseModel):
    type: str 
    name: str
    source_entity: str
    target_entity: str
    oriented: bool = True 

class ConstructionElementsContainerInput(BaseModel):
    construction_elements: List[ConstructionElementInput]

class ComplexConstructionInput(BaseModel):
    name: str
    figures: List[Union[PolygonInput, CircleInput, ConstructionElementsContainerInput]]
    relationships: List[RelationshipInput]