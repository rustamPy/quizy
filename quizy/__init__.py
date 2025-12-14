f"""
Quizy - A professional Python quiz framework
"""

from .core import (
    Quiz,
    Question,
    QuestionType,
    MultipleChoiceQuestion,
    MultipleSelectQuestion,
    ShortTextQuestion,
    TrueFalseQuestion,
    MatchingQuestion,
    QuizResult,
    QuestionResult,
    ResultStatus,
)
from .cli import QuizCLI, TimerDisplay

__version__ = "0.4.8"
__all__ = [
    "Quiz",
    "Question",
    "QuestionType",
    "MultipleChoiceQuestion",
    "MultipleSelectQuestion",
    "ShortTextQuestion",
    "TrueFalseQuestion",
    "MatchingQuestion",
    "QuizResult",
    "QuestionResult",
    "ResultStatus",
    "QuizCLI",
    "TimerDisplay",
]
