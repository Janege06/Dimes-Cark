import json
import random
from enum import Enum
from typing import TypedDict, cast, Optional


class Category(Enum):
    SURDURULEBILIRLIK = "s"
    URUNLER = "u"
    GENEL_KULTUR = "g"
    BONUS = "b"


class Question(TypedDict):
    q: str
    opts: list[str]
    ans: int


class QuestionManager:
    questions = dict[str, list[Question]]

    def __init__(self):
        with open('questions.json', 'r', encoding='utf-8') as file:
            self.questions = cast(dict[str, list[Question]], json.load(file))

    def get_questions(self, subject: Category) -> list[Question]:
        if subject == Category.BONUS:
            return (
                    self.questions.get(Category.SURDURULEBILIRLIK.value, []) +
                    self.questions.get(Category.URUNLER.value, []) +
                    self.questions.get(Category.GENEL_KULTUR.value, [])
            )
        return self.questions.get(subject.value, [])

    def get_random_question(self, subject: Category, used_indices: list[int]) -> tuple[Optional[Question], int]:
        pool = self.get_questions(subject)
        if not pool:
            return None, -1

        # Filter out already answered questions
        available_indices = [i for i in range(len(pool)) if i not in used_indices]
        
        # If all questions in pool have been answered, reset (pick from full pool)
        if not available_indices:
            available_indices = list(range(len(pool)))

        idx = random.choice(available_indices)
        return pool[idx], idx
