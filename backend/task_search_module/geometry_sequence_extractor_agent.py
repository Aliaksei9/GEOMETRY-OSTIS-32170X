"""
Agent for extracting action sequences from geometry tasks
"""

import logging
from sc_client.models import ScAddr
from sc_client.constants import sc_type
from sc_client.client import search_by_template
from sc_client.models import ScTemplate

from sc_kpm import ScAgentClassic, ScResult, ScKeynodes
from sc_kpm.utils import generate_node, get_element_system_identifier, generate_connector
from sc_kpm.utils.action_utils import (
    generate_action_result,
    finish_action_with_status,
    get_action_arguments
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)


class GeometrySequenceExtractorAgent(ScAgentClassic):
    def __init__(self):
        super().__init__("action_extract_geometry_sequence")

    def on_event(self, action_class: ScAddr, arc: ScAddr, action: ScAddr) -> ScResult:
        result = self.run(action)
        is_successful = result == ScResult.OK
        finish_action_with_status(action, is_successful)
        logging.info("GeometrySequenceExtractorAgent finished %s",
                     "successfully" if is_successful else "unsuccessfully")
        return result

    def run(self, action_node: ScAddr) -> ScResult:
        logging.info("GeometrySequenceExtractorAgent started")
        
        try:
            # Получаем аргументы - задачу от первого агента
            arguments = get_action_arguments(action_node, 1)
            if not arguments:
                logging.error("No arguments provided")
                return ScResult.ERROR
                
            task_structure = arguments[0]
            
            # Извлекаем ноду задачи из структуры
            geometry_task = self.extract_task_from_structure(task_structure)
            if not geometry_task:
                logging.error("No task node found in the structure")
                return ScResult.ERROR
            
            logging.info(f"=== НАЧАЛО ИЗВЛЕЧЕНИЯ ПОСЛЕДОВАТЕЛЬНОСТИ ===")
            logging.info(f"Входная задача: {geometry_task.value}")
            
            # Шаг 1: Ищем ноду CONST_NODE_TUPLE через отношение nrel_decomposition_of_action
            tuple_node = self.find_tuple_node_for_task(geometry_task)
            if not tuple_node:
                logging.error("No tuple node found for the task")
                return ScResult.ERROR
                
            logging.info(f"Найдена нода кортежа: {tuple_node.value}")
            
            # Шаг 2: Идём от кортежа к первой ноде через rrel_1
            first_node = self.get_node_by_role_relation(tuple_node, 1)
            if not first_node:
                logging.error("No first node found via rrel_1")
                return ScResult.ERROR
                
            logging.info(f"Найдена первая нода последовательности: {first_node.value}")
            
            # Шаг 3: Собираем всю последовательность через nrel_basic_sequence
            sequence_nodes, sequence_connections, nrel_sequence = self.collect_sequence(first_node)

            logging.info(f"Собрано нод в последовательности: {len(sequence_nodes)}")
            for i, node in enumerate(sequence_nodes):
                node_idtf = get_element_system_identifier(node) or f"unknown_{node.value}"
                logging.info(f"  {i+1}. {node_idtf}")

            # Шаг 4: Создаем результирующую структуру
            solving_sequence = self.create_result_structure(sequence_nodes, sequence_connections, nrel_sequence)
            
            generate_action_result(action_node, *solving_sequence)
            logging.info("=== ИЗВЛЕЧЕНИЕ ПОСЛЕДОВАТЕЛЬНОСТИ ЗАВЕРШЕНО ===")
            
            return ScResult.OK
            
        except Exception as e:
            logging.error(f"Error in GeometrySequenceExtractorAgent: {str(e)}")
            return ScResult.ERROR

    def extract_task_from_structure(self, structure: ScAddr) -> ScAddr:
        """Извлекает ноду задачи из структуры (структура -> нода задачи)"""
        try:
            # Ищем ноду, на которую указывает структура
            template = ScTemplate()
            template.triple(
                structure,
                sc_type.VAR_PERM_POS_ARC >> "_arc",
                sc_type.VAR_NODE >> "_task_node"
            )
            
            search_results = search_by_template(template)
            
            if search_results:
                task_node = search_results[0].get("_task_node")
                if task_node and task_node.is_valid():
                    task_idtf = get_element_system_identifier(task_node) or f"unknown_{task_node.value}"
                    logging.info(f"Извлечена нода задачи из структуры: {task_idtf}")
                    return task_node
            
            logging.warning(f"Нода задачи не найдена в структуре {structure.value}")
            return None
            
        except Exception as e:
            logging.error(f"Error extracting task from structure: {str(e)}")
            return None

    def find_tuple_node_for_task(self, task_node: ScAddr) -> ScAddr:
        """Ищет ноду CONST_NODE_TUPLE через отношение nrel_decomposition_of_action"""
        try:
            nrel_decomposition = ScKeynodes.resolve("nrel_decomposition_of_action", sc_type.CONST_NODE_NON_ROLE)
            
            template = ScTemplate()
            template.quintuple(
                task_node,                              
                sc_type.VAR_ARC >> "_main_arc",        
                sc_type.VAR_NODE_TUPLE >> "_tuple_node", 
                sc_type.VAR_PERM_POS_ARC >> "_rel_arc", 
                nrel_decomposition                      
            )
            
            search_results = search_by_template(template)
            
            if search_results:
                tuple_node = search_results[0].get("_tuple_node")
                if tuple_node and tuple_node.is_valid():
                    tuple_idtf = get_element_system_identifier(tuple_node) or f"unknown_{tuple_node.value}"
                    logging.info(f"Найден кортеж: {tuple_idtf}")
                    return tuple_node
            
            logging.warning(f"Кортеж не найден для задачи {task_node.value}")
            return None
            
        except Exception as e:
            logging.error(f"Error finding tuple node: {str(e)}")
            return None

    def get_node_by_role_relation(self, source_node: ScAddr, rrel_index: int) -> ScAddr:
        """Получает ноду через отношение rrel_index от исходной ноды"""
        try:
            # Получаем rrel ноду по индексу
            rrel_node = ScKeynodes.rrel_index(rrel_index)
            
            template = ScTemplate()
            template.quintuple(
                source_node,                           
                sc_type.VAR_ARC >> "_main_arc",        
                sc_type.VAR_NODE >> "_target_node",    
                sc_type.VAR_PERM_POS_ARC >> "_rel_arc", 
                rrel_node                             
            )
            
            search_results = search_by_template(template)
            
            if search_results:
                target_node = search_results[0].get("_target_node")
                if target_node and target_node.is_valid():
                    target_idtf = get_element_system_identifier(target_node) or f"unknown_{target_node.value}"
                    logging.info(f"Найдена нода через rrel_{rrel_index}: {target_idtf}")
                    return target_node
            
            logging.warning(f"Нода не найдена через rrel_{rrel_index} от {source_node.value}")
            return None
            
        except Exception as e:
            logging.error(f"Error getting node by role relation: {str(e)}")
            return None

    def collect_sequence(self, start_node: ScAddr) -> tuple:
        """Собирает последовательность нод через отношение nrel_basic_sequence, возвращает ноды и связи"""
        sequence_nodes = []
        sequence_connections = []  # Будет хранить все элементы связей (коннекторы, дуги отношений)
        
        current_node = start_node
        
        try:
            nrel_basic_sequence = ScKeynodes.resolve("nrel_basic_sequence", sc_type.CONST_NODE_NON_ROLE)
            
            while current_node:
                # Добавляем текущую ноду в последовательность
                sequence_nodes.append(current_node)
                
                # Ищем следующую ноду через nrel_basic_sequence
                connection_elements = self.find_connection_elements_in_sequence(current_node, nrel_basic_sequence)
                
                if connection_elements and connection_elements["target"] not in sequence_nodes:  # Защита от циклов
                    # Добавляем все элементы связи в общий список
                    sequence_connections.extend(connection_elements["elements"])
                    current_node = connection_elements["target"]
                    next_idtf = get_element_system_identifier(current_node) or f"unknown_{current_node.value}"
                    logging.info(f"Найдена следующая нода в последовательности: {next_idtf}")
                else:
                    # Последовательность закончена
                    current_node = None
            
            # Добавляем nrel_basic_sequence только если есть связи между действиями
            if len(sequence_nodes) > 1:
                logging.info(f"Собрана последовательность из {len(sequence_nodes)} нод и {len(sequence_connections)} элементов связей")
                return sequence_nodes, sequence_connections, nrel_basic_sequence
            else:
                logging.info(f"Собрана последовательность из {len(sequence_nodes)} нод (без связей nrel_basic_sequence)")
                return sequence_nodes, sequence_connections, None
                
        except Exception as e:
            logging.error(f"Error collecting sequence: {str(e)}")
            return sequence_nodes, sequence_connections, None
    

    def find_connection_elements_in_sequence(self, current_node: ScAddr, nrel_sequence: ScAddr) -> dict:
        """Ищет следующую ноду в последовательности через отношение nrel_basic_sequence, возвращает элементы связи"""
        try:
            template = ScTemplate()
            template.quintuple(
                current_node,                           
                sc_type.VAR_ARC >> "_main_arc",        
                sc_type.VAR_NODE >> "_next_node",      
                sc_type.VAR_PERM_POS_ARC >> "_rel_arc",
                nrel_sequence                          
            )
            
            search_results = search_by_template(template)
            
            if search_results:
                main_arc = search_results[0].get("_main_arc")
                next_node = search_results[0].get("_next_node")
                rel_arc = search_results[0].get("_rel_arc")
                
                if next_node and next_node.is_valid():
                    # Собираем все элементы связи в простой список
                    connection_elements = []
                    if main_arc and main_arc.is_valid():
                        connection_elements.append(main_arc)
                    if rel_arc and rel_arc.is_valid():
                        connection_elements.append(rel_arc)
                    
                    return {
                        "target": next_node,
                        "elements": connection_elements
                    }
            
            return None
            
        except Exception as e:
            logging.error(f"Error finding connection elements in sequence: {str(e)}")
            return None

    def create_result_structure(self, sequence_nodes: list, sequence_connections: list, nrel_sequence: ScAddr) -> ScAddr:
        """Создает структуру с последовательностью нод и отношениями nrel_basic_sequence"""
        try:
            solving_sequence = []
            # Добавляем все ноды последовательности в структуру
            solving_sequence.extend(sequence_nodes)
            
            # Добавляем все связи (коннекторы) между нодами в структуру
            solving_sequence.extend(sequence_connections)
            
            # Добавляем отношение nrel_basic_sequence в структуру только если оно есть
            if nrel_sequence:
                solving_sequence.append(nrel_sequence)
            
            return solving_sequence
            
        except Exception as e:
            logging.error(f"Error creating result structure: {str(e)}")
            return generate_node(sc_type.CONST_NODE_STRUCTURE)