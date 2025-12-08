from typing import List, Dict

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