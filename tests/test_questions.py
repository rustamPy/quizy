"""Tests for different question types"""
import pytest
from quizy import (
    MultipleChoiceQuestion,
    MultipleSelectQuestion,
    ShortTextQuestion,
    TrueFalseQuestion,
    MatchingQuestion,
    Quiz,
    ResultStatus,
    QuestionType,
)


class TestMultipleChoiceQuestion:
    """Test multiple choice questions"""

    def test_check_correct_answer(self):
        q = MultipleChoiceQuestion(
            text="What is 2+2?", options=["3", "4", "5"], correct_answer="4"
        )
        assert q.check_answer("4") is True

    def test_check_incorrect_answer(self):
        q = MultipleChoiceQuestion(
            text="What is 2+2?", options=["3", "4", "5"], correct_answer="4"
        )
        assert q.check_answer("3") is False

    def test_get_option_by_index(self):
        q = MultipleChoiceQuestion(
            text="What is 2+2?", options=["3", "4", "5"], correct_answer="4"
        )
        assert q.get_option_by_index(2) == "4"

    def test_validation(self):
        q = MultipleChoiceQuestion(
            text="Valid?", options=["A", "B"], correct_answer="A"
        )
        is_valid, error = q.validate_config()
        assert is_valid is True

    def test_invalid_answer_not_in_options(self):
        with pytest.raises(ValueError):
            MultipleChoiceQuestion(
                text="Q?", options=["A", "B"], correct_answer="C"
            )


class TestMultipleSelectQuestion:
    """Test multiple select questions"""

    def test_check_all_correct(self):
        q = MultipleSelectQuestion(
            text="Select correct",
            options=["Python", "JavaScript", "HTML", "Java"],
            correct_answers=["Python", "JavaScript", "Java"],
        )
        assert q.check_answer(["Python", "JavaScript", "Java"]) is True

    def test_missing_one_answer(self):
        q = MultipleSelectQuestion(
            text="Select correct",
            options=["Python", "JavaScript", "HTML", "Java"],
            correct_answers=["Python", "JavaScript", "Java"],
        )
        assert q.check_answer(["Python", "Java"]) is False

    def test_extra_incorrect_answer(self):
        q = MultipleSelectQuestion(
            text="Select correct",
            options=["Python", "JavaScript", "HTML", "Java"],
            correct_answers=["Python", "JavaScript", "Java"],
        )
        assert q.check_answer(["Python", "JavaScript", "Java", "HTML"]) is False

    def test_requires_minimum_two_answers(self):
        with pytest.raises(ValueError):
            MultipleSelectQuestion(
                text="Q?",
                options=["A", "B"],
                correct_answers=["A"],
            )


class TestShortTextQuestion:
    """Test short text questions"""

    def test_case_insensitive_match(self):
        q = ShortTextQuestion(
            text="What year?", correct_answer="1991", case_sensitive=False
        )
        assert q.check_answer("1991") is True
        assert q.check_answer("1992") is False

    def test_case_sensitive_match(self):
        q = ShortTextQuestion(
            text="Symbol?", correct_answer="Au", case_sensitive=True
        )
        assert q.check_answer("Au") is True
        assert q.check_answer("au") is False

    def test_accepted_variations(self):
        q = ShortTextQuestion(
            text="Symbol?",
            correct_answer="Au",
            case_sensitive=True,
            accepted_variations=["au", "AU"],
        )
        assert q.check_answer("Au") is True
        assert q.check_answer("au") is True
        assert q.check_answer("AU") is True
        assert q.check_answer("ag") is False

    def test_whitespace_trimming(self):
        q = ShortTextQuestion(text="Year?", correct_answer="1991")
        assert q.check_answer("  1991  ") is True


class TestTrueFalseQuestion:
    """Test true/false questions"""

    def test_boolean_true(self):
        q = TrueFalseQuestion(text="Is true?", correct_answer=True)
        assert q.check_answer(True) is True
        assert q.check_answer(False) is False

    def test_string_true_variations(self):
        q = TrueFalseQuestion(text="Is true?", correct_answer=True)
        assert q.check_answer("true") is True
        assert q.check_answer("yes") is True
        assert q.check_answer("y") is True
        assert q.check_answer("1") is True

    def test_numeric_true(self):
        q = TrueFalseQuestion(text="Is true?", correct_answer=True)
        assert q.check_answer(1) is True
        assert q.check_answer(42) is True

    def test_boolean_false(self):
        q = TrueFalseQuestion(text="Is false?", correct_answer=False)
        assert q.check_answer(False) is True
        assert q.check_answer(True) is False

    def test_string_false_variations(self):
        q = TrueFalseQuestion(text="Is false?", correct_answer=False)
        assert q.check_answer("false") is True
        assert q.check_answer("no") is True
        assert q.check_answer("0") is True

    def test_numeric_false(self):
        q = TrueFalseQuestion(text="Is false?", correct_answer=False)
        assert q.check_answer(0) is True

    def test_non_boolean_raises_error(self):
        with pytest.raises(ValueError):
            TrueFalseQuestion(text="Q?", correct_answer="true")


