"""
Agent for searching geometric constructions in OSTIS knowledge base
"""

import logging
from sc_client.models import ScAddr, ScLinkContentType
from sc_client.constants import sc_type
from sc_client.client import search_by_template
from sc_client.models import ScTemplate
from sc_kpm.sc_sets import ScStructure
from sc_client.client import get_elements_types

from sc_kpm import ScAgentClassic, ScResult, ScKeynodes
from sc_kpm.utils import (
    generate_link, generate_node, generate_connector, get_element_system_identifier
)
from sc_kpm.utils.action_utils import (
    generate_action_result,
    finish_action_with_status,
    get_action_arguments
)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="[%d-%b-%y %H:%M:%S]"
)


class GeometrySearchAgent(ScAgentClassic):
    def __init__(self):
        super().__init__("action_search_geometry_constructions")

    def on_event(self, action_class: ScAddr, arc: ScAddr, action: ScAddr) -> ScResult:
        result = self.run(action)
        is_successful = result == ScResult.OK
        finish_action_with_status(action, is_successful)
        logging.info("GeometrySearchAgent finished %s",
                     "successfully" if is_successful else "unsuccessfully")
        return result

    def run(self, action_node: ScAddr) -> ScResult:
        logging.info("GeometrySearchAgent started")
        
        try:
            # Получаем аргументы - структуру для поиска
            arguments = get_action_arguments(action_node, 1)
            if not arguments:
                logging.error("No arguments provided")
                return ScResult.ERROR
                
            search_structure = arguments[0]
            
            # Проверяем, что это действительно структура
            if not self.is_structure(search_structure):
                logging.error("Input argument is not a structure")
                return ScResult.ERROR
            
            logging.info(f"=== НАЧАЛО ПОИСКА ===")
            logging.info(f"Входная структура: {search_structure.value}")
            
            # Шаг 1: Получаем все структуры по паттерну
            candidate_structures = self.find_structures_by_pattern()
            logging.info(f"Найдено структур-кандидатов: {len(candidate_structures)}")
            
            # Шаг 2: Получаем все ноды входной структуры
            input_nodes = self.get_all_nodes_from_structure(search_structure)
            logging.info(f"Ноды входной структуры ({len(input_nodes)}):")
            for node in input_nodes:
                node_idtf = get_element_system_identifier(node) or f"unknown_{node.value}"
                logging.info(f"  - {node_idtf}")
            
            # Шаг 3: Фильтруем кандидатов, проверяя тройки и пятёрки
            matching_structures = self.filter_structures_by_triples_and_quintuples(
                candidate_structures, search_structure, input_nodes
            )
            
            logging.info(f"Найдено подходящих структур: {len(matching_structures)}")
            
            # Шаг 4: Создаем результирующую структуру
            found_tasks = self.create_result_structure(matching_structures)
            
            generate_action_result(action_node, *found_tasks)
            logging.info("=== ПОИСК ЗАВЕРШЕН ===")
            
            return ScResult.OK
            
        except Exception as e:
            logging.error(f"Error in GeometrySearchAgent: {str(e)}")
            return ScResult.ERROR

    def is_structure(self, element: ScAddr) -> bool:
        """Проверяет, является ли элемент структурой"""
        try:
            from sc_client.client import get_elements_types
            element_types = get_elements_types(element)
            return element_types and element_types[0].is_structure()
        except Exception as e:
            logging.error(f"Error checking element type: {str(e)}")
            return False
        
    def find_structures_by_pattern(self) -> list:
        """Шаг 1: Ищет структуры по паттерну CONST_NODE -> STRUCT через nrel_context_of_action"""
        structures = []
        
        try:
            template = ScTemplate()
            
            nrel_context = ScKeynodes.resolve("nrel_context_of_the_action", sc_type.CONST_NODE_NON_ROLE)
            
            template.quintuple(
                sc_type.VAR_NODE >> "_const_node",         
                sc_type.VAR_COMMON_ARC >> "_arc",         
                sc_type.VAR_NODE_STRUCTURE >> "_structure",         
                sc_type.VAR_PERM_POS_ARC >> "_context_arc",  
                nrel_context                                 
            )
            
            search_results = search_by_template(template)
            
            for result in search_results:
                structure_addr = result.get("_structure")
                const_node_addr = result.get("_const_node")
                print(get_element_system_identifier(const_node_addr))
                
                if structure_addr and structure_addr.is_valid() and self.is_structure(structure_addr):
                    structures.append({
                        "structure": structure_addr,
                        "const_node": const_node_addr
                    })
                    
            logging.info(f"Найдено структур по паттерну: {len(structures)}")
                    
        except Exception as e:
            logging.error(f"Error finding structures by pattern: {str(e)}")
            
        return structures

    def get_all_nodes_from_structure(self, structure: ScAddr) -> list:
        """Шаг 2: Получает все ноды из структуры"""
        nodes = []
        
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
                    nodes.append(element)
                    
        except Exception as e:
            logging.error(f"Error getting nodes from structure: {str(e)}")
            
        return nodes

    def filter_structures_by_triples_and_quintuples(self, candidate_structures: list, 
                                                search_structure: ScAddr, input_nodes: list) -> list:
        """Фильтрует структуры, проверяя тройки и пятёрки"""
        matching_structures = []
        
        remaining_candidates = candidate_structures.copy()
        
        logging.info(f"Кандидатов до начала отсеивания: {len(remaining_candidates)}")
        
        try:
            for node in input_nodes:
                node_idtf = get_element_system_identifier(node) or f"unknown_{node.value}"
                logging.info(f"Обрабатываем ноду: {node_idtf}")
                
                # Получаем все тройки и пятёрки для текущей ноды
                triples_and_quintuples = self.get_triples_and_quintuples_for_node(node, search_structure)
                
                # Фильтруем кандидатов
                remaining_candidates = self.filter_candidates_by_patterns(
                    remaining_candidates, triples_and_quintuples
                )
                
                logging.info(f"После обработки ноды осталось кандидатов: {len(remaining_candidates)}")
                
                if not remaining_candidates:
                    break
            
            # Оставшиеся кандидаты - это подходящие структуры
            matching_structures = remaining_candidates
            
        except Exception as e:
            logging.error(f"Error filtering structures: {str(e)}")
            
        return matching_structures


    def get_triples_and_quintuples_for_node(self, node: ScAddr, structure: ScAddr) -> list:
        """Получает все тройки и пятёрки для ноды, где все связанные ноды принадлежат структуре"""
        patterns = []
        
        try:
            # Шаблон 1: Тройки с тонкими дугами (исходящие)
            template_outgoing = ScTemplate()
            template_outgoing.triple(
                node >> "_source",
                sc_type.VAR_PERM_POS_ARC >> "_arc",
                sc_type.VAR_NODE >> "_target"
            )
            
            # Шаблон 2: Пятёрки с ролевыми отношениями (ориентированное ребро)
            template_quintuple_role = ScTemplate()
            template_quintuple_role.quintuple(
                node >> "_source",
                sc_type.VAR_ARC >> "_main_arc",
                sc_type.VAR_NODE >> "_target",
                sc_type.VAR_ARC >> "_rel_arc", 
                sc_type.VAR_NODE_ROLE >> "_relation"
            )
            
            # Шаблон 3: Пятёрки с не-ролевыми отношениями (ориентированное ребро)
            template_quintuple_nonrole = ScTemplate()
            template_quintuple_nonrole.quintuple(
                node >> "_source",
                sc_type.VAR_ARC >> "_main_arc",
                sc_type.VAR_NODE >> "_target", 
                sc_type.VAR_ARC >> "_rel_arc",
                sc_type.VAR_NODE_NON_ROLE >> "_relation"
            )
            
            # Шаблон 4: Пятёрки с ролевыми отношениями (неориентированное ребро - EDGE_COMMON)
            template_quintuple_role_edge = ScTemplate()
            template_quintuple_role_edge.quintuple(
                node >> "_source",
                sc_type.VAR_COMMON_EDGE >> "_main_edge", 
                sc_type.VAR_NODE >> "_target",
                sc_type.VAR_ARC >> "_rel_arc", 
                sc_type.VAR_NODE_ROLE >> "_relation"
            )
            
            # Шаблон 5: Пятёрки с не-ролевыми отношениями (неориентированное ребро - EDGE_COMMON)
            template_quintuple_nonrole_edge = ScTemplate()
            template_quintuple_nonrole_edge.quintuple(
                node >> "_source",
                sc_type.VAR_COMMON_EDGE >> "_main_edge", 
                sc_type.VAR_NODE >> "_target", 
                sc_type.VAR_ARC >> "_rel_arc",
                sc_type.VAR_NODE_NON_ROLE >> "_relation"
            )
            
            # Выполняем поиски только для исходящих отношений
            patterns.extend(self.execute_template_search(template_outgoing, "triple_outgoing", structure))
            patterns.extend(self.execute_template_search(template_quintuple_role, "quintuple_role", structure))
            patterns.extend(self.execute_template_search(template_quintuple_nonrole, "quintuple_nonrole", structure))
            patterns.extend(self.execute_template_search(template_quintuple_role_edge, "quintuple_role_edge", structure))
            patterns.extend(self.execute_template_search(template_quintuple_nonrole_edge, "quintuple_nonrole_edge", structure))
            
            self.log_pattern_elements(patterns)
            
        except Exception as e:
            logging.error(f"Error getting triples and quintuples: {str(e)}")
            
        return patterns

    def execute_template_search(self, template: ScTemplate, pattern_type: str, structure: ScAddr) -> list:
        """Выполняет поиск по шаблону и возвращает результаты, где все элементы принадлежат структуре"""
        patterns = []
        
        try:
            search_results = search_by_template(template)
            
            for result in search_results:
                pattern_data = {
                    "type": pattern_type,
                    "elements": {}
                }
                
                aliases = ["_source", "_target", "_arc", "_main_arc", "_rel_arc", "_relation", "_main_edge"]
                
                for alias in aliases:
                    try:
                        element = result.get(alias)
                        if element and element.is_valid():
                            pattern_data["elements"][alias] = element
                    except:
                        pass
                
                # Проверяем, что ВСЕ элементы паттерна (ноды и дуги) принадлежат нашей структуре
                if self.all_pattern_elements_belong_to_structure(pattern_data, structure):
                    patterns.append(pattern_data)
                else:
                    logging.debug(f"Паттерн {pattern_type} отфильтрован - не все элементы принадлежат структуре")
                    
        except Exception as e:
            logging.error(f"Error executing template search for {pattern_type}: {str(e)}")
                
        return patterns

    def all_pattern_elements_belong_to_structure(self, pattern: dict, structure: ScAddr) -> bool:
        """Проверяет, что все элементы паттерна (ноды и дуги) принадлежат структуре"""
        try:
            for alias, element in pattern["elements"].items():
                if element and element.is_valid():
                    if not self.element_belongs_to_structure(element, structure):
                        logging.debug(f"Элемент {alias} не принадлежит структуре: {element.value}")
                        return False
            return True
        except Exception as e:
            logging.error(f"Error checking pattern elements belonging: {str(e)}")
            return False

    def element_belongs_to_structure(self, element: ScAddr, structure: ScAddr) -> bool:
        """Проверяет, что элемент принадлежит структуре"""
        try:
            template = ScTemplate()
            template.triple(
                structure,
                sc_type.VAR_PERM_POS_ARC >> "_check_arc",
                element
            )
            
            results = search_by_template(template)
            return len(results) > 0
        except Exception as e:
            logging.error(f"Error checking element belonging: {str(e)}")
            return False

    def log_pattern_elements(self, patterns: list):
        """Логирует системные идентификаторы и типы элементов паттернов"""
        for pattern in patterns:
            logging.info(f"Паттерн {pattern['type']}:")
            for alias, element in pattern["elements"].items():
                if element and element.is_valid():
                    element_idtf = get_element_system_identifier(element) or f"unknown_{element.value}"
                    element_type = self.get_element_type(element)
                    type_name = self.get_type_name(element_type)
                    logging.info(f"  - {alias}: {element_idtf} (type: {type_name})")

    def get_type_name(self, sc_type_obj) -> str:
        """Получает читаемое имя типа"""
        if sc_type_obj is None:
            return "unknown"
        
        if sc_type_obj.is_node():
            if sc_type_obj.is_const():
                if sc_type_obj.is_struct():
                    return "const_node_structure"
                else:
                    return "const_node"
            else:
                return "var_node"
        elif sc_type_obj.is_link():
            return "link"
        elif sc_type_obj.is_connector():
            return "connector"
        else:
            return "unknown"

    def filter_candidates_by_patterns(self, candidates: list, patterns: list) -> list:
        """Фильтрует кандидатов по найденным паттернам"""
        filtered_candidates = []
        
        try:
            logging.info(f"Фильтруем {len(candidates)} кандидатов по {len(patterns)} паттернам")
            
            for candidate in candidates:
                candidate_structure = candidate["structure"]
                candidate_idtf = get_element_system_identifier(candidate_structure) or f"structure_{candidate_structure.value}"
                candidate_valid = True
                
                # Проверяем каждый паттерн в кандидате
                for pattern in patterns:
                    pattern_found = self.check_pattern_in_candidate(candidate_structure, pattern)
                    if not pattern_found:
                        candidate_valid = False
                        logging.debug(f"Кандидат {candidate_idtf} отсеян по паттерну {pattern['type']}")
                        break
                
                if candidate_valid:
                    filtered_candidates.append(candidate)
                    logging.debug(f"Кандидат {candidate_idtf} прошел проверку")
                    
            logging.info(f"После фильтрации осталось кандидатов: {len(filtered_candidates)}")
            
        except Exception as e:
            logging.error(f"Error filtering candidates: {str(e)}")
            
        return filtered_candidates

    def check_pattern_in_candidate(self, candidate_structure: ScAddr, pattern: dict) -> bool:
        """Проверяет, содержится ли паттерн в структуре-кандидате с использованием переменных дуг и безымянных нод"""
        try:
            check_template = ScTemplate()
            
            for alias, element in pattern["elements"].items():
                if (element and element.is_valid() and 
                    not alias.endswith("_arc") and 
                    alias not in ["_main_arc", "_rel_arc", '_main_edge']):
                    
                    element_idtf = get_element_system_identifier(element)
                    logging.info(f"Ищем ноду в паттерне: {alias} = {element_idtf}")
                    
                    # Если нода безымянная, используем переменную ноду того же типа
                    if not element_idtf or element_idtf.startswith("unknown_") or element_idtf.startswith("element_") or get_elements_types(element)[0] == sc_type.CONST_NODE:
                        element_type = self.get_element_type(element)
                        
                        if element_type.is_node():
                            if element_type.is_const():
                                if element_type == sc_type.CONST_NODE_CLASS:
                                    logging.error("JHGLKFLKSFLSKJDFLSKJFLD")
                                    check_template.triple(
                                        candidate_structure,
                                        sc_type.VAR_PERM_POS_ARC >> f"_struct_arc_{alias}",
                                        sc_type.VAR_NODE_CLASS >> f"_var_node_{alias}" 
                                    )
                                else:
                                    check_template.triple(
                                        candidate_structure,
                                        sc_type.VAR_PERM_POS_ARC >> f"_struct_arc_{alias}",
                                        sc_type.VAR_NODE >> f"_var_node_{alias}"  
                                    )
                            else:
                                check_template.triple(
                                    candidate_structure,
                                    sc_type.VAR_PERM_POS_ARC >> f"_struct_arc_{alias}",
                                    sc_type.VAR_NODE >> f"_var_node_{alias}"  
                                )
                        else:
                            check_template.triple(
                                candidate_structure,
                                sc_type.VAR_PERM_POS_ARC >> f"_struct_arc_{alias}",
                                sc_type.VAR_NODE >> f"_var_node_{alias}" 
                            )
                    else:
                        check_template.triple(
                            candidate_structure,
                            sc_type.VAR_PERM_POS_ARC >> f"_struct_arc_{alias}",
                            element
                        )
        
            if pattern["type"].startswith("triple"):
                self.reconstruct_triple_pattern_with_variable_elements(check_template, pattern)
            elif pattern["type"].startswith("quintuple"):
                self.reconstruct_quintuple_pattern_with_variable_elements(check_template, pattern)
            
            results = search_by_template(check_template)
            found = len(results) > 0
            
            if found:
                self.log_found_pattern_in_candidate(candidate_structure, pattern, results[0])
                logging.debug(f"Паттерн {pattern['type']} найден в кандидате")
            else:
                logging.debug(f"Паттерн {pattern['type']} НЕ найден в кандидате")
                
            return found
                
        except Exception as e:
            logging.error(f"Error checking pattern in candidate: {str(e)}")
            return False
    

    def log_found_pattern_in_candidate(self, candidate_structure: ScAddr, pattern: dict, search_result):
        """Логирует найденный паттерн в структуре-кандидате с идентификаторами нод"""
        try:
            candidate_idtf = get_element_system_identifier(candidate_structure) or f"structure_{candidate_structure.value}"
            logging.info(f"=== НАЙДЕН ПАТТЕРН В СТРУКТУРЕ-КАНДИДАТЕ {candidate_idtf} ===")
            logging.info(f"Тип паттерна: {pattern['type']}")
            
            logging.info("Элементы исходного паттерна:")
            for alias, element in pattern["elements"].items():
                if element and element.is_valid():
                    element_idtf = get_element_system_identifier(element) or f"unknown_{element.value}"
                    element_type = self.get_element_type(element)
                    type_name = self.get_type_name(element_type)
                    logging.info(f"  - {alias}: {element_idtf} (type: {type_name}, addr: {element.value})")
            
            logging.info("Найденные элементы в кандидате:")
            for alias in pattern["elements"].keys():
                if alias in ["_source", "_target", "_relation"]:
                    try:
                        found_element = search_result.get(f"_var_node_{alias}")
                        if found_element and found_element.is_valid():
                            found_idtf = get_element_system_identifier(found_element) or f"unknown_{found_element.value}"
                            found_type = self.get_element_type(found_element)
                            found_type_name = self.get_type_name(found_type)
                            logging.info(f"  - {alias}: {found_idtf} (type: {found_type_name}, addr: {found_element.value})")
                    except:
                        element = pattern["elements"][alias]
                        if element and element.is_valid():
                            element_idtf = get_element_system_identifier(element) or f"unknown_{element.value}"
                            logging.info(f"  - {alias}: {element_idtf} (конкретный элемент)")
            
            logging.info("=" * 60)
            
        except Exception as e:
            logging.error(f"Error logging found pattern: {str(e)}")

    def get_element_type(self, element: ScAddr) -> sc_type:
        """Получает тип элемента"""
        try:
            
            element_types = get_elements_types(element)
            return element_types[0] if element_types else sc_type.UNKNOWN
        except Exception as e:
            logging.error(f"Error getting element type: {str(e)}")
            return sc_type.UNKNOWN

    def reconstruct_triple_pattern_with_variable_elements(self, template: ScTemplate, pattern: dict):
        """Восстанавливает тройку в шаблоне проверки с переменными дугами и безымянными нодами"""
        try:
            source = None
            target = None
            
            for alias, element in pattern["elements"].items():
                if alias == "_source":
                    source = self.get_element_for_reconstruction(element, "_source")
                elif alias == "_target":
                    target = self.get_element_for_reconstruction(element, "_target")
            
            if source and target:
                template.triple(
                    source,
                    sc_type.VAR_PERM_POS_ARC >> "_var_arc", 
                    target
                )
                
        except Exception as e:
            logging.error(f"Error reconstructing triple pattern with variable elements: {str(e)}")

    def reconstruct_quintuple_pattern_with_variable_elements(self, template: ScTemplate, pattern: dict):
        """Восстанавливает пятёрку в шаблоне проверки с переменными дугами и безымянными нодами"""
        try:
            source = None
            target = None
            relation = None
            main_arc_type = sc_type.VAR_COMMON_ARC
            
            for alias, element in pattern["elements"].items():
                if alias == "_source":
                    source = self.get_element_for_reconstruction(element, "_source")
                elif alias == "_target":
                    target = self.get_element_for_reconstruction(element, "_target")
                elif alias == "_relation":
                    relation = self.get_element_for_reconstruction(element, "_relation")
                elif alias == "_main_arc" or alias == "_main_edge":
                    print(f"asdhdfjgkjfdkd {alias}")
                    original_arc_type = self.get_element_type(element)
                    if original_arc_type == sc_type.CONST_COMMON_EDGE:
                        main_arc_type = sc_type.VAR_COMMON_EDGE
                    else:
                        main_arc_type = sc_type.VAR_COMMON_ARC
            
            if source and target and relation:
                template.quintuple(
                    source,
                    main_arc_type >> "_var_main_arc",  
                    target,
                    sc_type.VAR_PERM_POS_ARC >> "_var_rel_arc",   
                    relation
                )
                
        except Exception as e:
            logging.error(f"Error reconstructing quintuple pattern with variable elements: {str(e)}")

    def get_element_for_reconstruction(self, element: ScAddr, alias: str):
        """Возвращает элемент для реконструкции паттерна (конкретный или переменный)"""
        try:
            element_idtf = get_element_system_identifier(element)
            
            if not element_idtf or element_idtf.startswith("unknown_") or element_idtf.startswith("element_"):
                element_type = self.get_element_type(element)
                
                if element_type.is_node():
                    if element_type.is_const():
                        if element_type == sc_type.CONST_NODE_CLASS:
                            logging.error("asdfasfawadsd")
                            return sc_type.VAR_NODE_CLASS >> f"_var_node_{alias}"
                        else:
                            return sc_type.VAR_NODE >> f"_var_node_{alias}"
                    else:
                        return sc_type.VAR_NODE >> f"_var_node_{alias}"
                else:
                    return sc_type.VAR_NODE >> f"_var_node_{alias}"
            else:
                return element
                
        except Exception as e:
            logging.error(f"Error getting element for reconstruction: {str(e)}")
            return sc_type.VAR_NODE >> f"_var_node_{alias}"
        
    def create_result_structure(self, matching_structures: list) -> list[ScAddr]:
        """Создает структуру с результатами поиска, добавляя CONST_NODE из подходящих структур"""
        try:
            found_taks = []
            # Для каждой подходящей структуры находим CONST_NODE через пятёрку и добавляем его
            for struct_data in matching_structures:
                structure_addr = struct_data["structure"]
                
                found_taks.extend(self.find_const_nodes_for_structure(structure_addr))
            
            logging.info(f"Создана результирующая структура с {len(matching_structures)} найденными структурами")
            return found_taks
            
        except Exception as e:
            logging.error(f"Error creating result structure: {str(e)}")
            return generate_node(sc_type.CONST_NODE_STRUCTURE)

    def find_const_nodes_for_structure(self, structure_addr: ScAddr) -> list:
        """Находит все CONST_NODE, связанные со структурой через паттерн пятёрки"""
        const_nodes = []
        
        try:
            template = ScTemplate()
            
            nrel_context = ScKeynodes.resolve("nrel_context_of_the_action", sc_type.CONST_NODE_NON_ROLE)
            
            template.quintuple(
                sc_type.VAR_NODE >> "_const_node",          
                sc_type.VAR_COMMON_ARC >> "_arc",              
                structure_addr,                              
                sc_type.VAR_PERM_POS_ARC >> "_context_arc",  
                nrel_context                                 
            )
            
            search_results = search_by_template(template)
            
            for result in search_results:
                const_node = result.get("_const_node")
                if const_node and const_node.is_valid():
                    const_nodes.append(const_node)
                    logging.info(f"Найден CONST_NODE для структуры {structure_addr.value}: {get_element_system_identifier(const_node) or f'unknown_{const_node.value}'}")
                    
        except Exception as e:
            logging.error(f"Error finding const nodes for structure: {str(e)}")
            
        return const_nodes