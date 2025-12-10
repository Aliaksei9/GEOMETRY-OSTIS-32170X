from fastapi import FastAPI
from services.endpoints import upload_construction
from contextlib import asynccontextmanager
import subprocess
import sys

# Описание для Swagger
description = """
Geometry Construction API помогает вам работать с геометрическими конструкциями.

## Фигуры

Вы можете создавать:
* **Полигоны** (треугольники, четырехугольники и т.д.)
* **Окружности** 
* **Конструкционные элементы**
* **Сложные конструкции** с отношениями между фигурами

## Валидация

API автоматически проверяет:
* Корректность вершин и ребер
* Уникальность имен точек
* Положительные длины
* Соответствие типов фигур
"""

tags_metadata = [
    {
        "name": "constructions",
        "description": "Операции с геометрическими конструкциями",
    },
    {
        "name": "validation", 
        "description": "Валидация геометрических данных",
    }
]

server_process = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Geometry Construction API started")
    global server_process
    server_process = subprocess.Popen([sys.executable, "server.py"])
    yield
    if server_process:
        server_process.terminate()
        server_process.wait()

    print("Geometry Construction API stopped")

app = FastAPI(
    title="Geometry Construction API",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "API Support",
        "email": "support@geometry.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Регистрируем endpoints
app.post("/upload-construction/", 
         tags=["constructions"],
         summary="Загрузка геометрической конструкции",
         response_description="Результат обработки конструкции")(upload_construction)

@app.get("/", tags=["validation"])
async def root():
    return {"message": "Geometry Construction API", "status": "active"}
