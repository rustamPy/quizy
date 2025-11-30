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
from .quiz_101 import quiz_101
from .quiz_102 import quiz_102

__version__ = "0.3.2"
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
