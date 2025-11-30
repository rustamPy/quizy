"""
Core quizy functionality - Professional API with async support and enhanced features
Improvements:
- Async/await support for non-blocking quiz execution
- Live timer management with countdown tracking
- Enhanced MatchingQuestion with shuffling options
- Better time tracking and timeout handling
- Partial credit support for some question types
"""

import asyncio
import time
import random
from enum import Enum
from typing import List, Optional, Callable, Dict, Any, Tuple, Union, Coroutine
from dataclasses import dataclass, field


class ResultStatus(Enum):
    """Status of a quiz result"""

    CORRECT = "correct"
    INCORRECT = "incorrect"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"
    PARTIAL = "partial"  # New: for partial credit


@dataclass
class QuestionResult:
    """Result of answering a single question"""

    question_index: int
    user_answer: Any
    correct_answer: Any
    status: ResultStatus
    time_taken: float
    score: float = 1.0  # New: support partial credit (0.0 to 1.0)

    @property
    def is_correct(self) -> bool:
        """Check if answer was correct"""
        return self.status == ResultStatus.CORRECT

    @property
    def is_partial(self) -> bool:
        """Check if answer was partially correct"""
        return self.status == ResultStatus.PARTIAL

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "question_index": self.question_index,
            "user_answer": str(self.user_answer),
            "correct_answer": str(self.correct_answer),
            "status": self.status.value,
            "time_taken": self.time_taken,
            "score": self.score,
        }


@dataclass
class QuizResult:
    """Complete quiz result with enhanced metrics"""

    title: str
    total_questions: int
    correct_answers: int
    time_taken: float
    question_results: List[QuestionResult] = field(default_factory=list)
    partial_answers: int = 0

    @property
    def score_percentage(self) -> float:
        """Get score as percentage (including partial credit)"""
        if self.total_questions == 0:
            return 0.0
        total_score = sum(r.score for r in self.question_results)
        return (total_score / self.total_questions) * 100

    @property
    def skipped_count(self) -> int:
        """Count skipped questions"""
        return sum(1 for r in self.question_results if r.status == ResultStatus.SKIPPED)

    @property
    def timeout_count(self) -> int:
        """Count timeout questions"""
        return sum(1 for r in self.question_results if r.status == ResultStatus.TIMEOUT)

    @property
    def average_time_per_question(self) -> float:
        """Calculate average time spent per question"""
        if self.total_questions == 0:
            return 0.0
        return self.time_taken / self.total_questions

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "title": self.title,
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "partial_answers": self.partial_answers,
            "score_percentage": self.score_percentage,
            "time_taken": self.time_taken,
            "average_time_per_question": self.average_time_per_question,
            "skipped_count": self.skipped_count,
            "timeout_count": self.timeout_count,
            "question_results": [r.to_dict() for r in self.question_results],
        }


class QuestionType(Enum):
    """Types of questions supported"""

    MULTIPLE_CHOICE = "multiple_choice"
    MULTIPLE_SELECT = "multiple_select"
    SHORT_TEXT = "short_text"
    MATCHING = "matching"
    TRUE_FALSE = "true_false"


