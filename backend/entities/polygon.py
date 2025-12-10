from typing import List, Optional

from .point import Point
from .edge import Edge

class Polygon:
    def __init__(self, vertices: Optional[List[Point]] = None, edges: Optional[List[Edge]] = None, name: Optional[str] = None):
        if vertices is None:
            vertices = []
            
        if edges is None:
            edges = []
        
        self.name = name
        self.vertices = vertices
        self.edges = edges
        vertex_count = len(vertices)
        if vertex_count >= 3:
            self.type = f"polygon_{vertex_count}"
        else:
            self.type = f"polygon_edges_{len(edges)}"

    def __str__(self):
        return f"Polygon({self.name or 'unnamed'}, vertices: {len(self.vertices)}, edges: {len(self.edges)})"