class TestMatchingQuestion:
    """Test matching questions"""

    def test_correct_match(self):
        q = MatchingQuestion(
            text="Match",
            pairs={"France": "Paris", "Germany": "Berlin", "Italy": "Rome"},
        )
        assert (
            q.check_answer(
                {"France": "Paris", "Germany": "Berlin", "Italy": "Rome"}
            )
            is True
        )

    def test_one_wrong_match(self):
        q = MatchingQuestion(
            text="Match", pairs={"France": "Paris", "Germany": "Berlin"}
        )
        assert q.check_answer({"France": "Berlin", "Germany": "Berlin"}) is False

    def test_wrong_type(self):
        q = MatchingQuestion(
            text="Match", pairs={"France": "Paris", "Germany": "Berlin"}
        )
        assert q.check_answer(["France", "Paris"]) is False

    def test_minimum_two_pairs_required(self):
        with pytest.raises(ValueError):
            MatchingQuestion(text="Q?", pairs={"a": "1"})


class TestQuizExecution:
    """Test quiz execution with mixed question types"""

    def test_all_correct(self):
        quiz = Quiz("Test")
        quiz.add_question(
            MultipleChoiceQuestion("Q1?", ["A", "B"], correct_answer="A")
        )
        quiz.add_question(TrueFalseQuestion("Q2?", correct_answer=True))

        answers = ["A", True]
        answer_idx = [0]

        def answer_provider(q, idx):
            answer = answers[answer_idx[0]]
            answer_idx[0] += 1
            return answer

        result = quiz.execute(answer_provider=answer_provider)

        assert result.correct_answers == 2
        assert result.score_percentage == 100.0

    def test_mixed_results(self):
        quiz = Quiz("Test")
        quiz.add_question(
            MultipleChoiceQuestion("Q1?", ["A", "B"], correct_answer="A")
        )
        quiz.add_question(
            MultipleChoiceQuestion("Q2?", ["X", "Y"], correct_answer="X")
        )

        answers = ["A", "Y"]  # First correct, second wrong
        answer_idx = [0]

        def answer_provider(q, idx):
            answer = answers[answer_idx[0]]
            answer_idx[0] += 1
            return answer

        result = quiz.execute(answer_provider=answer_provider)

        assert result.correct_answers == 1
        assert result.score_percentage == 50.0
        assert result.question_results[0].status == ResultStatus.CORRECT
        assert result.question_results[1].status == ResultStatus.INCORRECT

    def test_skip_functionality(self):
        quiz = Quiz("Test", allow_skip=True)
        quiz.add_question(
            MultipleChoiceQuestion("Q1?", ["A", "B"], correct_answer="A")
        )
        quiz.add_question(
            MultipleChoiceQuestion("Q2?", ["X", "Y"], correct_answer="Y")
        )

        answers = [None, "Y"]  # Skip first, answer second
        answer_idx = [0]

        def answer_provider(q, idx):
            answer = answers[answer_idx[0]]
            answer_idx[0] += 1
            return answer

        result = quiz.execute(answer_provider=answer_provider)

        assert result.skipped_count == 1
        assert result.correct_answers == 1

    def test_multiple_select_execution(self):
        quiz = Quiz("Test")
        quiz.add_question(
            MultipleSelectQuestion(
                "Select all",
                options=["A", "B", "C"],
                correct_answers=["A", "C"],
            )
        )

        def answer_provider(q, idx):
            return ["A", "C"]

        result = quiz.execute(answer_provider=answer_provider)

        assert result.correct_answers == 1
        assert result.score_percentage == 100.0


class TestQuizValidation:
    """Test quiz validation"""

    def test_empty_quiz_invalid(self):
        quiz = Quiz("Empty")
        is_valid, errors = quiz.validate()
        assert is_valid is False
        assert len(errors) > 0

    def test_valid_quiz(self):
        quiz = Quiz("Valid")
        quiz.add_question(
            MultipleChoiceQuestion("Q?", ["A", "B"], correct_answer="A")
        )
        is_valid, errors = quiz.validate()
        assert is_valid is True
        assert len(errors) == 0


class TestQuestionTypes:
    """Test question type detection"""

    def test_multiple_choice_type(self):
        q = MultipleChoiceQuestion("Q?", ["A", "B"], "A")
        assert q.question_type == QuestionType.MULTIPLE_CHOICE

    def test_multiple_select_type(self):
        q = MultipleSelectQuestion("Q?", ["A", "B", "C"], ["A", "B"])
        assert q.question_type == QuestionType.MULTIPLE_SELECT

    def test_short_text_type(self):
        q = ShortTextQuestion("Q?", "answer")
        assert q.question_type == QuestionType.SHORT_TEXT

    def test_true_false_type(self):
        q = TrueFalseQuestion("Q?", True)
        assert q.question_type == QuestionType.TRUE_FALSE

    def test_matching_type(self):
        q = MatchingQuestion("Q?", {"a": "1", "b": "2"})
        assert q.question_type == QuestionType.MATCHING


class TestMetadata:
    """Test metadata storage"""

    def test_question_metadata(self):
        q = MultipleChoiceQuestion(
            text="Q?",
            options=["A", "B"],
            correct_answer="A",
            metadata={
                "difficulty": "easy",
                "topic": "math",
                "tags": ["basic"],
            },
        )
        assert q.metadata["difficulty"] == "easy"
        assert q.metadata["topic"] == "math"
        assert "basic" in q.metadata["tags"]

    def test_empty_metadata_default(self):
        q = MultipleChoiceQuestion(
            text="Q?",
            options=["A", "B"],
            correct_answer="A",
        )
        assert isinstance(q.metadata, dict)
        assert len(q.metadata) == 0
