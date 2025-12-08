from typing import List, Dict
from .question import Question

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