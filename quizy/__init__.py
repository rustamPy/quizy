"""
Quiz - A simple Python quiz framework
"""

from .core import Quiz, Question
from .quiz_102 import quiz_102
from .quiz_101 import quiz_101

__version__ = "0.1.4"
__all__ = ["Quiz", "Question", "quiz_102", "quiz_101"]