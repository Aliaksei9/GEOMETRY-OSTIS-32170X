#!/usr/bin/env python3
"""
API server using FastAPI that generates geometry tests using Grock LLM
"Receives POST requests with {"message": "user input"}, processes with Groq LLM"
Run with: uvicorn this_file:app --reload
Requires: pip install fastapi uvicorn groq
"""
import os
import json
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from fastapi.middleware.cors import CORSMiddleware

"""
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent / ".env")
"""

MODEL = "openai/gpt-oss-20b"
SYSTEM_PROMT = """
        Ты - эксперт по созданию образовательных тестов по геометрии. 

        ТРЕБОВАНИЯ:
        1. Создавай УНИКАЛЬНЫЕ вопросы, не перефразированные
        2. 4 варианта ответа (1 правильный, 3 правдоподобных неправильных)
        3. Правильный ответ должен быть точным
        4. Формат вывода - ТОЛЬКО JSON

        ФОРМАТ JSON:
        {
          "test_title": "Название",
          "questions": [
            {
              "question_text": "Текст вопроса",
              "options": ["A", "B", "C", "D"],
              "correct_index": 0
            }
          ]
        }
        """
TEMPERATURE = 0.7
MAX_TOKENS = 4000


class Question:
    def __init__(self, question_text: str, options: List[str], correct_index: int):
        self.question_text = question_text
        self.options = options
        self.correct_index = correct_index
    
    def to_dict(self) -> Dict:
        """Для удобной сериализации в JSON"""
        return {
            "question_text": self.question_text,
            "options": self.options,
            "correct_index": self.correct_index
        }

class Test:
    def __init__(self, title: str, questions: List[Question], topic: str):
        self.title = title
        self.questions = questions
        self.topic = topic
    
    def to_dict(self) -> Dict:
        """Для использования в любом интерфейсе"""
        return {
            "title": self.title,
            "questions": [q.to_dict() for q in self.questions]
        }

class TestGenerator:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = MODEL
    
    def generate_test(self, topic: str, num_questions: int = 10) -> Test:
        system_prompt = SYSTEM_PROMT
        
        user_prompt = f"""
        Тема теста: {topic}
        Количество вопросов: {num_questions}
        
        Создай разнообразные вопросы по этой теме. Вопросы должны охватывать разные аспекты темы.
        Убедись, что вопросы действительно разные, а не просто перефразированы.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            response_text = response.choices[0].message.content
            test_data = json.loads(response_text)
            
            # Преобразуем в объекты
            questions = []
            for q_data in test_data["questions"]:
                question = Question(
                    question_text=q_data["question_text"],
                    options=q_data["options"],
                    correct_index=q_data["correct_index"]
                )
                questions.append(question)
            
            return Test(
                title=test_data["test_title"],
                questions=questions,
                topic=topic
            )
            
        except Exception as e:
            print(f"Ошибка при генерации теста: {e}")
            return None

def get_api_key():
    """Читает API ключ из переменной окружения или из файла keys.txt"""

    env_key = os.environ.get("GROQ_API_KEY")
    if env_key:
        return env_key
    
    try:
        with open('keys.txt', 'r') as f:
            content = f.read().strip()
            
        # Если файл в формате "GROQ_API_KEY=ключ"
        if '=' in content:
            for line in content.split('\n'):
                if line.startswith('GROQ_API_KEY='):
                    return line.split('=', 1)[1].strip()
        
        # Если файл содержит просто ключ
        return content
    except FileNotFoundError:
        print("Файл 'keys' не найден!")
        return None

# --- FastAPI приложение ---
app = FastAPI()

# CORS настройки (аналогично коду друга)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TestRequest(BaseModel):
    topic: str
    num_questions: int

@app.post("/generate-test")
async def generate_test_endpoint(req: TestRequest):
    api_key = get_api_key()
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not found")
    
    generator = TestGenerator(api_key)
    test = generator.generate_test(req.topic, req.num_questions)
    
    if test:
        return test.to_dict()
    else:
        raise HTTPException(status_code=500, detail="Failed to generate test")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)