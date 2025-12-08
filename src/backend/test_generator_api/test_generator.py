from typing import List

import json
from groq import Groq

from .test import Test
from .question import Question

from .config import (
    DEFAULT_MODEL, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE
)
from .prompt import DEFAULT_SYSTEM_PROMPT, DEFAULT_USER_PROMPT

MODEL = DEFAULT_MODEL
MAX_TOKENS = DEFAULT_MAX_TOKENS
TEMPERATURE = DEFAULT_TEMPERATURE

SYSTEM_PROMT = DEFAULT_SYSTEM_PROMPT
USER_PROMPT = DEFAULT_USER_PROMPT

class TestGenerator:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = MODEL
    

    def question_parser(self, test_data) -> List[Question]:
        questions = []
        for q_data in test_data["questions"]:
            question = Question(
                question_text=q_data["question_text"],
                options=q_data["options"],
                correct_index=q_data["correct_index"]
            )
            questions.append(question)

        return questions

    def generate_test(self, topic: str, num_questions: int = 10) -> Test:
        system_prompt = SYSTEM_PROMT
        
        user_prompt = USER_PROMPT(topic, num_questions)
        
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
            
            questions = self.question_parser(test_data)
            
            return Test(
                title=test_data["test_title"],
                questions=questions,
                topic=topic
            )
            
        except Exception as e:
            print(f"Ошибка при генерации теста: {e}")
            return None