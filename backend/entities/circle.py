from .point import Point
import math
from typing import Optional

class Circle:
    def __init__(self, center: Point, diameter: Optional[float] = None, name: Optional[str] = None):
        if center is None:
            raise ValueError("Center must be specified")
        
        self.center = center
        self.name = name
        
        if diameter is not None:
            if not isinstance(diameter, (int, float)):
                raise ValueError("Diameter must be a number")
            if diameter <= 0:
                raise ValueError("Diameter cannot be negative or zero")
            
            self.diameter = float(diameter)
            self.radius = self.diameter / 2
            self.circumference = self.diameter * math.pi
        else:
            self.diameter = None
            self.radius = None
            self.circumference = None

    def __str__(self):
        return f"Circle({self.name or 'unnamed'}, center: {self.center.name}, diameter: {self.diameter})"