from sc_client.client import connect, disconnect, search_by_template, get_link_content
from sc_client import client
from sc_client.constants import sc_type
from sc_client.models import ScAddr, ScConstruction, ScTemplate, ScLinkContent
from sc_client.constants.sc_type import ScType
from sc_kpm.identifiers import ScAlias
from sc_kpm import ScKeynodes
from sc_kpm.utils import generate_connector, generate_link, generate_node
from typing import Dict, List, Any

class SCAdapter:

    def __init__(self, url="ws://localhost:8090/ws_json"):
        self.url = url
        self._connected = False
        self.parsedSolvingSteps = None


    # --- Подключение и отключение ---
    def connect(self):
        if not self._connected:
            connect(self.url)
            self._connected = True

    def disconnect(self):
        if self._connected:
            disconnect()
            self._connected = False

    def get_parsing_result(self) -> str:
        """Просто возвращает сохраненный результат парсинга"""
        return self.parsedSolvingSteps

    def _connect_all_to_main_node(self, main_node: ScAddr, all_addrs: List[ScAddr]) -> List[ScAddr]:
        """Создаёт коннекторы между main_node и всеми элементами из списка all_addrs"""
        connector_addrs = []
        
        for addr in all_addrs:
            # Пропускаем сам main_node и уже существующие связи
            if addr == main_node:
                continue
                
            # Создаём коннектор от main_node к элементу
            connector_addr = generate_connector(sc_type.CONST_PERM_POS_ARC, main_node, addr)
            connector_addrs.append(connector_addr)
            print(f"Created connector from main node to {addr}")
        
        print(f"Created {len(connector_addrs)} connectors to main node")
        return connector_addrs

    # --- Основной метод загрузки конструкции ---
    def upload_construction(self, construction_data: Dict[str, Any]):
        """Загружает всю конструкцию в SC-память с использованием ScKeynodes"""
        try:
            self.connect()
            print("Connected to SC-server.")

            # 1. Главный узел конструкции
            construction_name = construction_data.get("construction", "unnamed")
            main_node = ScKeynodes.resolve(construction_name, sc_type.CONST_NODE_STRUCTURE)
            print(f"Created/Resolved main node: {construction_name}")

            all_addrs = []

            # 2. Создаём точки
            points = construction_data.get("points", [])
            print(f"Processing {len(points)} points...")
            points_addrs = self._create_points(points)
            all_addrs.extend(points_addrs)

            # 3. Создаём фигуры
            figures = construction_data.get("figures", [])
            print(f"Processing {len(figures)} figures...")
            figures_addrs = self._create_figures(figures)
            all_addrs.extend(figures_addrs)

            # 4. Создаём элементы конструкции (включая углы)
            construction_elements = construction_data.get("construction_elements", [])
            print(f"Processing {len(construction_elements)} construction elements...")
            elements_addrs = self._create_construction_elements(construction_elements)
            all_addrs.extend(elements_addrs)

            # 5. Создаём отношения
            relationships = construction_data.get("relationships", [])
            print(f"Processing {len(relationships)} relationships...")
            relationships_addrs = self._create_relationships(relationships)
            all_addrs.extend(relationships_addrs)

            self._connect_all_to_main_node(main_node, all_addrs)
            print("Successfully uploaded construction to SC-memory.")

            return True, all_addrs

        except Exception as e:
            import traceback
            print("Error uploading to SC:", e)
            traceback.print_exc()
            return False, []

    # --- Создание точек ---
    def _create_points(self, points: List[str]) -> List[ScAddr]:
        """Создаёт ноды для всех точек (A, B, C и т.д.)"""
        addrs = []
        
        # Если точек нет, не создаем ничего
        if not points:
            return addrs
            
        class_point = ScKeynodes.resolve("concept_point", sc_type.CONST_NODE_CLASS)
        addrs.append(class_point)

        for point_name in points:
            point_node = ScKeynodes.resolve(point_name, sc_type.CONST_NODE)
            arc_addr = generate_connector(sc_type.CONST_PERM_POS_ARC, class_point, point_node)
            addrs.extend([point_node, arc_addr])
            print(f"Created point: {point_name}")

        return addrs

    # --- Создание фигур ---
    def _create_figures(self, figures: List[Dict]) -> List[ScAddr]:
        """Создаёт ноды для всех фигур"""
        addrs = []
        
        # Определяем классы для разных типов фигур
        figure_classes = {
            "circle": "concept_circle",
            "triangle": "concept_triangle", 
            "quadrilateral": "concept_quadrilateral",
            "pentagon": "concept_pentagon",
            "hexagon": "concept_hexagon",
            "heptagon": "concept_heptagon"
        }
        
        # Собираем только те типы фигур, которые действительно есть в данных
        used_figure_types = set(figure.get("type") for figure in figures)
        
        # Резолвим только нужные классы фигур
        class_nodes = {}
        for fig_type in used_figure_types:
            class_name = figure_classes.get(fig_type)
            if class_name:
                class_node = ScKeynodes.resolve(class_name, sc_type.CONST_NODE_CLASS)
                class_nodes[fig_type] = class_node
                addrs.append(class_node)
                print(f"Resolved class for {fig_type}: {class_name}")

        for figure in figures:
            fig_type = figure.get("type", "unknown")
            fig_name = figure.get("name", "unnamed_figure")

            # Создаем фигуру с её именем
            fig_node = ScKeynodes.resolve(fig_name, sc_type.CONST_NODE)
            addrs.append(fig_node)
            print(f"Created figure: {fig_name}")
            
            if fig_type == "circle":
                circle_addrs = self._create_circle(fig_node, figure)
                addrs.extend(circle_addrs)
                
                # Связываем с соответствующим классом
                class_node = class_nodes.get("circle")
                if class_node:
                    arc_addr = generate_connector(sc_type.CONST_PERM_POS_ARC, class_node, fig_node)
                    addrs.append(arc_addr)
                    print(f"Linked circle to concept_circle")
                    
            elif fig_type in ["triangle", "quadrilateral", "pentagon", "hexagon", "heptagon"]:
                polygon_addrs = self._create_polygon(fig_node, figure)
                addrs.extend(polygon_addrs)
                
                # Связываем с соответствующим классом полигона
                class_node = class_nodes.get(fig_type)
                if class_node:
                    arc_addr = generate_connector(sc_type.CONST_PERM_POS_ARC, class_node, fig_node)
                    addrs.append(arc_addr)
                    print(f"Linked {fig_type} to {figure_classes[fig_type]}")
                else:
                    # Fallback - используем общий класс polygon
                    fallback_class = ScKeynodes.resolve("concept_polygon", sc_type.CONST_NODE_CLASS)
                    arc_addr = generate_connector(sc_type.CONST_PERM_POS_ARC, fallback_class, fig_node)
                    addrs.extend([fallback_class, arc_addr])
                    print(f"Linked {fig_type} to concept_polygon (fallback)")

        return addrs

    def generate_binary_relation(self, connector_type: ScType, src: ScAddr, trg: ScAddr, *relations: ScAddr) -> List[ScAddr]:
        """Переопределённый метод, возвращающий всю конструкцию"""
        construction = ScConstruction()
        
        # Создаём основную дугу отношения
        construction.generate_connector(connector_type, src, trg, ScAlias.RELATION_ARC)
        
        # Создаём связи для каждого отношения
        for relation in relations:
            construction.generate_connector(sc_type.CONST_PERM_POS_ARC, relation, ScAlias.RELATION_ARC)
        
        # Генерируем все элементы и возвращаем всю конструкцию
        all_elements = client.generate_elements(construction)
        return all_elements

    def generate_role_relation(self, src: ScAddr, trg: ScAddr, *rrel_nodes: ScAddr) -> List[ScAddr]:
        return self.generate_binary_relation(sc_type.CONST_PERM_POS_ARC, src, trg, *rrel_nodes)

    def generate_non_role_relation(self, src: ScAddr, trg: ScAddr, *nrel_nodes: ScAddr) -> List[ScAddr]:
        return self.generate_binary_relation(sc_type.CONST_COMMON_ARC, src, trg, *nrel_nodes)

    # --- Создание элементов конструкции ---
    def _create_construction_elements(self, elements: List[Dict]) -> List[ScAddr]:
        """Создаёт ноды для элементов конструкции (углы и т.д.)"""
        addrs = []
        for element in elements:
            if element["type"] == "angle":
                angle_addrs = self._create_angle_element(element)
                addrs.extend(angle_addrs)
        return addrs

    def _create_angle_element(self, angle_data: Dict) -> List[ScAddr]:
        """Создаёт структуру для угла"""
        addrs = []
        try:
            print("POINT01")

            # Создаем вершины угла
            vertex1 = angle_data.get("vertex1")
            vertex2 = angle_data.get("vertex2")  # Вершина угла
            vertex3 = angle_data.get("vertex3")
            angle_name = f"{vertex1}{vertex2}{vertex3}"
            print("POINT0")
            angle_node = ScKeynodes.resolve(angle_name, sc_type.CONST_NODE)
            addrs.append(angle_node)

            if vertex1 and vertex2 and vertex3:
                print("POINT1")
                vertex1_node = ScKeynodes.resolve(vertex1, sc_type.CONST_NODE)
                vertex2_node = ScKeynodes.resolve(vertex2, sc_type.CONST_NODE)
                vertex3_node = ScKeynodes.resolve(vertex3, sc_type.CONST_NODE)
                addrs.extend([vertex1_node, vertex2_node, vertex3_node])
                print("POINT2")
                
                # 1. Создаем отношение между углом и вершиной угла (vertex2)
                nrel_vertex_of_angle = ScKeynodes.resolve("nrel_vertex_of_angle", sc_type.CONST_NODE_NON_ROLE)
                vertex_arc_addrs = self.generate_non_role_relation(angle_node, vertex2_node, nrel_vertex_of_angle)
                addrs.extend([nrel_vertex_of_angle] + vertex_arc_addrs)  # РАСКРЫВАЕМ список
                print("POINT3")
                
                # 2. Создаем отрезки AB и BC (где B - вершина угла)
                edge_ab_name = f"{vertex1}{vertex2}"
                edge_bc_name = f"{vertex2}{vertex3}"
                
                # Создаем узлы для отрезков
                edge_ab_node = ScKeynodes.resolve(edge_ab_name, sc_type.CONST_NODE)
                edge_bc_node = ScKeynodes.resolve(edge_bc_name, sc_type.CONST_NODE)
                addrs.extend([edge_ab_node, edge_bc_node])
                print("POINT4")
                
                # 3. Создаем отношения между углом и отрезками
                nrel_side_of_angle = ScKeynodes.resolve("nrel_side_of_angle", sc_type.CONST_NODE_NON_ROLE)
                side_ab_arc_addrs = self.generate_non_role_relation(angle_node, edge_ab_node, nrel_side_of_angle)
                side_bc_arc_addrs = self.generate_non_role_relation(angle_node, edge_bc_node, nrel_side_of_angle)
                addrs.extend([nrel_side_of_angle] + side_ab_arc_addrs + side_bc_arc_addrs)  # РАСКРЫВАЕМ списки
                
                print(f"Created angle: {angle_name} with vertex {vertex2} and sides {edge_ab_name}, {edge_bc_name}")
                print("POINT5")
            
            # Создаем структуру измерения угла
            angle_measure = angle_data.get("angle")
            if angle_measure:
                angle_structure_addrs = self._create_angle_structure(angle_node, angle_measure)
                addrs.extend(angle_structure_addrs)
                
        except Exception as e:
            print(f"Error creating angle element: {e}")
        
        return addrs

    def _create_angle_structure(self, angle_node, angle_info) -> List[ScAddr]:
        """Создаёт структуру для хранения информации об угле (аналогично длине)"""
        addrs = []
        try:
            concept_angular_measure = ScKeynodes.resolve("concept_angular_measure", sc_type.CONST_NODE_SUPERCLASS)
            decimal_numeral_system = ScKeynodes.resolve("decimal_numeral_system", sc_type.CONST_NODE_CLASS)
            nrel_idtf = ScKeynodes.resolve("nrel_idtf", sc_type.CONST_NODE_NON_ROLE)
            class_number = ScKeynodes.resolve("number", sc_type.CONST_NODE_CLASS)
            nrel_measurement_str = str(angle_info.get("way_of_measurement"))
            nrel_measurement = ScKeynodes.resolve(f"nrel_measurement_in_{nrel_measurement_str}", sc_type.CONST_NODE_NON_ROLE)

            addrs.extend([concept_angular_measure, decimal_numeral_system, nrel_idtf, class_number, nrel_measurement])

            # Получаем значение угла
            angle_value = angle_info.get("value") if isinstance(angle_info, dict) else angle_info
            
            if angle_value is None:
                return addrs
                
            # Преобразуем в строку для создания имени узла
            value_str = str(angle_value).replace('.', '_')
            
            # 1. Создаём безымянный узел класса для угла
            anonymous_angle_node = generate_node(sc_type.CONST_NODE_CLASS)
            
            # 2. Связываем угол с безымянным узлом через ТОНКУЮ стрелку (CONST_PERM_POS_ARC)
            angle_arc_addr = generate_connector(sc_type.CONST_PERM_POS_ARC, anonymous_angle_node, angle_node)
            
            # 3. Связываем безымянный узел с concept_angular_measure через ТОНКУЮ стрелку (CONST_PERM_POS_ARC)
            measure_arc_addr = generate_connector(sc_type.CONST_PERM_POS_ARC, concept_angular_measure, anonymous_angle_node)
            
            # 4. Создаём узел для числового значения
            number_node = ScKeynodes.resolve(f"number_{value_str}", sc_type.CONST_NODE)
            
            # 5. Связываем безымянный узел с числовым узлом через ТОЛСТУЮ стрелку (CONST_PERM_POS_TUPLE)
            measurement_arc_addrs = self.generate_non_role_relation(anonymous_angle_node, number_node, nrel_measurement)
            
            # 6. Связываем числовой узел с классом number через ТОНКУЮ стрелку
            number_class_arc_addr = generate_connector(sc_type.CONST_PERM_POS_ARC, class_number, number_node)
            
            number_link = generate_link(str(angle_value))
            idtf_arc_addrs = self.generate_non_role_relation(number_node, number_link, nrel_idtf)
            
            # 7. Связываем ссылку с десятичной системой счисления через ТОНКУЮ стрелку
            decimal_arc_addr = generate_connector(sc_type.CONST_PERM_POS_ARC, decimal_numeral_system, number_link)
            
            addrs.extend([
                anonymous_angle_node, angle_arc_addr, measure_arc_addr,
                number_node, number_class_arc_addr,
                number_link, decimal_arc_addr
            ] + measurement_arc_addrs + idtf_arc_addrs)  # РАСКРЫВАЕМ списки
            
            print(f"Created angle structure for value: {angle_value}")
            
        except Exception as e:
            print(f"Error creating angle structure: {e}")
        
        return addrs

    # --- Существующие методы (оставляем без изменений) ---
    def _create_circle(self, circle_node, circle_data) -> List[ScAddr]:
        """Создаёт структуру окружности"""
        addrs = []
        center = circle_data.get("center")
        if center:
            center_node = ScKeynodes.resolve(center, sc_type.CONST_NODE)
            nrel_center = ScKeynodes.resolve("nrel_center", sc_type.CONST_NODE_NON_ROLE)
            center_arc_addrs = self.generate_non_role_relation(circle_node, center_node, nrel_center)
            addrs.extend([center_node, nrel_center] + center_arc_addrs)  # РАСКРЫВАЕМ список

        diameter_edge = circle_data.get("diameter_edge")
        if diameter_edge:
            edge_name = f"{diameter_edge['vert1']}{diameter_edge['vert2']}"
            edge_node = ScKeynodes.resolve(edge_name, sc_type.CONST_NODE)
            
            point1_node = ScKeynodes.resolve(diameter_edge['vert1'], sc_type.CONST_NODE)
            point2_node = ScKeynodes.resolve(diameter_edge['vert2'], sc_type.CONST_NODE)
            
            nrel_endpoint = ScKeynodes.resolve("nrel_endpoint", sc_type.CONST_NODE_NON_ROLE)
            endpoint1_arc_addrs = self.generate_non_role_relation(edge_node, point1_node, nrel_endpoint)
            endpoint2_arc_addrs = self.generate_non_role_relation(edge_node, point2_node, nrel_endpoint)
            
            nrel_diameter = ScKeynodes.resolve("nrel_diameter", sc_type.CONST_NODE_NON_ROLE)
            diameter_arc_addrs = self.generate_non_role_relation(circle_node, edge_node, nrel_diameter)
            
            addrs.extend([
                edge_node, point1_node, point2_node, nrel_endpoint, nrel_diameter
            ] + endpoint1_arc_addrs + endpoint2_arc_addrs + diameter_arc_addrs)  # РАСКРЫВАЕМ списки
            
            if diameter_edge.get('length'):
                length_addrs = self._create_length_structure(edge_node, diameter_edge['length'])
                addrs.extend(length_addrs)

        return addrs

    def _create_polygon(self, polygon_node, polygon_data) -> List[ScAddr]:
        """Создаёт структуру полигона"""
        addrs = []
        
        # Обработка вершин (если они есть) - только явно объявленные точки
        vertices = polygon_data.get("vertices", [])
        for vertex_name in vertices:
            vertex_node = ScKeynodes.resolve(vertex_name, sc_type.CONST_NODE)
            nrel_angle = ScKeynodes.resolve("nrel_angle", sc_type.CONST_NODE_NON_ROLE)
            angle_arc_addrs = self.generate_non_role_relation(polygon_node, vertex_node, nrel_angle)
            addrs.extend([vertex_node, nrel_angle] + angle_arc_addrs)

        # Обработка сторон - создаем только отрезки, без точек
        input_data = polygon_data.get("input_data")
        if input_data and hasattr(input_data, 'edges') and input_data.edges:
            for edge_input in input_data.edges:
                # Имя отрезка формируется из строк vert1 и vert2
                edge_name = f"{edge_input.vert1}{edge_input.vert2}"
                edge_node = ScKeynodes.resolve(edge_name, sc_type.CONST_NODE)
                
                nrel_side = ScKeynodes.resolve("nrel_side", sc_type.CONST_NODE_NON_ROLE)
                side_arc_addrs = self.generate_non_role_relation(polygon_node, edge_node, nrel_side)
                
                addrs.extend([edge_node, nrel_side] + side_arc_addrs)
                
                if edge_input.length:
                    length_addrs = self._create_length_structure(edge_node, edge_input.length.dict())
                    addrs.extend(length_addrs)
        
        return addrs

    def _create_length_structure(self, edge_node, length_info) -> List[ScAddr]:
        """Создаёт структуру для хранения информации о длине стороны"""
        addrs = []
        try:
            concept_length = ScKeynodes.resolve("concept_length", sc_type.CONST_NODE_SUPERCLASS)
            class_number = ScKeynodes.resolve("number", sc_type.CONST_NODE_CLASS)
            nrel_measurement_str = str(length_info.get("way_of_measurement"))
            nrel_measurement = ScKeynodes.resolve(f"nrel_measurement_in_{nrel_measurement_str}", sc_type.CONST_NODE_NON_ROLE)

            addrs.extend([concept_length, class_number, nrel_measurement])

            length_value = length_info.get("value") if isinstance(length_info, dict) else length_info
            
            if length_value is None:
                return addrs
            
            # Преобразуем значение в float для проверки на целочисленность
            try:
                float_value = float(length_value)
                # Проверяем, является ли число целым
                if float_value.is_integer():
                    value_str = str(int(float_value))  # Убираем .0
                else:
                    value_str = str(float_value).replace('.', '_')  # Заменяем точку на подчеркивание
            except (ValueError, TypeError):
                # Если не удалось преобразовать в число, используем строку как есть
                value_str = str(length_value).replace('.', '_')
            
            anonymous_length_node = generate_node(sc_type.CONST_NODE_CLASS)
            
            edge_arc_addr = generate_connector(sc_type.CONST_PERM_POS_ARC, anonymous_length_node, edge_node)
            length_arc_addr = generate_connector(sc_type.CONST_PERM_POS_ARC, concept_length, anonymous_length_node)
            
            number_node = ScKeynodes.resolve(f"number_{value_str}", sc_type.CONST_NODE)
            
            measurement_arc_addrs = self.generate_non_role_relation(anonymous_length_node, number_node, nrel_measurement)
            number_class_arc_addr = generate_connector(sc_type.CONST_PERM_POS_ARC, class_number, number_node)
            
            addrs.extend([
                anonymous_length_node, edge_arc_addr, length_arc_addr,
                number_node, number_class_arc_addr,
            ] + measurement_arc_addrs)  # РАСКРЫВАЕМ списки
            
            print(f"Created length structure for value: {length_value} (node: number_{value_str})")
            
        except Exception as e:
            print(f"Error creating length structure: {e}")
        
        return addrs

    def _create_relationships(self, relationships: List[Dict]) -> List[ScAddr]:
        """Создаёт структуры для отношений между любыми сущностями в SC-памяти."""
        addrs = []
        for i, relationship in enumerate(relationships):
            rel_type = relationship.get("type", "role")
            rel_name = relationship.get("name", f"relationship_{i}")
            oriented = relationship.get("oriented", True)  # Получаем ориентацию

            source_entity_name = relationship.get("source_entity")
            target_entity_name = relationship.get("target_entity")
            
            print(f'Creating relationship: {source_entity_name} -> {target_entity_name} (type: {rel_type}, name: {rel_name}, oriented: {oriented})')

            source_node = ScKeynodes.resolve(str(source_entity_name), sc_type.CONST_NODE)
            target_node = ScKeynodes.resolve(str(target_entity_name), sc_type.CONST_NODE)
            addrs.extend([source_node, target_node])

            if rel_type == "nonrole":
                nrel_relation = ScKeynodes.resolve(f"nrel_{rel_name}", sc_type.CONST_NODE_NON_ROLE)
                
                # ВЫБИРАЕМ ТИП ДУГИ В ЗАВИСИМОСТИ ОТ ОРИЕНТАЦИИ
                if oriented:
                    connector_type = sc_type.CONST_COMMON_ARC  # Ориентированная дуга
                else:
                    connector_type = sc_type.CONST_COMMON_EDGE  # Неориентированное ребро
                    
                relation_arc_addrs = self.generate_binary_relation(connector_type, source_node, target_node, nrel_relation)
                addrs.extend([nrel_relation] + relation_arc_addrs)
                print(f"Created non-role relation: nrel_{rel_name} (oriented: {oriented})")
            else:
                rrel_relation = ScKeynodes.resolve(f"rrel_{rel_name}", sc_type.CONST_NODE_ROLE)
                relation_arc_addrs = self.generate_role_relation(source_node, target_node, rrel_relation)
                addrs.extend([rrel_relation] + relation_arc_addrs)
                print(f"Created role relation: rrel_{rel_name}")

        return addrs

    # --- Контекстный менеджер ---
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()