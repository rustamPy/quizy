"""
Core quizy functionality - Professional API for building quiz applications
"""

import time
from enum import Enum
from typing import List, Optional, Callable, Dict, Any, Tuple
from dataclasses import dataclass, field


class ResultStatus(Enum):
    """Status of a quiz result"""

    CORRECT = "correct"
    INCORRECT = "incorrect"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


@dataclass
class QuestionResult:
    """Result of answering a single question"""

    question_index: int
    user_answer: str
    correct_answer: str
    status: ResultStatus
    time_taken: float

    @property
    def is_correct(self) -> bool:
        """Check if answer was correct"""
        return self.status == ResultStatus.CORRECT


@dataclass
class QuizResult:
    """Complete quiz result"""

    title: str
    total_questions: int
    correct_answers: int
    time_taken: float
    question_results: List[QuestionResult] = field(default_factory=list)

    @property
    def score_percentage(self) -> float:
        """Get score as percentage"""
        if self.total_questions == 0:
            return 0.0
        return (self.correct_answers / self.total_questions) * 100

    @property
    def skipped_count(self) -> int:
        """Count skipped questions"""
        return sum(1 for r in self.question_results if r.status == ResultStatus.SKIPPED)

    @property
    def timeout_count(self) -> int:
        """Count timeout questions"""
        return sum(1 for r in self.question_results if r.status == ResultStatus.TIMEOUT)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "title": self.title,
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "score_percentage": self.score_percentage,
            "time_taken": self.time_taken,
            "skipped_count": self.skipped_count,
            "timeout_count": self.timeout_count,
            "question_results": [
                {
                    "question_index": r.question_index,
                    "user_answer": r.user_answer,
                    "correct_answer": r.correct_answer,
                    "status": r.status.value,
                    "time_taken": r.time_taken,
                }
                for r in self.question_results
            ],
        }


class QuestionType(Enum):
    """Types of questions supported"""

    MULTIPLE_CHOICE = "multiple_choice"  # Single answer from options
    SINGLE_ANSWER = "single_answer"  # Alias for MULTIPLE_CHOICE
    MULTIPLE_SELECT = "multiple_select"  # Multiple correct answers
    SHORT_TEXT = "short_text"  # Free-form text input
    MATCHING = "matching"  # Match items to pairs
    TRUE_FALSE = "true_false"  # True/False question


class Question:
    """Base class for quiz questions"""

    def __init__(
        self,
        text: str,
        correct_answer: Any,
        explanation: Optional[str] = None,
        time_limit: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        question_type: QuestionType = QuestionType.MULTIPLE_CHOICE,
    ):
        """
        Base question constructor

        Args:
            text: The question text
            correct_answer: The correct answer(s)
            explanation: Optional explanation for the answer
            time_limit: Optional time limit in seconds for this question
            metadata: Optional metadata dictionary for custom data
            question_type: Type of question
        """
        self.text = text
        self.correct_answer = correct_answer
        self.explanation = explanation
        self.time_limit = time_limit
        self.metadata = metadata or {}
        self.question_type = question_type

    def check_answer(self, user_answer: Any) -> bool:
        """
        Check if the user's answer is correct

        Args:
            user_answer: The user's answer

        Returns:
            True if correct, False otherwise
        """
        raise NotImplementedError("Subclasses must implement check_answer()")

    def get_options(self) -> Optional[List[str]]:
        """Get options if applicable"""
        return None

    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """Validate question configuration"""
        if not self.text:
            return False, "Question text is required"
        return True, None


