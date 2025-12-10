# pipeline_runner.py
import os
import asyncio
import subprocess
import time
import threading
from concurrent.futures import Future
import time
import uvicorn
import json
from fastapi import FastAPI, HTTPException, BackgroundTasks
from sc_client.client import connect, disconnect
from sc_client.models import ScAddr, ScLinkContent, ScLinkContentType
from sc_client.constants import sc_type
from sc_kpm import ScKeynodes
from sc_kpm.utils import generate_link, generate_connector, generate_node
from endpoints.sc_send import SCAdapter
from contextlib import asynccontextmanager

# Глобальные переменные для управления процессом
pipeline_processes = {}
pipeline_results = {}
sc_client_url = "ws://localhost:8090"

async def run_script_async(script_name):
    """Асинхронный запуск Python скрипта"""
    try:
        process = await asyncio.create_subprocess_exec(
            'python3', script_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        pipeline_processes[script_name] = process
        print(f"Запущен скрипт: {script_name}")
        return process
    except Exception as e:
        print(f"Ошибка запуска {script_name}: {e}")
        return None

async def start_servers():
    """Запуск всех необходимых серверов"""
    scripts = ['server.py']
    
    tasks = [run_script_async(script) for script in scripts]
    await asyncio.gather(*tasks)
    
    # Даем время серверам запуститься
    await asyncio.sleep(5)
    print("Все серверы запущены")

def check_servers_ready():
    """Проверка готовности серверов - для WebSocket соединения"""
    try:
        # Пробуем подключиться к WebSocket серверу SC-памяти
        from sc_client.client import connect, disconnect
        connect("ws://localhost:8090")
        disconnect()
        return True
    except Exception as e:
        print(f"SC-сервер не готов: {e}")
        return False

async def wait_for_servers():
    """Ожидание готовности серверов"""
    max_attempts = 100
    for attempt in range(max_attempts):
        if check_servers_ready():
            print("Серверы готовы к работе")
            return True
        print(f"Ожидание серверов... ({attempt + 1}/{max_attempts})")
        await asyncio.sleep(2)
    print("Таймаут ожидания серверов")
    return False

async def initialize_pipeline():
    """Инициализация всего пайплайна"""
    print("=== ИНИЦИАЛИЗАЦИЯ ПАЙПЛАЙНА ===")
    
    # Подключаемся к SC-памяти
    try:
        connect(sc_client_url)
        print("Подключение к SC-памяти установлено")
    except Exception as e:
        print(f"Ошибка подключения к SC-памяти: {e}")
    
    # Запускаем серверы
    await start_servers()
    
    # Ждем готовности
    if not await wait_for_servers():
        raise Exception("Серверы не запустились")
    
    print("Пайплайн инициализирован и готов к работе")
    return True

def generate_role_relation(src: ScAddr, trg: ScAddr, relation: ScAddr):
    """Создает связь с указанным отношением"""
    edge = generate_connector(sc_type.CONST_PERM_POS_ARC, src, trg)
    generate_connector(sc_type.CONST_PERM_POS_ARC, relation, edge)
    return edge

def start_agent(agent_identifier: str, agent_argument: ScAddr) -> ScAddr:
    """Запускает агента с аргументом"""
    try:
        # Получаем системные узлы с указанием типов
        action_node = ScKeynodes.resolve('action', sc_type.CONST_NODE_CLASS)
        action_initiated_node = ScKeynodes.resolve('action_initiated', sc_type.CONST_NODE_ROLE)
        rrel_1_node = ScKeynodes.resolve('rrel_1', sc_type.CONST_NODE_ROLE)
        agent_node = ScKeynodes.resolve(agent_identifier, sc_type.CONST_NODE_CLASS)
        
        print(f"Поиск системных узлов для агента {agent_identifier}:")
        print(f"  action: {action_node.value if action_node else 'не найден'}")
        print(f"  action_initiated: {action_initiated_node.value if action_initiated_node else 'не найден'}")
        print(f"  rrel_1: {rrel_1_node.value if rrel_1_node else 'не найден'}")
        print(f"  agent: {agent_node.value if agent_node else 'не найден'}")
        
        if not all([action_node, action_initiated_node, rrel_1_node, agent_node]):
            missing = []
            if not action_node: missing.append("action")
            if not action_initiated_node: missing.append("action_initiated") 
            if not rrel_1_node: missing.append("rrel_1")
            if not agent_node: missing.append(agent_identifier)
            print(f"Ошибка: не найдены системные узлы: {', '.join(missing)}")
            return None
            
        # Создаем узел экземпляра действия
        agent_instance_node = generate_node(sc_type.CONST_NODE)
        print(f"Создан экземпляр действия: {agent_instance_node.value}")
        
        # Связываем с классом action
        action_arc = generate_connector(sc_type.CONST_PERM_POS_ARC, action_node, agent_instance_node)
        print(f"Связь с классом action: {action_arc.value}")
        
        # Связываем с конкретным агентом
        agent_arc = generate_connector(sc_type.CONST_PERM_POS_ARC, agent_node, agent_instance_node)
        print(f"Связь с агентом: {agent_arc.value}")
        
        # Добавляем аргумент через rrel_1
        if agent_argument and agent_argument.is_valid():
            arg_arc = generate_role_relation(agent_instance_node, agent_argument, rrel_1_node)
            print(f"Добавлен аргумент {agent_argument.value} через rrel_1: {arg_arc.value}")
        else:
            print("Предупреждение: аргумент невалиден или отсутствует")
        
        # Помечаем как инициированное действие
        initiated_arc = generate_connector(sc_type.CONST_PERM_POS_ARC, action_initiated_node, agent_instance_node)
        print(f"Помечено как инициированное: {initiated_arc.value}")
        
        print(f"Агент {agent_identifier} успешно запущен с экземпляром {agent_instance_node.value}")
        return agent_instance_node
        
    except Exception as e:
        print(f"Ошибка запуска агента {agent_identifier}: {e}")
        import traceback
        traceback.print_exc()
        return None

def wait_for_agent_result(action_node: ScAddr, timeout: int = 300) -> dict:
    """Ожидает результат выполнения агента - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    try:
        from sc_client.client import search_by_template
        from sc_client.models import ScTemplate
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # ПЕРВОЕ: Проверяем статус выполнения действия
            finished_status = check_action_finished(action_node)
            
            if finished_status == "finished":
                print(f"Действие {action_node.value} завершено, ищем результат...")
                # Ищем результат через отношение nrel_result
                nrel_result = ScKeynodes.resolve("nrel_result", sc_type.CONST_NODE_NON_ROLE)
                
                if nrel_result and nrel_result.is_valid():
                    template = ScTemplate()
                    template.quintuple(
                        action_node,
                        sc_type.VAR_ARC >> "_result_arc",
                        sc_type.VAR_NODE >> "_result_element",
                        sc_type.VAR_PERM_POS_ARC >> "_rel_arc", 
                        nrel_result
                    )
                    
                    results = search_by_template(template)
                    
                    for result_item in results:
                        result_element = result_item.get("_result_element")
                        if result_element and result_element.is_valid():
                            print(f"Найден результат через nrel_result: {result_element.value}")
                            return {
                                "status": "success", 
                                "result": f"structure_{result_element.value}",
                                "result_addr": result_element
                            }
                
                # Если результат не найден, но действие завершено
                print(f"Действие завершено, но результат не найден. Возвращаем действие как результат.")
                return {"status": "success", "result": action_node.value, "result_addr": action_node}
                
            elif finished_status == "failed":
                print(f"Действие {action_node.value} завершилось неудачно")
                return {"status": "error", "result": "Action failed", "result_addr": None}
            
            # Если действие еще выполняется, ждем
            elapsed = int(time.time() - start_time)
            print(f"Действие {action_node.value} выполняется... ({elapsed} сек)")
            time.sleep(2)
        
        print(f"Таймаут ожидания результата для действия {action_node.value} ({timeout} сек)")
        return {"status": "timeout", "result": None, "result_addr": None}
        
    except Exception as e:
        print(f"Ошибка ожидания результата агента {action_node.value}: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "result": str(e), "result_addr": None}

def check_action_finished(action_node: ScAddr) -> str:
    """Проверяет статус выполнения действия - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    try:
        from sc_client.client import search_by_template
        from sc_client.models import ScTemplate
        
        # Проверяем finished статус
        action_finished = ScKeynodes.resolve("action_finished_successfully", sc_type.CONST_NODE_ROLE)
        if action_finished and action_finished.is_valid():
            template_finished = ScTemplate()
            template_finished.triple(
                action_finished,
                sc_type.VAR_ARC >> "_arc",
                action_node
            )
            finished_results = search_by_template(template_finished)
            if finished_results:
                print(f"Действие {action_node.value} - статус: finished")
                return "finished"
        
        # Проверяем failed статус  
        action_failed = ScKeynodes.resolve("action_finished_unsuccessfully", sc_type.CONST_NODE_ROLE)
        if action_failed and action_failed.is_valid():
            template_failed = ScTemplate()
            template_failed.triple(
                action_failed,
                sc_type.VAR_ARC >> "_arc",
                action_node
            )
            failed_results = search_by_template(template_failed)
            if failed_results:
                print(f"Действие {action_node.value} - статус: failed")
                return "failed"
        
        print(f"Действие {action_node.value} - статус: running")
        return "running"
        
    except Exception as e:
        print(f"Ошибка проверки статуса действия {action_node.value}: {e}")
        return "unknown"

def _start_agent(agent_identifier: str, argument: ScAddr) -> dict:
    """Запуск одного агента и ожидание результата, возвращает полную информацию"""
    try:
        print(f"Запуск агента {agent_identifier} с аргументом {argument.value if argument else 'None'}")
        action_node = start_agent(agent_identifier, argument)
        if not action_node:
            print(f"Не удалось создать действие для агента {agent_identifier}")
            return {"status": "error", "message": f"Failed to start agent {agent_identifier}"}
            
        print(f"Ожидание результата от агента {agent_identifier}...")
        result = wait_for_agent_result(action_node)
        
        return {
            "status": result["status"],
            "result": result["result"],
            "result_addr": result["result_addr"],
            "action_node": action_node,
            "agent": agent_identifier
        }
            
    except Exception as e:
        print(f"Ошибка в _start_agent для {agent_identifier}: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

def find_link_in_structure(structure_addr: ScAddr):
    """Находит ссылку внутри структуры"""
    try:
        from sc_client.client import search_by_template, get_link_content, get_elements_types
        from sc_client.models import ScTemplate
        
        # Ищем все элементы в структуре
        template = ScTemplate()
        template.triple(
            structure_addr,
            sc_type.VAR_PERM_POS_ARC >> "_arc",
            sc_type.VAR_NODE >> "_element"
        )
        
        results = search_by_template(template)
        
        for result in results:
            element = result.get("_element")
            if element and element.is_valid():
                # Проверяем, является ли элемент ссылкой
                try:
                    element_types = get_elements_types(element)
                    if element_types and element_types[0].is_link():
                        # Пробуем получить содержимое ссылки
                        content_list = get_link_content(element)
                        if content_list and len(content_list) > 0:
                            content_obj = content_list[0]  # Берем первый элемент списка
                            content = content_obj.data  # Получаем данные из ScLinkContent
                            print(f"Найдена ссылка в структуре: {element.value}")
                            print(f"Содержимое ссылки: {content}")
                            try:
                                # Пробуем распарсить JSON
                                return json.loads(content)
                            except json.JSONDecodeError:
                                # Если не JSON, возвращаем как строку
                                return content
                except Exception as e:
                    print(f"Элемент {element.value} не является ссылкой или ошибка получения содержимого: {e}")
                    continue
                    
        return None
        
    except Exception as e:
        print(f"Ошибка поиска ссылки в структуре: {e}")
        return None

def extract_json_from_result(result_addr: ScAddr):
    """Извлекает JSON из результата агента (структуры с линкой)"""
    try:
        from sc_client.client import search_by_template, get_link_content
        from sc_client.models import ScTemplate
        
        if not result_addr or not result_addr.is_valid():
            return None
            
        print(f"Поиск линки в структуре результата {result_addr.value}")
        
        # Ищем линку внутри структуры
        template = ScTemplate()
        template.triple(
            result_addr,
            sc_type.VAR_PERM_POS_ARC >> "_arc",
            sc_type.VAR_NODE >> "_link_element"
        )
        
        results = search_by_template(template)
        
        for result in results:
            link_element = result.get("_link_element")
            if link_element and link_element.is_valid():
                # Проверяем, является ли элемент линкой
                try:
                    content_list = get_link_content(link_element)
                    if content_list and len(content_list) > 0:
                        content_obj = content_list[0]
                        content = content_obj.data
                        print(f"Найдена линка в структуре: {link_element.value}")
                        print(f"Содержимое линки: {content}")
                        
                        try:
                            # Пробуем распарсить JSON
                            return json.loads(content)
                        except json.JSONDecodeError:
                            # Если не JSON, возвращаем как строку
                            return content
                except Exception as e:
                    print(f"Элемент {link_element.value} не является линкой: {e}")
                    continue
                    
        print("Линка не найдена в структуре результата")
        return {
            "node_type": "structure",
            "node_id": result_addr.value,
            "description": "Результат представлен в виде SC-структуры, но линка не найдена"
        }
        
    except Exception as e:
        print(f"Ошибка извлечения JSON из результата: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def trigger_agent_pipeline(construction_data: dict, result_future: Future):
    """Запуск пайплайна агентов для обработки конструкции"""
    try:
        print("=== ЗАПУСК ПАЙПЛАЙНА АГЕНТОВ ===")
        
        # Шаг 1: Отправка конструкции в базу знаний
        print("Шаг 1: Отправка конструкции в SC-память...")
        sc_adapter = SCAdapter()
        success, sc_addrs = sc_adapter.upload_construction(construction_data)
        
        if not success:
            raise Exception("Ошибка загрузки конструкции в SC-памяти")
        
        print(f"Конструкция загружена, создано {len(sc_addrs)} элементов")
        
        # Находим главный узел конструкции
        construction_name = construction_data.get("name", "unnamed")
        main_node = ScKeynodes.resolve(construction_name, sc_type.CONST_NODE_STRUCTURE)
        
        if not main_node or not main_node.is_valid():
            print("Предупреждение: не удалось найти главный узел конструкции, используем первый элемент")
            main_node = sc_addrs[0] if sc_addrs else None
        
        if not main_node:
            raise Exception("Не удалось определить главный узел конструкции")
        
        print(f"Используем главный узел конструкции: {main_node.value}")
        
        # Запускаем цепочку агентов
        print("Запуск цепочки агентов...")
        
        # Агент 1: Поиск геометрических конструкций
        print("=== Шаг 2: Активация GeometrySearchAgent ===")
        first_agent_result = _start_agent("action_search_geometry_constructions", main_node)
        print(f"GeometrySearchAgent результат: {first_agent_result['status']}")
        
        if first_agent_result["status"] != "success":
            raise Exception(f"GeometrySearchAgent завершился с ошибкой: {first_agent_result.get('message', 'Unknown error')}")
            
        # Агент 2: Извлечение последовательности
        print("=== Шаг 3: Активация GeometrySequenceExtractorAgent ===")
        second_agent_result = _start_agent("action_extract_geometry_sequence", first_agent_result["result_addr"])
        print(f"GeometrySequenceExtractorAgent результат: {second_agent_result['status']}")
        
        if second_agent_result["status"] != "success":
            raise Exception(f"GeometrySequenceExtractorAgent завершился с ошибкой: {second_agent_result.get('message', 'Unknown error')}")
            
        # Агент 3: Парсинг последовательности
        print("=== Шаг 4: Активация GeometrySequenceParserAgent ===")
        third_agent_result = _start_agent("action_parse_geometry_sequence", second_agent_result["result_addr"])
        print(f"GeometrySequenceParserAgent результат: {third_agent_result['status']}")
        
        if third_agent_result["status"] != "success":
            raise Exception(f"GeometrySequenceParserAgent завершился с ошибкой: {third_agent_result.get('message', 'Unknown error')}")
        
        print("=== Извлечение финального JSON ===")
        # Извлекаем финальный JSON из результата парсера
        final_json = extract_json_from_result(third_agent_result["result_addr"])
        print(f"Финальный JSON: {final_json}")
        
        # Устанавливаем результат в Future
        result_future.set_result({
            "status": "success",
            "original_construction": construction_data,
            "agents_execution": {
                "search_agent": {
                    "status": first_agent_result["status"],
                    "result_addr": first_agent_result["result_addr"].value if first_agent_result["result_addr"] else None
                },
                "extractor_agent": {
                    "status": second_agent_result["status"],
                    "result_addr": second_agent_result["result_addr"].value if second_agent_result["result_addr"] else None
                },
                "parser_agent": {
                    "status": third_agent_result["status"],
                    "result_addr": third_agent_result["result_addr"].value if third_agent_result["result_addr"] else None
                }
            },
            "parsed_result": final_json,
            "message": "Цепочка агентов успешно завершена"
        })
        
        print("=== ПАЙПЛАЙН УСПЕШНО ЗАВЕРШЕН ===")
        
    except Exception as e:
        print(f"ОШИБКА В ПАЙПЛАЙНЕ: {e}")
        import traceback
        traceback.print_exc()
        result_future.set_exception(e)

# FastAPI приложение
app = FastAPI(title="Geometry Pipeline API", version="1.0.0")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск пайплайна при старте
    print("Запуск пайплайна...")
    await initialize_pipeline()
    yield
    # Остановка при завершении
    print("Остановка пайплайна...")
    for script, process in pipeline_processes.items():
        if process:
            process.terminate()
    # Отключаемся от SC-памяти
    try:
        disconnect()
        print("Отключение от SC-памяти")
    except:
        pass

app = FastAPI(lifespan=lifespan)

@app.post("/upload-construction/")
async def upload_construction_with_pipeline(construction_data: dict):
    """
    Эндпоинт для загрузки конструкции с автоматическим запуском пайплайна агентов
    """
    # Создаем Future для результата
    result_future = Future()
    pipeline_id = f"pipeline_{int(time.time())}"
    
    # Сохраняем Future для отслеживания
    pipeline_results[pipeline_id] = result_future
    
    # Запускаем пайплайн в отдельном потоке
    pipeline_thread = threading.Thread(
        target=trigger_agent_pipeline, 
        args=(construction_data, result_future)
    )
    pipeline_thread.daemon = True
    pipeline_thread.start()
    
    return {
        "status": "processing",
        "pipeline_id": pipeline_id,
        "message": "Конструкция принята в обработку. Пайплайн агентов запущен.",
        "timestamp": time.time()
    }

@app.get("/pipeline-result/{pipeline_id}")
async def get_pipeline_result(pipeline_id: str):
    """
    Получение результата выполнения пайплайна
    """
    if pipeline_id not in pipeline_results:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    future = pipeline_results[pipeline_id]
    
    if future.done():
        if future.exception():
            error_msg = str(future.exception())
            # Удаляем завершенный пайплайн
            del pipeline_results[pipeline_id]
            raise HTTPException(status_code=500, detail=f"Pipeline error: {error_msg}")
        
        result = future.result()
        # Удаляем завершенный пайплайн
        del pipeline_results[pipeline_id]
        
        return {
            "status": "completed",
            "pipeline_id": pipeline_id,
            "result": result
        }
    else:
        return {
            "status": "processing", 
            "pipeline_id": pipeline_id,
            "message": "Pipeline is still processing"
        }

@app.get("/pipeline-status/")
async def get_all_pipelines_status():
    """
    Получение статуса всех пайплайнов
    """
    statuses = {}
    for pid, future in pipeline_results.items():
        if future.done():
            if future.exception():
                statuses[pid] = {"status": "error", "error": str(future.exception())}
            else:
                result = future.result()
                # Возвращаем готовый JSON результат, а не адреса
                statuses[pid] = {
                    "status": "completed", 
                    "result": {
                        "parsed_result": result.get("parsed_result"),
                        "original_construction": result.get("original_construction"),
                        "message": result.get("message")
                    }
                }
        else:
            statuses[pid] = {"status": "processing"}
    
    return {
        "active_pipelines": len(pipeline_results),
        "pipelines": statuses
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья системы"""
    servers_ready = check_servers_ready()
    sc_connected = False
    try:
        from sc_client.client import check_connection
        sc_connected = check_connection()
    except:
        pass
        
    return {
        "status": "healthy" if (servers_ready and sc_connected) else "degraded",
        "servers_ready": servers_ready,
        "sc_connected": sc_connected,
        "active_pipelines": len(pipeline_results)
    }

# Эндпоинт для ручного запуска серверов (на случай проблем)
@app.post("/restart-servers/")
async def restart_servers():
    """Перезапуск серверов пайплайна"""
    global pipeline_processes
    
    # Останавливаем текущие процессы
    for script, process in pipeline_processes.items():
        if process:
            process.terminate()
    
    pipeline_processes = {}
    
    # Перезапускаем
    await initialize_pipeline()
    
    return {"status": "success", "message": "Servers restarted"}

if __name__ == "__main__":
    # Запуск FastAPI сервера
    uvicorn.run(
        "pipeline_runner:app",
        host="0.0.0.0", 
        port=8001,
        reload=True
    )