class Question:
    """Base class for quiz questions with enhanced features"""

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

    def check_answer(self, user_answer: Any) -> Union[bool, float]:
        """
        Check if the user's answer is correct

        Args:
            user_answer: The user's answer

        Returns:
            True if correct, False if incorrect, or float (0.0-1.0) for partial credit
        """
        raise NotImplementedError("Subclasses must implement check_answer()")

    def get_options(self) -> Optional[Any]:
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
        shuffle_options: bool = False,
    ):
        """
        Args:
            text: The question text
            options: List of possible answers
            correct_answer: The correct answer (must be in options)
            explanation: Optional explanation for the answer
            time_limit: Optional time limit in seconds
            metadata: Optional metadata dictionary
            shuffle_options: Whether to shuffle options for display
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
        self.shuffle_options = shuffle_options
        self._shuffled_options = None

    @property
    def display_options(self) -> List[str]:
        """Get options, shuffled if configured"""
        if self.shuffle_options and self._shuffled_options is None:
            self._shuffled_options = self.options.copy()
            random.shuffle(self._shuffled_options)
        return self._shuffled_options if self._shuffled_options else self.options

    def check_answer(self, user_answer: str) -> bool:
        """Check if answer matches exactly"""
        return user_answer == self.correct_answer

    def get_option_by_index(self, index: int) -> Optional[str]:
        """Get option by 1-based index"""
        if 1 <= index <= len(self.options):
            return self.options[index - 1]
        return None

    def get_options(self) -> List[str]:
        """Get all options for this question"""
        return self.options

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
        allow_partial_credit: bool = False,
        shuffle_options: bool = False,
    ):
        """
        Args:
            text: The question text
            options: List of possible answers
            correct_answers: List of correct answers
            explanation: Optional explanation
            time_limit: Optional time limit
            metadata: Optional metadata
            allow_partial_credit: Award points for partially correct answers
            shuffle_options: Whether to shuffle options
        """
        for answer in correct_answers:
            if answer not in options:
                raise ValueError(f"Answer '{answer}' must be in options")

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
        self.allow_partial_credit = allow_partial_credit
        self.shuffle_options = shuffle_options
        self._shuffled_options = None

    @property
    def display_options(self) -> List[str]:
        """Get options, shuffled if configured"""
        if self.shuffle_options and self._shuffled_options is None:
            self._shuffled_options = self.options.copy()
            random.shuffle(self._shuffled_options)
        return self._shuffled_options if self._shuffled_options else self.options

    def check_answer(self, user_answer: List[str]) -> Union[bool, float]:
        """Check if answers are correct, with optional partial credit"""
        if not isinstance(user_answer, list):
            return False

        if set(user_answer) == set(self.correct_answer):
            return True

        if not self.allow_partial_credit:
            return False

        # Calculate partial credit
        correct_selected = len(set(user_answer) & set(self.correct_answer))
        incorrect_selected = len(set(user_answer) - set(self.correct_answer))
        missed = len(set(self.correct_answer) - set(user_answer))

        if incorrect_selected > 0:
            return 0.0  # Any wrong selection = no credit

        if missed > 0:
            return correct_selected / len(self.correct_answer)

        return True

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
    """Free-form text input question with case sensitivity option"""

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
            explanation: Optional explanation
            time_limit: Optional time limit
            metadata: Optional metadata
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
        """Check if answer matches"""
        user_text = user_answer.strip()

        if not self.case_sensitive:
            user_text = user_text.lower()
            correct = self.correct_answer.lower()
        else:
            correct = self.correct_answer

        if user_text == correct:
            return True

        for variation in self.accepted_variations:
            compare_variation = variation.lower() if not self.case_sensitive else variation
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
            explanation: Optional explanation
            time_limit: Optional time limit
            metadata: Optional metadata
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
        if isinstance(user_answer, bool):
            return user_answer == self.correct_answer

        if isinstance(user_answer, str):
            normalized = user_answer.strip().lower()
            if self.correct_answer:
                return normalized in ("true", "t", "yes", "y", "1")
            else:
                return normalized in ("false", "f", "no", "n", "0")

        if isinstance(user_answer, (int, float)):
            return (user_answer != 0) == self.correct_answer

        return False


class MatchingQuestion(Question):
    """Enhanced matching question with shuffling and partial credit"""

    def __init__(
        self,
        text: str,
        pairs: Dict[str, str],
        explanation: Optional[str] = None,
        time_limit: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        shuffle_answers: bool = True,
        allow_partial_credit: bool = False,
    ):
        """
        Args:
            text: The question text
            pairs: Dictionary of {prompt: answer} pairs to match
            explanation: Optional explanation
            time_limit: Optional time limit
            metadata: Optional metadata
            shuffle_answers: Shuffle the answer options (default: True)
            allow_partial_credit: Award partial credit for partial matches (default: False)
        """
        if not pairs or len(pairs) < 2:
            raise ValueError("Must have at least 2 pairs")

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
        self.shuffle_answers = shuffle_answers
        self.allow_partial_credit = allow_partial_credit
        self._shuffled_answers = None

    @property
    def display_answers(self) -> List[str]:
        """Get answers, shuffled if configured"""
        if self.shuffle_answers and self._shuffled_answers is None:
            self._shuffled_answers = self.answers.copy()
            random.shuffle(self._shuffled_answers)
        return self._shuffled_answers if self._shuffled_answers else self.answers

    def check_answer(self, user_answer: Dict[str, str]) -> Union[bool, float]:
        """Check matches, with optional partial credit"""
        if not isinstance(user_answer, dict):
            return False

        if user_answer == self.pairs:
            return True

        if not self.allow_partial_credit:
            return False

        # Calculate partial credit
        correct_matches = sum(1 for k, v in user_answer.items() if self.pairs.get(k) == v)
        return correct_matches / len(self.pairs)

    def get_options(self) -> Dict[str, List[str]]:
        """Get prompts and answers"""
        return {"prompts": self.prompts, "answers": self.display_answers}


class Quiz:
    """Enhanced Quiz with async support and live timer management"""

    def __init__(
        self,
        title: str,
        questions: Optional[List[Question]] = None,
        time_limit: Optional[float] = None,
        allow_skip: bool = False,
        shuffle_options: bool = False,
        randomize_order: bool = False,
        show_progress: bool = True,
    ):
        """
        Args:
            title: Quiz title
            questions: List of Question objects
            time_limit: Optional total time limit for quiz in seconds
            allow_skip: Allow users to skip questions
            shuffle_options: Shuffle answer options for each question
            randomize_order: Randomize question order
            show_progress: Show progress indicator during quiz
        """
        self.title = title
        self.questions = questions or []
        self.time_limit = time_limit
        self.allow_skip = allow_skip
        self.shuffle_options = shuffle_options
        self.randomize_order = randomize_order
        self.show_progress = show_progress
        self._result: Optional[QuizResult] = None
        self._start_time: Optional[float] = None

    def add_question(self, question: Question) -> None:
        """Add a question to the quiz"""
        if not isinstance(question, Question):
            raise TypeError("Must be a Question instance")
        self.questions.append(question)

    def add_questions(self, questions: List[Question]) -> None:
        """Add multiple questions at once"""
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

    def get_remaining_time(self) -> Optional[float]:
        """Get remaining time for quiz"""
        if self.time_limit is None or self._start_time is None:
            return None
        elapsed = time.time() - self._start_time
        return max(0.0, self.time_limit - elapsed)

    def is_time_up(self) -> bool:
        """Check if quiz time limit exceeded"""
        remaining = self.get_remaining_time()
        return remaining is not None and remaining <= 0

    def clear(self) -> None:
        """Clear all questions and results"""
        self.questions = []
        self._result = None

    def execute(
        self,
        answer_provider: Callable,
        result_callback: Optional[Callable] = None,
        question_callback: Optional[Callable] = None,
        timeout_callback: Optional[Callable] = None,
    ) -> QuizResult:
        """
        Execute the quiz synchronously

        Args:
            answer_provider: Callable(question, index) -> answer or None
            result_callback: Optional callback after each question
            question_callback: Optional callback before each question
            timeout_callback: Optional callback when time expires

        Returns:
            QuizResult with complete statistics
        """
        if not self.questions:
            raise ValueError("No questions in quiz")

        self._start_time = time.time()
        results = []
        correct_count = 0
        partial_count = 0

        questions_to_run = self.questions.copy()
        if self.randomize_order:
            random.shuffle(questions_to_run)

        for i, question in enumerate(questions_to_run, 1):
            # Check time limit
            if self.is_time_up():
                if timeout_callback:
                    timeout_callback(question, i, len(questions_to_run))
                remaining_questions = len(questions_to_run) - i
                for j in range(remaining_questions):
                    results.append(
                        QuestionResult(
                            question_index=i + j - 1,
                            user_answer="",
                            correct_answer=question.correct_answer,
                            status=ResultStatus.TIMEOUT,
                            time_taken=0.0,
                            score=0.0,
                        )
                    )
                break

            if question_callback:
                question_callback(question, i, len(questions_to_run))

            question_start = time.time()
            user_answer = answer_provider(question, i - 1)
            time_taken = time.time() - question_start

            # Determine status and score
            if user_answer is None:
                status = ResultStatus.SKIPPED
                score = 0.0
            else:
                check_result = question.check_answer(user_answer)
                if isinstance(check_result, bool):
                    status = ResultStatus.CORRECT if check_result else ResultStatus.INCORRECT
                    score = 1.0 if check_result else 0.0
                    if check_result:
                        correct_count += 1
                else:
                    # Partial credit
                    status = ResultStatus.PARTIAL if check_result > 0 else ResultStatus.INCORRECT
                    score = check_result
                    if check_result > 0:
                        partial_count += 1

            result = QuestionResult(
                question_index=i - 1,
                user_answer=user_answer or "",
                correct_answer=question.correct_answer,
                status=status,
                time_taken=time_taken,
                score=score,
            )
            results.append(result)

            if result_callback:
                result_callback(question, i, user_answer or "", status, time_taken)

        total_time = time.time() - self._start_time

        quiz_result = QuizResult(
            title=self.title,
            total_questions=len(questions_to_run),
            correct_answers=correct_count,
            time_taken=total_time,
            question_results=results,
            partial_answers=partial_count,
        )

        self._result = quiz_result
        return quiz_result

    async def execute_async(
        self,
        answer_provider: Callable[..., Coroutine],
        result_callback: Optional[Callable] = None,
        question_callback: Optional[Callable] = None,
        timeout_callback: Optional[Callable] = None,
    ) -> QuizResult:
        """
        Execute the quiz asynchronously with non-blocking operations

        Args:
            answer_provider: Async callable(question, index) -> answer or None
            result_callback: Optional callback after each question
            question_callback: Optional callback before each question
            timeout_callback: Optional callback when time expires

        Returns:
            QuizResult with complete statistics
        """
        if not self.questions:
            raise ValueError("No questions in quiz")

        self._start_time = time.time()
        results = []
        correct_count = 0
        partial_count = 0

        questions_to_run = self.questions.copy()
        if self.randomize_order:
            random.shuffle(questions_to_run)

        for i, question in enumerate(questions_to_run, 1):
            # Check time limit
            if self.is_time_up():
                if timeout_callback:
                    await timeout_callback(question, i, len(questions_to_run))
                break

            if question_callback:
                await question_callback(question, i, len(questions_to_run))

            question_start = time.time()
            try:
                # Get answer with timeout if question has time limit
                if question.time_limit:
                    user_answer = await asyncio.wait_for(
                        answer_provider(question, i - 1),
                        timeout=question.time_limit,
                    )
                else:
                    user_answer = await answer_provider(question, i - 1)
            except asyncio.TimeoutError:
                user_answer = None
                status = ResultStatus.TIMEOUT
                score = 0.0
                time_taken = time.time() - question_start
                results.append(
                    QuestionResult(
                        question_index=i - 1,
                        user_answer="",
                        correct_answer=question.correct_answer,
                        status=status,
                        time_taken=time_taken,
                        score=score,
                    )
                )
                continue

            time_taken = time.time() - question_start

            # Determine status and score
            if user_answer is None:
                status = ResultStatus.SKIPPED
                score = 0.0
            else:
                check_result = question.check_answer(user_answer)
                if isinstance(check_result, bool):
                    status = ResultStatus.CORRECT if check_result else ResultStatus.INCORRECT
                    score = 1.0 if check_result else 0.0
                    if check_result:
                        correct_count += 1
                else:
                    status = ResultStatus.PARTIAL if check_result > 0 else ResultStatus.INCORRECT
                    score = check_result
                    if check_result > 0:
                        partial_count += 1

            result = QuestionResult(
                question_index=i - 1,
                user_answer=user_answer or "",
                correct_answer=question.correct_answer,
                status=status,
                time_taken=time_taken,
                score=score,
            )
            results.append(result)

            if result_callback:
                await result_callback(question, i, user_answer or "", status, time_taken)

        total_time = time.time() - self._start_time

        quiz_result = QuizResult(
            title=self.title,
            total_questions=len(questions_to_run),
            correct_answers=correct_count,
            time_taken=total_time,
            question_results=results,
            partial_answers=partial_count,
        )

        self._result = quiz_result
        return quiz_result

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate quiz configuration"""
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
