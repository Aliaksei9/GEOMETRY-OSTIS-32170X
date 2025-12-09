from typing import Any

class Relationship:
    def __init__(
        self,
        rel_type: str,
        name: str,
        source_entity: Any,
        target_entity: Any,
        oriented: bool = True  # Новый параметр
    ):
        self.type = rel_type
        self.name = name
        self.source_entity = source_entity
        self.target_entity = target_entity
        self.oriented = oriented  # Сохраняем ориентацию

    def __str__(self):
        source_name = self._get_entity_name(self.source_entity)
        target_name = self._get_entity_name(self.target_entity)
        orientation = "->" if self.oriented else "<->"
        return f"Relationship({self.type}:{self.name}, {source_name} {orientation} {target_name})"

    def _get_entity_name(self, entity):
        """Получает имя сущности независимо от её типа"""
        if hasattr(entity, 'name'):
            return entity.name
        elif hasattr(entity, '__str__'):
            return str(entity)
        else:
            return "unknown_entity"