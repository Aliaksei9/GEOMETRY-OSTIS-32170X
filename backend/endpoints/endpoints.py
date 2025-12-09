from fastapi import HTTPException, status
from dto.input_dtos import ComplexConstructionInput, PolygonInput, CircleInput, ConstructionElementsContainerInput, RelationshipInput
from factory.factory import GeometryFactory
from .sc_send import SCAdapter
import json

async def upload_construction(construction_input: ComplexConstructionInput):
    """
    Загрузка и валидация геометрической конструкции
    """
    try:
        business_objects = []
        point_registry = {}
        
        for figure_input in construction_input.figures:
            if isinstance(figure_input, PolygonInput):
                polygon = GeometryFactory.create_polygon(figure_input, point_registry)
                business_objects.append({
                    "type": "polygon",
                    "subtype": figure_input.type,
                    "object": polygon,
                    "name": figure_input.name,
                    "input_data": figure_input
                })
                
            elif isinstance(figure_input, CircleInput):
                circle = GeometryFactory.create_circle(figure_input, point_registry)
                business_objects.append({
                    "type": "circle", 
                    "object": circle,
                    "name": circle.name,
                    "input_data": figure_input
                })
                
            elif isinstance(figure_input, ConstructionElementsContainerInput):
                elements = []
                for elem in figure_input.construction_elements:
                    if elem.type == "general_point" and elem.name:
                        point = GeometryFactory.create_point(elem.name, point_registry)
                        elements.append({"type": "point", "point": point})
                    elif elem.type == "angle":
                        angle = GeometryFactory.create_angle(elem, point_registry)
                        elements.append({"type": "angle", "angle": angle})
                    else:
                        elements.append({"type": elem.type, "data": elem.model_dump()})
                
                business_objects.append({
                    "type": "construction_elements",
                    "elements": elements
                })
        
        result = {
            "construction": construction_input.name,
            "total_figures": len(business_objects),
            "total_points": len(point_registry),
            "points": list(point_registry.keys()),
            "figures": [],
            "construction_elements": [],
            "relationships": []
        }
        
        for obj in business_objects:
            if obj["type"] == "polygon":
                polygon = obj["object"]
                edge_names = [f"{e.vert1.name}{e.vert2.name}" for e in polygon.edges]
                result["figures"].append({
                    "type": obj["subtype"],
                    "name": obj["name"],
                    "vertices": [v.name for v in polygon.vertices],
                    "edges": edge_names,
                    "vertex_count": len(polygon.vertices),
                    "input_data": obj["input_data"]
                })
            elif obj["type"] == "circle":
                circle = obj["object"]
                circle_input = obj["input_data"]
                
                diameter_info = None
                if circle_input.diameter:
                    diameter_info = {
                        "vert1": circle_input.diameter.vert1,
                        "vert2": circle_input.diameter.vert2,
                        "length": circle_input.diameter.length.dict() if circle_input.diameter.length else None
                    }
                
                result["figures"].append({
                    "type": "circle",
                    "name": circle.name, 
                    "center": circle.center.name,
                    "diameter": circle.diameter,
                    "radius": circle.radius,
                    "circumference": circle.circumference,
                    "diameter_edge": diameter_info
                })
            elif obj["type"] == "construction_elements":
                for element in obj["elements"]:
                    if element["type"] == "point":
                        result["construction_elements"].append({
                            "type": "point",
                            "name": element["point"].name
                        })
                    elif element["type"] == "angle":
                        angle = element["angle"]
                        result["construction_elements"].append({
                            "type": "angle",
                            "name": angle.name,
                            "vertex1": angle.vertex1.name,
                            "vertex2": angle.vertex2.name,
                            "vertex3": angle.vertex3.name,
                            "angle": angle.angle_measure.dict() if angle.angle_measure else None
                        })
                    else:
                        result["construction_elements"].append(element)
        
        for relationship in construction_input.relationships:
            result["relationships"].append({
                "type": relationship.type,
                "name": relationship.name,
                "source_entity": relationship.source_entity,
                "target_entity": relationship.target_entity
            })
        
        parsing_result = ""
        try:
            with SCAdapter() as sc_adapter:
                success, uploaded_addrs = sc_adapter.upload_construction(result)
                if success:
                    parsing_result = sc_adapter.get_parsing_result()
                else:
                    parsing_result = "Ошибка загрузки в SC-память"
        except Exception as e:
            parsing_result = f"SC-memory error: {e}"
        
        # Парсим JSON строку в объект Python и возвращаем как отформатированный JSON
        return json.loads(parsing_result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing error: {str(e)}"
        )