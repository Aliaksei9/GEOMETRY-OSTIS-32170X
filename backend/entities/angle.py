from .edge import Point
from typing import Optional
from dto.input_dtos import AngleInput

class Angle:
    def __init__(
        self, 
        vertex1: Point, 
        vertex2: Point,
        vertex3: Point,
        angle_measure: Optional[AngleInput] = None,
        name: Optional[str] = None
    ):
        if vertex1 is None or vertex2 is None or vertex3 is None:
            raise ValueError("All vertices must be specified for an angle")
        
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.vertex3 = vertex3
        self.angle_measure = angle_measure
        self.name = name

    def __str__(self):
        angle_value = self.angle_measure.value if self.angle_measure else "unknown"
        return f"Angle({self.name or 'unnamed'}, vertex: {self.vertex2.name}, value: {angle_value})"