class MultipleChoiceQuestion(Question):
    """Single-answer multiple choice question"""

    def __init__(
        self,
        text: str,
        options: List[str],
        correct_answer: str,
        explanation: Optional[str] = None,
        time_limit: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            text: The question text
            options: List of possible answers
            correct_answer: The correct answer (must be in options)
            explanation: Optional explanation for the answer
            time_limit: Optional time limit in seconds for this question
            metadata: Optional metadata dictionary for custom data

        Raises:
            ValueError: If correct_answer is not in options
        """
        if correct_answer not in options:
            raise ValueError("Correct answer must be one of the options")

        super().__init__(
            text=text,
            correct_answer=correct_answer,
            explanation=explanation,
            time_limit=time_limit,
            metadata=metadata,
            question_type=QuestionType.MULTIPLE_CHOICE,
        )
        self.options = options

    def check_answer(self, user_answer: str) -> bool:
        """Check if answer matches exactly"""
        return user_answer == self.correct_answer

    def get_options(self) -> List[str]:
        """Get all options for this question"""
        return self.options

    def get_option_by_index(self, index: int) -> Optional[str]:
        """Get option by 1-based index"""
        if 1 <= index <= len(self.options):
            return self.options[index - 1]
        return None

    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """Validate question configuration"""
        is_valid, error = super().validate_config()
        if not is_valid:
            return False, error

        if not self.options or len(self.options) < 2:
            return False, "Must have at least 2 options"

        return True, None


class MultipleSelectQuestion(Question):
    """Multiple-answer question where user must select all correct answers"""

    def __init__(
        self,
        text: str,
        options: List[str],
        correct_answers: List[str],
        explanation: Optional[str] = None,
        time_limit: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            text: The question text
            options: List of possible answers
            correct_answers: List of correct answers (all must be in options)
            explanation: Optional explanation for the answer
            time_limit: Optional time limit in seconds for this question
            metadata: Optional metadata dictionary for custom data

        Raises:
            ValueError: If any correct answer is not in options
        """
        for answer in correct_answers:
            if answer not in options:
                raise ValueError(f"Answer '{answer}' must be one of the options")

        if len(correct_answers) < 2:
            raise ValueError("Multiple select must have at least 2 correct answers")

        super().__init__(
            text=text,
            correct_answer=correct_answers,
            explanation=explanation,
            time_limit=time_limit,
            metadata=metadata,
            question_type=QuestionType.MULTIPLE_SELECT,
        )
        self.options = options

    def check_answer(self, user_answer: List[str]) -> bool:
        """Check if all correct answers are selected and no incorrect ones"""
        if not isinstance(user_answer, list):
            return False
        return set(user_answer) == set(self.correct_answer)

    def get_options(self) -> List[str]:
        """Get all options"""
        return self.options

    def validate_config(self) -> Tuple[bool, Optional[str]]:
        """Validate question configuration"""
        is_valid, error = super().validate_config()
        if not is_valid:
            return False, error

        if not self.options or len(self.options) < 2:
            return False, "Must have at least 2 options"

        return True, None


class ShortTextQuestion(Question):
    """Free-form text input question with optional case sensitivity"""

    def __init__(
        self,
        text: str,
        correct_answer: str,
        explanation: Optional[str] = None,
        time_limit: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        case_sensitive: bool = False,
        accepted_variations: Optional[List[str]] = None,
    ):
        """
        Args:
            text: The question text
            correct_answer: The correct answer
            explanation: Optional explanation for the answer
            time_limit: Optional time limit in seconds for this question
            metadata: Optional metadata dictionary for custom data
            case_sensitive: Whether comparison is case-sensitive
            accepted_variations: Alternative accepted answers
        """
        super().__init__(
            text=text,
            correct_answer=correct_answer,
            explanation=explanation,
            time_limit=time_limit,
            metadata=metadata,
            question_type=QuestionType.SHORT_TEXT,
        )
        self.case_sensitive = case_sensitive
        self.accepted_variations = accepted_variations or []

    def check_answer(self, user_answer: str) -> bool:
        """Check if answer matches (with case sensitivity option)"""
        user_text = user_answer.strip()

        # Normalize based on case sensitivity
        if not self.case_sensitive:
            user_text = user_text.lower()
            correct = self.correct_answer.lower()
        else:
            correct = self.correct_answer

        if user_text == correct:
            return True

        # Check accepted variations
        for variation in self.accepted_variations:
            compare_variation = (
                variation.lower() if not self.case_sensitive else variation
            )
            if user_text == compare_variation:
                return True

        return False


class TrueFalseQuestion(Question):
    """True/False question"""

    def __init__(
        self,
        text: str,
        correct_answer: bool,
        explanation: Optional[str] = None,
        time_limit: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            text: The question text
            correct_answer: True or False
            explanation: Optional explanation for the answer
            time_limit: Optional time limit in seconds for this question
            metadata: Optional metadata dictionary for custom data
        """
        if not isinstance(correct_answer, bool):
            raise ValueError("Correct answer must be a boolean")

        super().__init__(
            text=text,
            correct_answer=correct_answer,
            explanation=explanation,
            time_limit=time_limit,
            metadata=metadata,
            question_type=QuestionType.TRUE_FALSE,
        )

    def check_answer(self, user_answer: Any) -> bool:
        """Check if answer is correct"""
        # Accept boolean, string variations, or numeric representations
        if isinstance(user_answer, bool):
            return user_answer == self.correct_answer

        if isinstance(user_answer, str):
            normalized = user_answer.strip().lower()
            if self.correct_answer:
                return normalized in ("true", "t", "yes", "y", "1")
            else:
                return normalized in ("false", "f", "no", "n", "0")

        if isinstance(user_answer, (int, float)):
            if self.correct_answer:
                return user_answer != 0
            else:
                return user_answer == 0

        return False


class MatchingQuestion(Question):
    """Matching question where items must be matched to their pairs"""

    def __init__(
        self,
        text: str,
        pairs: Dict[str, str],
        explanation: Optional[str] = None,
        time_limit: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            text: The question text
            pairs: Dictionary of {prompt: answer} pairs to match
            explanation: Optional explanation for the answer
            time_limit: Optional time limit in seconds for this question
            metadata: Optional metadata dictionary for custom data
        """
        if not pairs or len(pairs) < 2:
            raise ValueError("Must have at least 2 pairs to match")

        super().__init__(
            text=text,
            correct_answer=pairs,
            explanation=explanation,
            time_limit=time_limit,
            metadata=metadata,
            question_type=QuestionType.MATCHING,
        )
        self.pairs = pairs
        self.prompts = list(pairs.keys())
        self.answers = list(pairs.values())

    def check_answer(self, user_answer: Dict[str, str]) -> bool:
        """Check if all matches are correct"""
        if not isinstance(user_answer, dict):
            return False
        return user_answer == self.pairs

    def get_options(self) -> Dict[str, List[str]]:
        """Get prompts and answers separately for display"""
        return {"prompts": self.prompts, "answers": self.answers}


class Quiz:
    """A quiz containing multiple questions with configurable behavior"""

    def __init__(
        self,
        title: str,
        questions: Optional[List[Question]] = None,
        time_limit: Optional[float] = None,
        allow_skip: bool = False,
        shuffle_options: bool = False,
        randomize_order: bool = False,
    ):
        """
        Args:
            title: Quiz title
            questions: List of Question objects
            time_limit: Optional total time limit for quiz in seconds
            allow_skip: Allow users to skip questions
            shuffle_options: Shuffle answer options for each question
            randomize_order: Randomize question order
        """
        self.title = title
        self.questions = questions or []
        self.time_limit = time_limit
        self.allow_skip = allow_skip
        self.shuffle_options = shuffle_options
        self.randomize_order = randomize_order
        self._result: Optional[QuizResult] = None

    def add_question(self, question: Question) -> None:
        """
        Add a question to the quiz

        Args:
            question: Question instance to add

        Raises:
            TypeError: If question is not a Question instance
        """
        if not isinstance(question, Question):
            raise TypeError("Must be a Question instance")
        self.questions.append(question)

    def add_questions(self, questions: List[Question]) -> None:
        """
        Add multiple questions at once

        Args:
            questions: List of Question instances
        """
        for q in questions:
            self.add_question(q)

    def remove_question(self, index: int) -> None:
        """Remove a question by index"""
        if 0 <= index < len(self.questions):
            self.questions.pop(index)

    def get_questions(self) -> List[Question]:
        """Get all questions"""
        return self.questions

    def get_question_count(self) -> int:
        """Get total number of questions"""
        return len(self.questions)

    def get_result(self) -> Optional[QuizResult]:
        """Get the last quiz result"""
        return self._result

    def clear(self) -> None:
        """Clear all questions and results"""
        self.questions = []
        self._result = None

    def execute(
        self,
        answer_provider: Callable,
        result_callback: Optional[Callable] = None,
        question_callback: Optional[Callable] = None,
    ) -> QuizResult:
        """
        Execute the quiz with custom answer provider

        Args:
            answer_provider: Callable that takes (question, question_index) and returns answer or None
            result_callback: Optional callback called after each question with results
            question_callback: Optional callback called before each question

        Returns:
            QuizResult object with complete quiz statistics

        Raises:
            ValueError: If no questions in quiz
        """
        if not self.questions:
            raise ValueError("No questions in quiz")

        start_time = time.time()
        results = []
        correct_count = 0

        for i, question in enumerate(self.questions, 1):
            if question_callback:
                question_callback(question, i, len(self.questions))

            question_start = time.time()
            user_answer = answer_provider(question, i - 1)
            time_taken = time.time() - question_start

            if user_answer is None:
                status = (
                    ResultStatus.SKIPPED if self.allow_skip else ResultStatus.SKIPPED
                )
            elif question.check_answer(user_answer):
                status = ResultStatus.CORRECT
                correct_count += 1
            else:
                status = ResultStatus.INCORRECT

            result = QuestionResult(
                question_index=i - 1,
                user_answer=user_answer or "",
                correct_answer=question.correct_answer,
                status=status,
                time_taken=time_taken,
            )
            results.append(result)

            if result_callback:
                result_callback(question, i, user_answer or "", status, time_taken)

        total_time = time.time() - start_time

        quiz_result = QuizResult(
            title=self.title,
            total_questions=len(self.questions),
            correct_answers=correct_count,
            time_taken=total_time,
            question_results=results,
        )

        self._result = quiz_result
        return quiz_result

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate quiz configuration

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not self.title:
            errors.append("Quiz title is required")

        if not self.questions:
            errors.append("Quiz must have at least one question")

        for i, q in enumerate(self.questions):
            is_valid, error = q.validate_config()
            if not is_valid:
                errors.append(f"Question {i+1}: {error}")

        return len(errors) == 0, errors
