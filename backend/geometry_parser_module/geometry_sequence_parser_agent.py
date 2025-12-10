"""
Agent for parsing geometry sequence results to JSON format - WORKING VERSION WITH OPTIMIZATIONS
"""

import json
import logging
import time
from sc_client.models import ScAddr
from sc_client.constants import sc_type
from sc_client.client import search_by_template, get_elements_types
from sc_client.models import ScTemplate
from sc_client.models import ScLinkContent, ScLinkContentType

from sc_kpm import ScAgentClassic, ScResult, ScKeynodes
from sc_kpm.utils import get_element_system_identifier, generate_link
from sc_kpm.utils.action_utils import (
    generate_action_result,
    finish_action_with_status,
    get_action_arguments
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)


class GeometrySequenceParserAgent(ScAgentClassic):
    def __init__(self):
        super().__init__("action_parse_geometry_sequence")
        self.parser = GeometrySequenceParser()

    def on_event(self, action_class: ScAddr, arc: ScAddr, action: ScAddr) -> ScResult:
        result = self.run(action)
        is_successful = result == ScResult.OK
        finish_action_with_status(action, is_successful)
        logging.info("GeometrySequenceParserAgent finished %s",
                     "successfully" if is_successful else "unsuccessfully")
        return result

    def run(self, action_node: ScAddr) -> ScResult:
        logging.info("GeometrySequenceParserAgent started")
        
        try:
            # Получаем аргументы - структуру результата от агента извлечения последовательности
            arguments = get_action_arguments(action_node, 1)
            if not arguments:
                logging.error("No arguments provided")
                return ScResult.ERROR
                
            result_structure = arguments[0]
            
            logging.info(f"=== НАЧАЛО ПАРСИНГА ПОСЛЕДОВАТЕЛЬНОСТИ ===")
            logging.info(f"Входная структура: {result_structure.value}")
            
            # Парсим структуру в JSON
            json_result = self.parser.parse_sequence_result(result_structure)
            
            # Создаем строку с JSON результатом
            json_string = json.dumps(json_result, ensure_ascii=False, indent=2)
            
            # Создаем результат действия
            result_node = generate_link(content=json_string, content_type=ScLinkContentType.STRING)
            
            generate_action_result(action_node, result_node)
            logging.info("=== ПАРСИНГ ПОСЛЕДОВАТЕЛЬНОСТИ ЗАВЕРШЕН ===")
            
            # Выводим JSON в консоль для отладки
            print("=== РЕЗУЛЬТАТ ПАРСИНГА ПОСЛЕДОВАТЕЛЬНОСТИ ===")
            print(json_string)
            
            return ScResult.OK
            
        except Exception as e:
            logging.error(f"Error in GeometrySequenceParserAgent: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return ScResult.ERROR


class GeometrySequenceParser:
    def __init__(self):
        self.logger = logging.getLogger("GeometrySequenceParser")
        self._id_cache = {}  # Простое кэширование идентификаторов
        
    def get_element_identifier_cached(self, element: ScAddr) -> str:
        """Кэшированное получение идентификатора"""
        if not element or not element.is_valid():
            return ""
            
        if element.value in self._id_cache:
            return self._id_cache[element.value]
        
        identifier = get_element_system_identifier(element) or f"node_{element.value}"
        self._id_cache[element.value] = identifier
        return identifier
        
    def parse_sequence_result(self, result_structure: ScAddr) -> dict:
        """
        Парсит результат агента извлечения последовательности и возвращает JSON
        """
        try:
            start_time = time.time()
            self.logger.info("=== НАЧАЛО ПАРСИНГА ПОСЛЕДОВАТЕЛЬНОСТИ ===")
            
            # Получаем все элементы из структуры результата
            sequence_elements = self.get_all_elements_from_structure(result_structure)
            self.logger.info(f"Найдено элементов в структуре: {len(sequence_elements)}")
            
            # Разделяем элементы на ноды последовательности и связи
            sequence_nodes, connections = self.extract_sequence_nodes_and_connections(sequence_elements)
            self.logger.info(f"Найдено нод последовательности: {len(sequence_nodes)}")
            self.logger.info(f"Найдено связей: {len(connections)}")
            
            # Сортируем ноды по порядку в последовательности (если есть последовательность)
            ordered_nodes = self.order_sequence_nodes(sequence_nodes, connections)
            self.logger.info(f"Упорядочено нод: {len(ordered_nodes)}")
            
            # Создаем JSON структуру
            result_json = self.create_sequence_json(ordered_nodes, result_structure)
            
            total_time = time.time() - start_time
            self.logger.info(f"=== ПАРСИНГ ПОСЛЕДОВАТЕЛЬНОСТИ ЗАВЕРШЕН за {total_time:.2f} сек ===")
            return result_json
            
        except Exception as e:
            self.logger.error(f"Error parsing sequence result: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def get_all_elements_from_structure(self, structure: ScAddr) -> list:
        """Получает все элементы из структуры"""
        elements = []
        
        try:
            template = ScTemplate()
            template.triple(
                structure,
                sc_type.VAR_PERM_POS_ARC >> "_arc",
                sc_type.VAR_NODE >> "_element"
            )
            
            search_results = search_by_template(template)
            
            for result in search_results:
                element = result.get("_element")
                if element and element.is_valid():
                    elements.append(element)
                    
            self.logger.info(f"Из структуры извлечено {len(elements)} элементов")
                    
        except Exception as e:
            self.logger.error(f"Error getting elements from structure: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
        return elements
    
    def extract_sequence_nodes_and_connections(self, elements: list) -> tuple:
        """Разделяет элементы на ноды последовательности и связи"""
        sequence_nodes = []
        connections = []
        
        for element in elements:
            try:
                element_types = get_elements_types(element)
                if element_types:
                    element_type = element_types[0]
                    
                    if element_type.is_node():
                        # Проверяем, является ли нода частью последовательности
                        if self.is_sequence_node(element):
                            sequence_nodes.append(element)
                    elif element_type.is_edge():
                        connections.append(element)
                        
            except Exception as e:
                self.logger.warning(f"Error processing element {element.value}: {str(e)}")
                
        return sequence_nodes, connections
    
    def is_sequence_node(self, node: ScAddr) -> bool:
        """Проверяет, является ли нода частью последовательности действий"""
        try:
            # Проверяем, является ли это действие или имеет отношение к последовательности
            node_idtf = self.get_element_identifier_cached(node)
            
            # Если это явно действие или задача
            if any(keyword in node_idtf.lower() for keyword in ["action", "task", "step", "operation"]):
                return True
                
            # Ищем связь через nrel_basic_sequence (для последовательностей)
            nrel_basic_sequence = ScKeynodes.resolve("nrel_basic_sequence", sc_type.CONST_NODE_NON_ROLE)
            
            if nrel_basic_sequence and nrel_basic_sequence.is_valid():
                # Проверяем исходящие связи
                template_out = ScTemplate()
                template_out.quintuple(
                    node,
                    sc_type.VAR_ARC >> "_main_arc",
                    sc_type.VAR_NODE >> "_target",
                    sc_type.VAR_PERM_POS_ARC >> "_rel_arc",
                    nrel_basic_sequence
                )
                
                results_out = search_by_template(template_out)
                if results_out:
                    return True
                    
                # Проверяем входящие связи
                template_in = ScTemplate()
                template_in.quintuple(
                    sc_type.VAR_NODE >> "_source",
                    sc_type.VAR_ARC >> "_main_arc",
                    node,
                    sc_type.VAR_PERM_POS_ARC >> "_rel_arc",
                    nrel_basic_sequence
                )
                
                results_in = search_by_template(template_in)
                if results_in:
                    return True
            
            # Если нет связей nrel_basic_sequence, но есть другие значимые связи,
            # считаем это одиночным действием
            if self.has_significant_connections(node):
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking sequence node: {str(e)}")
            # В случае ошибки считаем, что это может быть последовательностью
            return True
    
    def has_significant_connections(self, node: ScAddr) -> bool:
        """Проверяет, имеет ли нода значимые связи (не технические)"""
        try:
            # Ищем связи с другими элементами
            template = ScTemplate()
            template.triple(
                node,
                sc_type.VAR_ARC >> "_arc",
                sc_type.VAR_NODE >> "_target"
            )
            
            results = search_by_template(template)
            
            for result in results:
                target = result.get("_target")
                if target and target.is_valid():
                    target_idtf = self.get_element_identifier_cached(target)
                    # Если цель не является техническим элементом
                    if not self.is_technical_element(target_idtf):
                        return True
                        
            # Также проверяем входящие связи
            template_in = ScTemplate()
            template_in.triple(
                sc_type.VAR_NODE >> "_source",
                sc_type.VAR_ARC >> "_arc", 
                node
            )
            
            results_in = search_by_template(template_in)
            
            for result in results_in:
                source = result.get("_source")
                if source and source.is_valid():
                    source_idtf = self.get_element_identifier_cached(source)
                    if not self.is_technical_element(source_idtf):
                        return True
                        
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking significant connections: {str(e)}")
            return False
    
    def is_technical_element(self, identifier: str) -> bool:
        """Проверяет, является ли элемент техническим"""
        if not identifier:
            return True
            
        technical_keywords = ["connector", "arc", "edge", "link", "node_", "element_"]
        return any(keyword in identifier.lower() for keyword in technical_keywords)
    
    def order_sequence_nodes(self, nodes: list, connections: list) -> list:
        """Упорядочивает ноды последовательности по порядку выполнения"""
        # Если только одна нода, возвращаем ее как есть
        if len(nodes) <= 1:
            return nodes
            
        ordered_nodes = []
        
        try:
            # Находим начальную ноду (ту, у которой нет входящих связей nrel_basic_sequence)
            start_nodes = self.find_start_nodes(nodes)
            
            if not start_nodes:
                self.logger.warning("No start nodes found, returning unordered nodes")
                return nodes
                
            current_node = start_nodes[0]
            node_idtf = self.get_element_identifier_cached(current_node)
            self.logger.info(f"Начальная нода: {node_idtf}")
            
            while current_node and current_node not in ordered_nodes:
                ordered_nodes.append(current_node)
                next_node = self.find_next_node(current_node, nodes)
                
                if next_node and next_node not in ordered_nodes:
                    current_node = next_node
                    next_idtf = self.get_element_identifier_cached(current_node)
                    self.logger.info(f"Следующая нода: {next_idtf}")
                else:
                    break
                    
            # Добавляем оставшиеся ноды
            for node in nodes:
                if node not in ordered_nodes:
                    ordered_nodes.append(node)
                    node_idtf = self.get_element_identifier_cached(node)
                    self.logger.info(f"Добавлена оставшаяся нода: {node_idtf}")
                    
        except Exception as e:
            self.logger.error(f"Error ordering sequence nodes: {str(e)}")
            ordered_nodes = nodes
            
        return ordered_nodes
    
    def find_start_nodes(self, nodes: list) -> list:
        """Находит начальные ноды последовательности"""
        # Если только одна нода, она и является начальной
        if len(nodes) == 1:
            return nodes
            
        start_nodes = []
        nrel_basic_sequence = ScKeynodes.resolve("nrel_basic_sequence", sc_type.CONST_NODE_NON_ROLE)
        
        if not nrel_basic_sequence or not nrel_basic_sequence.is_valid():
            self.logger.warning("nrel_basic_sequence not found, using first node as start")
            return [nodes[0]] if nodes else []
        
        for node in nodes:
            try:
                # Ищем, есть ли входящие связи nrel_basic_sequence
                template = ScTemplate()
                template.quintuple(
                    sc_type.VAR_NODE >> "_source",
                    sc_type.VAR_ARC >> "_main_arc",
                    node,
                    sc_type.VAR_PERM_POS_ARC >> "_rel_arc",
                    nrel_basic_sequence
                )
                
                results = search_by_template(template)
                if not results:
                    start_nodes.append(node)
                    node_idtf = self.get_element_identifier_cached(node)
                    self.logger.info(f"Найдена стартовая нода: {node_idtf}")
                    
            except Exception as e:
                self.logger.warning(f"Error checking start node {node.value}: {str(e)}")
                
        return start_nodes if start_nodes else ([nodes[0]] if nodes else [])
    
    def find_next_node(self, current_node: ScAddr, all_nodes: list) -> ScAddr:
        """Находит следующую ноду в последовательности"""
        nrel_basic_sequence = ScKeynodes.resolve("nrel_basic_sequence", sc_type.CONST_NODE_NON_ROLE)
        
        if not nrel_basic_sequence or not nrel_basic_sequence.is_valid():
            return None
            
        try:
            template = ScTemplate()
            template.quintuple(
                current_node,
                sc_type.VAR_ARC >> "_main_arc",
                sc_type.VAR_NODE >> "_target",
                sc_type.VAR_PERM_POS_ARC >> "_rel_arc",
                nrel_basic_sequence
            )
            
            results = search_by_template(template)
            
            for result in results:
                target_node = result.get("_target")
                if target_node and target_node.is_valid() and target_node in all_nodes:
                    return target_node
                    
        except Exception as e:
            self.logger.error(f"Error finding next node: {str(e)}")
            
        return None
    
    def create_sequence_json(self, ordered_nodes: list, result_structure: ScAddr) -> dict:
        """Создает JSON структуру для последовательности"""
        result_json = {
            "idx": [],
            "steps": []
        }
        
        try:
            for i, node in enumerate(ordered_nodes):
                step_id = f"task_step_{i+1}"
                result_json["idx"].append(step_id)
                
                # Парсим структуру шага
                step_structure = self.parse_step_structure(node)
                
                result_json["steps"].append({
                    step_id: step_structure
                })
                
                node_idtf = self.get_element_identifier_cached(node)
                self.logger.info(f"Добавлен шаг {step_id}: {node_idtf}")
                
        except Exception as e:
            self.logger.error(f"Error creating sequence JSON: {str(e)}")
            
        return result_json
    
    def parse_step_structure(self, step_node: ScAddr) -> dict:
        """Парсит структуру отдельного шага"""
        step_name = self.get_element_identifier_cached(step_node)
        if not step_name or step_name.startswith("node_") or step_name.startswith("element_"):
            step_name = f"step_{step_node.value}"
            
        step_data = {
            "name": step_name,
            "entities": [],  # Все сущности (вершины, фигуры)
            "edges": [],     # Ребра между сущностями
            "relationships": []  # Отношения (nrel_, rrel_)
        }
        
        try:
            # Получаем все элементы, связанные с шагом
            related_elements = self.get_related_elements(step_node)
            self.logger.info(f"Для шага {step_data['name']} найдено {len(related_elements)} связанных элементов")
            
            # Извлекаем сущности, ребра и отношения
            entities, edges, relationships = self.extract_entities_edges_and_relationships(related_elements)
            
            step_data["entities"] = entities
            step_data["edges"] = edges
            step_data["relationships"] = relationships
            
            self.logger.info(f"Для шага {step_data['name']} извлечено {len(entities)} сущностей, {len(edges)} ребер и {len(relationships)} отношений")
            
        except Exception as e:
            self.logger.error(f"Error parsing step structure: {str(e)}")
            
        return step_data
    
    def get_related_elements(self, step_node: ScAddr) -> list:
        """Получает элементы, связанные с шагом"""
        related_elements = []
        
        try:
            # Ищем элементы, связанные через различные отношения
            templates = [
                # Прямые связи
                self.create_relation_template(step_node, sc_type.VAR_PERM_POS_ARC, "_target1"),
                # Связи через атрибуты
                self.create_attribute_template(step_node, "_target2")
            ]
            
            for template in templates:
                results = search_by_template(template)
                for result in results:
                    # Правильно обрабатываем ScTemplateResult - используем только существующие алиасы
                    for alias in self.get_available_aliases(template, result):
                        element = result.get(alias)
                        if element and element.is_valid() and element not in related_elements:
                            related_elements.append(element)
                                
        except Exception as e:
            self.logger.error(f"Error getting related elements: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
        return related_elements
    
    def get_available_aliases(self, template, result) -> list:
        """Получает список доступных алиасов из результата шаблона"""
        # Для простоты возвращаем стандартные алиасы, которые мы используем
        aliases = []
        
        # Для тройки
        if hasattr(template, 'triple_list') and len(template.triple_list) == 1:
            triple = template.triple_list[0]
            if triple.source.alias:
                aliases.append(triple.source.alias)
            if triple.connector.alias:
                aliases.append(triple.connector.alias)
            if triple.target.alias:
                aliases.append(triple.target.alias)
        
        # Для квинтюпля
        elif hasattr(template, 'triple_list') and len(template.triple_list) == 2:
            # Первая тройка
            triple1 = template.triple_list[0]
            if triple1.source.alias:
                aliases.append(triple1.source.alias)
            if triple1.connector.alias:
                aliases.append(triple1.connector.alias)
            if triple1.target.alias:
                aliases.append(triple1.target.alias)
            
            # Вторая тройка
            triple2 = template.triple_list[1]
            if triple2.source.alias:
                aliases.append(triple2.source.alias)
            if triple2.connector.alias:
                aliases.append(triple2.connector.alias)
            if triple2.target.alias:
                aliases.append(triple2.target.alias)
        
        return aliases
    
    def create_relation_template(self, source: ScAddr, arc_type: sc_type, target_alias: str) -> ScTemplate:
        """Создает шаблон для поиска связанных элементов"""
        template = ScTemplate()
        template.triple(
            source,
            arc_type >> "_arc",
            sc_type.VAR_NODE >> target_alias
        )
        return template
    
    def create_attribute_template(self, source: ScAddr, target_alias: str) -> ScTemplate:
        """Создает шаблон для поиска атрибутов"""
        template = ScTemplate()
        template.quintuple(
            source,
            sc_type.VAR_ARC >> "_main_arc",
            sc_type.VAR_NODE >> target_alias,
            sc_type.VAR_PERM_POS_ARC >> "_attr_arc",
            sc_type.VAR_NODE >> "_attribute"
        )
        return template
    
    def extract_entities_edges_and_relationships(self, elements: list) -> tuple:
        """Извлекает сущности, ребра и отношения из элементов"""
        entities = []
        edges = []
        relationships = []
        
        for element in elements:
            try:
                element_types = get_elements_types(element)
                if not element_types:
                    continue
                    
                element_type = element_types[0]
                
                # Определяем тип элемента и добавляем в соответствующую категорию
                if self.is_entity_element(element, element_type):
                    entity_data = self.parse_entity_element(element, element_type)
                    if entity_data:
                        entities.append(entity_data)
                elif self.is_edge_element(element, element_type):
                    edge_data = self.parse_edge_element(element, element_type)
                    if edge_data:
                        edges.append(edge_data)
                elif self.is_relationship_element(element, element_type):
                    relationship_data = self.parse_relationship_element(element, element_type)
                    if relationship_data:
                        relationships.append(relationship_data)
                        
            except Exception as e:
                self.logger.warning(f"Error processing element {element.value}: {str(e)}")
                
        return entities, edges, relationships
    
    def is_entity_element(self, element: ScAddr, element_type: sc_type) -> bool:
        """Проверяет, является ли элемент сущностью (вершиной или фигурой)"""
        if not element_type.is_node():
            return False
            
        # Сущность - это любая нода, которая не является отношением и не является ребром
        idtf = self.get_element_identifier_cached(element)
        
        # Исключаем отношения
        if idtf.startswith("nrel_") or idtf.startswith("rrel_"):
            return False
            
        # Исключаем технические элементы
        technical_keywords = ["connector", "arc", "edge", "link"]
        if any(keyword in idtf.lower() for keyword in technical_keywords):
            return False
            
        return True
    
    def is_edge_element(self, element: ScAddr, element_type: sc_type) -> bool:
        """Проверяет, является ли элемент ребром"""
        if not element_type.is_edge():
            return False
            
        # Ребро - это любая дуга, которая не является отношением
        return True
    
    def is_relationship_element(self, element: ScAddr, element_type: sc_type) -> bool:
        """Проверяет, является ли элемент отношением"""
        if not element_type.is_node():
            return False
            
        # Отношения обычно имеют префиксы nrel_, rrel_
        idtf = self.get_element_identifier_cached(element)
        return idtf.startswith("nrel_") or idtf.startswith("rrel_")
    
    def parse_entity_element(self, element: ScAddr, element_type: sc_type) -> dict:
        """Парсит элемент сущности"""
        entity_name = self.get_element_identifier_cached(element)
        if not entity_name or entity_name.startswith("node_") or entity_name.startswith("element_"):
            entity_name = f"entity_{element.value}"
            
        entity_data = {
            "name": entity_name,
            "type": self.determine_entity_type(element, entity_name),
            "properties": {}
        }
        
        try:
            # Находим связанные свойства сущности
            properties = self.find_entity_properties(element)
            entity_data["properties"] = properties
            
        except Exception as e:
            self.logger.warning(f"Error parsing entity element {entity_name}: {str(e)}")
            
        return entity_data
    
    def parse_edge_element(self, edge_element: ScAddr, element_type: sc_type) -> dict:
        """Парсит элемент ребра"""
        edge_name = self.get_element_identifier_cached(edge_element)
        if not edge_name or edge_name.startswith("node_") or edge_name.startswith("element_"):
            edge_name = f"edge_{edge_element.value}"
            
        edge_data = {
            "name": edge_name,
            "sources": [],
            "targets": [],
            "properties": {}
        }
        
        try:
            # Находим source и target ребра
            source_target = self.find_edge_source_target(edge_element)
            edge_data["sources"] = source_target.get("sources", [])
            edge_data["targets"] = source_target.get("targets", [])
                
            # Находим свойства ребра
            properties = self.find_edge_properties(edge_element)
            edge_data["properties"] = properties
                
        except Exception as e:
            self.logger.warning(f"Error parsing edge element {edge_name}: {str(e)}")
            
        return edge_data
    
    def parse_relationship_element(self, element: ScAddr, element_type: sc_type) -> dict:
        """Парсит элемент отношения"""
        relationship_name = self.get_element_identifier_cached(element)
        if not relationship_name:
            relationship_name = f"relation_{element.value}"
            
        relationship_data = {
            "type": "role" if relationship_name.startswith("rrel_") else "nonrole",
            "name": relationship_name,
            "source_entity": "",
            "target_entity": ""
        }
        
        try:
            # Находим source и target отношения
            source_target = self.find_relationship_source_target(element)
            if source_target:
                relationship_data["source_entity"] = source_target.get("source", "")
                relationship_data["target_entity"] = source_target.get("target", "")
                
        except Exception as e:
            self.logger.warning(f"Error parsing relationship element {relationship_name}: {str(e)}")
            
        return relationship_data
    
    def determine_entity_type(self, element: ScAddr, entity_name: str) -> str:
        """Определяет тип сущности"""
        entity_name_lower = entity_name.lower()
        
        if "triangle" in entity_name_lower:
            return "triangle"
        elif "circle" in entity_name_lower:
            return "circle"
        elif "square" in entity_name_lower or "quad" in entity_name_lower:
            return "quadrilateral"
        elif "polygon" in entity_name_lower:
            return "polygon"
        elif "point" in entity_name_lower or "vertex" in entity_name_lower:
            return "point"
        else:
            return "entity"
    
    def find_entity_properties(self, entity_element: ScAddr) -> dict:
        """Находит свойства сущности"""
        properties = {}
        
        try:
            # Ищем числовые значения, связанные с сущностью
            template = ScTemplate()
            template.quintuple(
                entity_element,
                sc_type.VAR_ARC >> "_main_arc",
                sc_type.VAR_NODE >> "_value",
                sc_type.VAR_PERM_POS_ARC >> "_rel_arc",
                sc_type.VAR_NODE >> "_relation"
            )
            
            results = search_by_template(template)
            
            for result in results:
                value_node = result.get("_value")
                relation_node = result.get("_relation")
                
                if value_node and value_node.is_valid() and relation_node and relation_node.is_valid():
                    value_name = self.get_element_identifier_cached(value_node)
                    relation_name = self.get_element_identifier_cached(relation_node)
                    
                    if not value_name:
                        value_name = f"value_{value_node.value}"
                    if not relation_name:
                        relation_name = f"relation_{relation_node.value}"
                    
                    # Пытаемся извлечь числовое значение
                    try:
                        import re
                        numbers = re.findall(r"\d+\.?\d*", value_name)
                        if numbers:
                            numeric_value = float(numbers[0])
                            properties[relation_name] = numeric_value
                        else:
                            properties[relation_name] = value_name
                    except ValueError:
                        properties[relation_name] = value_name
                        
        except Exception as e:
            self.logger.warning(f"Error finding entity properties: {str(e)}")
            
        return properties
    
    def find_edge_source_target(self, edge_element: ScAddr) -> dict:
        source_target = {
            "sources": [],
            "targets": []
        }
        
        try:
            template = ScTemplate()
            template.triple(
                sc_type.VAR_NODE >> "_source",
                edge_element,
                sc_type.VAR_NODE >> "_target"
            )
            
            results = search_by_template(template)
            
            for result in results:
                source = result.get("_source")
                target = result.get("_target")
                
                if source and source.is_valid():
                    source_name = self.get_element_identifier_cached(source)
                    if not source_name or source_name.startswith("node_") or source_name.startswith("element_"):
                        source_name = f"entity_{source.value}"
                    source_target["sources"].append(source_name)
                    
                if target and target.is_valid():
                    target_name = self.get_element_identifier_cached(target)
                    if not target_name or target_name.startswith("node_") or target_name.startswith("element_"):
                        target_name = f"entity_{target.value}"
                    source_target["targets"].append(target_name)
                                
        except Exception as e:
            self.logger.warning(f"Error finding edge source/target: {str(e)}")
            
        return source_target
    
    def find_edge_properties(self, edge_element: ScAddr) -> dict:
        """Находит свойства ребра"""
        properties = {}
        
        try:
            # Ищем числовые значения, связанные с ребром (например, длина)
            template = ScTemplate()
            template.quintuple(
                edge_element,
                sc_type.VAR_ARC >> "_main_arc",
                sc_type.VAR_NODE >> "_value",
                sc_type.VAR_PERM_POS_ARC >> "_rel_arc",
                sc_type.VAR_NODE >> "_relation"
            )
            
            results = search_by_template(template)
            
            for result in results:
                value_node = result.get("_value")
                relation_node = result.get("_relation")
                
                if value_node and value_node.is_valid() and relation_node and relation_node.is_valid():
                    value_name = self.get_element_identifier_cached(value_node)
                    relation_name = self.get_element_identifier_cached(relation_node)
                    
                    if not value_name:
                        value_name = f"value_{value_node.value}"
                    if not relation_name:
                        relation_name = f"relation_{relation_node.value}"
                    
                    # Пытаемся извлечь числовое значение
                    try:
                        import re
                        numbers = re.findall(r"\d+\.?\d*", value_name)
                        if numbers:
                            numeric_value = float(numbers[0])
                            properties[relation_name] = numeric_value
                        else:
                            properties[relation_name] = value_name
                    except ValueError:
                        properties[relation_name] = value_name
                        
        except Exception as e:
            self.logger.warning(f"Error finding edge properties: {str(e)}")
            
        return properties
    
    def find_relationship_source_target(self, relationship_element: ScAddr) -> dict:
        source_target = {
            "sources": [],
            "targets": []
        }
        
        try:
            template = ScTemplate()
            template.quintuple(
                sc_type.VAR_NODE >> "_source",
                sc_type.VAR_ARC >> "_main_arc",
                sc_type.VAR_NODE >> "_target", 
                sc_type.VAR_PERM_POS_ARC >> "_rel_arc",
                relationship_element
            )
            
            results = search_by_template(template)
            
            for result in results:
                source = result.get("_source")
                target = result.get("_target")
                
                if source and source.is_valid():
                    source_name = self.get_element_identifier_cached(source)
                    if not source_name or source_name.startswith("node_") or source_name.startswith("element_"):
                        source_name = f"entity_{source.value}"
                    source_target["sources"].append(source_name)
                    
                if target and target.is_valid():
                    target_name = self.get_element_identifier_cached(target)
                    if not target_name or target_name.startswith("node_") or target_name.startswith("element_"):
                        target_name = f"entity_{target.value}"
                    source_target["targets"].append(target_name)
                                
        except Exception as e:
            self.logger.warning(f"Error finding relationship source/target: {str(e)}")
            
        return source_target