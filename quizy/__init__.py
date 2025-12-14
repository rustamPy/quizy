"""
Quizy - A professional Python quiz framework
Version 0.3.0 - Enhanced with async support, live timers, and interactivity
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

__version__ = "0.5.1"
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
    "quiz_101",
    "quiz_102",
]
