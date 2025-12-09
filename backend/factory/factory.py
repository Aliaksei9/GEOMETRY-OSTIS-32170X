from typing import Dict, Union, Any
from entities.edge import Point, Edge
from entities.polygon import Polygon
from entities.circle import Circle
from entities.angle import Angle
from entities.relationship import Relationship
from dto.input_dtos import PolygonInput, EdgeInput, CircleInput, RelationshipInput, AngleInput

class GeometryFactory:
    @staticmethod
    def create_point(name: str, point_registry: Dict[str, Point]) -> Point:
        if name not in point_registry:
            point_registry[name] = Point(name=name)
        return point_registry[name]

    @staticmethod
    def create_edge(edge_input: EdgeInput, point_registry: Dict[str, Point]) -> Edge:
        vert1 = GeometryFactory.create_point(edge_input.vert1, point_registry)  # vert1 - строка
        vert2 = GeometryFactory.create_point(edge_input.vert2, point_registry)  # vert2 - строка
        
        if vert1.name == vert2.name:
            raise ValueError(f"Edge vertices cannot be the same: {vert1.name}")
        
        length_value = edge_input.length.value if edge_input.length else None
        
        return Edge(vert1=vert1, vert2=vert2, length=length_value)

    @staticmethod
    def create_angle(angle_input, point_registry: Dict[str, Point]) -> Angle:
        """Создает объект угла из ConstructionElementInput"""
        if not all([angle_input.vert1, angle_input.vert2, angle_input.vert3]):
            raise ValueError("Angle must have three vertices")
        
        vertex1 = GeometryFactory.create_point(angle_input.vert1, point_registry)
        vertex2 = GeometryFactory.create_point(angle_input.vert2, point_registry)  # Вершина угла
        vertex3 = GeometryFactory.create_point(angle_input.vert3, point_registry)
        
        return Angle(
            vertex1=vertex1,
            vertex2=vertex2,
            vertex3=vertex3,
            angle_measure=angle_input.angle,
            name=angle_input.name
        )

    @staticmethod
    def create_polygon(polygon_input: PolygonInput, point_registry: Dict[str, Point]) -> Polygon:
        # Создаем vertices если они предоставлены, иначе создаем пустой список
        if polygon_input.vertices:
            vertices = [GeometryFactory.create_point(v, point_registry) for v in polygon_input.vertices]
        else:
            vertices = []
        
        # Создаем edges если они предоставлены, иначе создаем пустой список
        if polygon_input.edges:
            edges = [GeometryFactory.create_edge(edge, point_registry) for edge in polygon_input.edges]
        else:
            edges = []
        
        # УБРАНО: автоматическое создание точек по умолчанию
        # Если нет вершин и нет edges - оставляем пустые списки
        
        return Polygon(vertices=vertices, edges=edges, name=polygon_input.name)

    @staticmethod
    def create_circle(circle_input: CircleInput, point_registry: Dict[str, Point]) -> Circle:
        center = GeometryFactory.create_point(circle_input.center, point_registry)
        
        diameter_value = None
        
        if circle_input.diameter:
            # Создаем точки диаметра
            GeometryFactory.create_point(circle_input.diameter.vert1, point_registry)
            GeometryFactory.create_point(circle_input.diameter.vert2, point_registry)
            
            # Получаем значение диаметра
            if circle_input.diameter.length and circle_input.diameter.length.value is not None:
                if isinstance(circle_input.diameter.length.value, str):
                    try:
                        diameter_value = float(circle_input.diameter.length.value)
                    except ValueError:
                        raise ValueError(f"Invalid diameter value: {circle_input.diameter.length.value}")
                else:
                    diameter_value = float(circle_input.diameter.length.value)
        
        return Circle(
            center=center, 
            diameter=diameter_value, 
            name=circle_input.name
        )

    @staticmethod
    def create_relationship(
        relationship_input: RelationshipInput,
        entity_registry: Dict[str, Any]
    ) -> Relationship:
        """
        Создает объект отношения между любыми сущностями
        """
        source_entity = GeometryFactory._find_entity(relationship_input.source_entity, entity_registry)
        target_entity = GeometryFactory._find_entity(relationship_input.target_entity, entity_registry)
        
        if not source_entity:
            raise ValueError(f"Source entity '{relationship_input.source_entity}' not found")
        if not target_entity:
            raise ValueError(f"Target entity '{relationship_input.target_entity}' not found")
        
        return Relationship(
            rel_type=relationship_input.type,
            name=relationship_input.name,
            source_entity=source_entity,
            target_entity=target_entity
        )

    @staticmethod
    def _find_entity(entity_name: str, entity_registry: Dict[str, Any]) -> Any:
        """Ищет сущность по имени в универсальном реестре"""
        return entity_registry.get(entity_name)