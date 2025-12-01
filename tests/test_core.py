"""Core tests - question types, quiz, and results"""
import pytest
from quizy.core import (
    Quiz,
    Question,
    MultipleChoiceQuestion,
    MultipleSelectQuestion,
    ShortTextQuestion,
    TrueFalseQuestion,
    MatchingQuestion,
    QuestionResult,
    QuizResult,
    ResultStatus,
    QuestionType,
)


class TestQuestionResult:
    """Test QuestionResult class"""

    def test_question_result_creation(self):
        """Test creating a question result"""
        result = QuestionResult(
            question_index=0,
            user_answer="A",
            correct_answer="A",
            status=ResultStatus.CORRECT,
            time_taken=5.0,
            score=1.0,
        )
        assert result.is_correct is True
        assert result.is_partial is False

    def test_question_result_partial(self):
        """Test partial credit result"""
        result = QuestionResult(
            question_index=0,
            user_answer=["A", "B"],
            correct_answer=["A", "B", "C"],
            status=ResultStatus.PARTIAL,
            time_taken=5.0,
            score=0.66,
        )
        assert result.is_correct is False
        assert result.is_partial is True

    def test_question_result_to_dict(self):
        """Test converting result to dictionary"""
        result = QuestionResult(
            question_index=0,
            user_answer="A",
            correct_answer="A",
            status=ResultStatus.CORRECT,
            time_taken=5.0,
            score=1.0,
        )
        result_dict = result.to_dict()
        assert result_dict["question_index"] == 0
        assert result_dict["status"] == "correct"
        assert result_dict["score"] == 1.0

    def test_question_result_incorrect(self):
        """Test incorrect question result"""
        result = QuestionResult(
            question_index=0,
            user_answer="B",
            correct_answer="A",
            status=ResultStatus.INCORRECT,
            time_taken=5.0,
        )
        assert result.is_correct is False

    def test_question_result_timeout(self):
        """Test timeout result"""
        result = QuestionResult(
            question_index=0,
            user_answer=None,
            correct_answer="A",
            status=ResultStatus.TIMEOUT,
            time_taken=30.0,
        )
        assert result.status == ResultStatus.TIMEOUT
        assert result.is_correct is False


class TestQuizResult:
    """Test QuizResult class"""

    def test_quiz_result_creation(self):
        """Test creating a quiz result"""
        result = QuizResult(
            title="Test Quiz",
            total_questions=5,
            correct_answers=4,
            time_taken=25.0,
        )
        assert result.title == "Test Quiz"
        assert result.total_questions == 5
        assert result.correct_answers == 4

    def test_quiz_result_score_percentage(self):
        """Test score percentage calculation"""
        result = QuizResult(
            title="Test",
            total_questions=10,
            correct_answers=7,
            time_taken=50.0,
        )
        result.question_results = [
            QuestionResult(i, "A", "A", ResultStatus.CORRECT, 5.0, 1.0)
            for i in range(7)
        ] + [
            QuestionResult(i, "B", "A", ResultStatus.INCORRECT, 5.0, 0.0)
            for i in range(7, 10)
        ]
        assert result.score_percentage == 70.0

    def test_quiz_result_skipped_count(self):
        """Test skipped question counting"""
        result = QuizResult(
            title="Test",
            total_questions=5,
            correct_answers=3,
            time_taken=25.0,
        )
        result.question_results = [
            QuestionResult(0, "A", "A", ResultStatus.CORRECT, 5.0, 1.0),
            QuestionResult(1, None, "B", ResultStatus.SKIPPED, 0.0, 0.0),
            QuestionResult(2, None, "C", ResultStatus.SKIPPED, 0.0, 0.0),
        ]
        assert result.skipped_count == 2

    def test_quiz_result_timeout_count(self):
        """Test timeout question counting"""
        result = QuizResult(
            title="Test",
            total_questions=5,
            correct_answers=3,
            time_taken=25.0,
        )
        result.question_results = [
            QuestionResult(0, "A", "A", ResultStatus.CORRECT, 5.0, 1.0),
            QuestionResult(1, None, "B", ResultStatus.TIMEOUT, 10.0, 0.0),
        ]
        assert result.timeout_count == 1

    def test_quiz_result_average_time_per_question(self):
        """Test average time per question"""
        result = QuizResult(
            title="Test",
            total_questions=5,
            correct_answers=5,
            time_taken=25.0,
        )
        assert result.average_time_per_question == 5.0

    def test_quiz_result_to_dict(self):
        """Test converting quiz result to dictionary"""
        result = QuizResult(
            title="Test",
            total_questions=2,
            correct_answers=2,
            time_taken=10.0,
        )
        result_dict = result.to_dict()
        assert result_dict["title"] == "Test"
        assert result_dict["total_questions"] == 2
        assert result_dict["correct_answers"] == 2

    def test_quiz_result_with_zero_questions(self):
        """Test results with zero questions"""
        result = QuizResult(
            title="Empty",
            total_questions=0,
            correct_answers=0,
            time_taken=0.0,
        )
        assert result.score_percentage == 0.0
        assert result.average_time_per_question == 0.0


class TestQuestionBaseClass:
    """Test Question base class"""

    def test_question_initialization(self):
        """Test question initialization"""
        q = Question(
            text="Test?",
            correct_answer="A",
            explanation="This is correct",
            time_limit=30.0,
        )
        assert q.text == "Test?"
        assert q.correct_answer == "A"
        assert q.explanation == "This is correct"
        assert q.time_limit == 30.0

    def test_question_metadata_default(self):
        """Test question metadata default"""
        q = Question(text="Test?", correct_answer="A")
        assert isinstance(q.metadata, dict)
        assert len(q.metadata) == 0

    def test_question_validate_config_invalid_text(self):
        """Test validation with no text"""
        q = Question(text="", correct_answer="A")
        is_valid, error = q.validate_config()
        assert is_valid is False
        assert error is not None

    def test_question_check_answer_not_implemented(self):
        """Test that check_answer raises NotImplementedError"""
        q = Question(text="Test?", correct_answer="A")
        with pytest.raises(NotImplementedError):
            q.check_answer("A")

    def test_question_get_options(self):
        """Test base question get_options returns None"""
        q = Question("Q?", "A")
        assert q.get_options() is None


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

    def test_get_options(self):
        """Test get_options returns options list"""
        options = ["A", "B", "C"]
        q = MultipleChoiceQuestion("Q?", options, "B")
        assert q.get_options() == options

    def test_shuffle_options(self):
        """Test shuffled options"""
        q = MultipleChoiceQuestion(
            text="Q?",
            options=["A", "B", "C", "D"],
            correct_answer="B",
            shuffle_options=True,
        )
        display1 = q.display_options
        display2 = q.display_options
        assert display1 == display2

    def test_no_shuffle(self):
        """Test non-shuffled options"""
        q = MultipleChoiceQuestion(
            text="Q?",
            options=["A", "B", "C"],
            correct_answer="B",
            shuffle_options=False,
        )
        assert q.display_options == ["A", "B", "C"]

    def test_option_index_zero(self):
        """Test get_option_by_index with 0 (invalid)"""
        q = MultipleChoiceQuestion("Q?", ["A", "B", "C"], "B")
        result = q.get_option_by_index(0)
        assert result is None

    def test_option_index_out_of_range(self):
        """Test get_option_by_index out of range"""
        q = MultipleChoiceQuestion("Q?", ["A", "B"], "A")
        result = q.get_option_by_index(10)
        assert result is None

    def test_with_all_options(self):
        """Test multiple choice with many options"""
        q = MultipleChoiceQuestion(
            "Which?",
            ["Option A", "Option B", "Option C", "Option D", "Option E"],
            "Option C"
        )
        assert q.check_answer("Option C") is True
        assert q.check_answer("Option A") is False


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

    def test_exact_match(self):
        """Test exact match in multiple select"""
        q = MultipleSelectQuestion(
            "Q?",
            ["A", "B", "C"],
            ["A", "B"]
        )
        assert q.check_answer(["A", "B"]) is True

    def test_partial_credit_calculation(self):
        """Test partial credit score calculation"""
        q = MultipleSelectQuestion(
            "Q?",
            ["A", "B", "C", "D"],
            ["A", "B"],
            allow_partial_credit=True
        )
        result = q.check_answer(["A"])
        assert result == 0.5

    def test_wrong_answers_no_partial_credit(self):
        """Test multiple select all wrong without partial credit"""
        q = MultipleSelectQuestion(
            "Q?",
            ["A", "B", "C", "D"],
            ["A", "B"],
            allow_partial_credit=False
        )
        assert q.check_answer(["C", "D"]) is False

    def test_partial_with_missed_answers(self):
        """Test partial credit when some answers are missed"""
        q = MultipleSelectQuestion(
            "Q?",
            ["A", "B", "C"],
            ["A", "B"],
            allow_partial_credit=True
        )
        result = q.check_answer(["A"])
        assert 0 < result < 1

    def test_with_incorrect_added(self):
        """Test multiple select with incorrect answer added"""
        q = MultipleSelectQuestion(
            "Q?",
            ["A", "B", "C"],
            ["A", "B"],
            allow_partial_credit=True
        )
        result = q.check_answer(["A", "C"])
        assert result == 0.0

    def test_partial_some_correct_some_missing(self):
        """Test partial credit with mix of correct and missing"""
        q = MultipleSelectQuestion(
            "Q?",
            ["A", "B", "C", "D"],
            ["B", "C", "D"],
            allow_partial_credit=True
        )
        result = q.check_answer(["B", "D"])
        assert result == pytest.approx(2/3)

    def test_validate_config(self):
        """Test validation of multiple select"""
        q = MultipleSelectQuestion(
            "Q?", ["A", "B", "C"], correct_answers=["A", "B"]
        )
        is_valid, error = q.validate_config()
        assert is_valid is True

    def test_shuffle_options(self):
        """Test shuffled options in multiple select"""
        q = MultipleSelectQuestion(
            text="Q?",
            options=["A", "B", "C"],
            correct_answers=["A", "B"],
            shuffle_options=True,
        )
        display1 = q.display_options
        display2 = q.display_options
        assert display1 == display2


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

    def test_with_explanation(self):
        """Test short text question with explanation"""
        q = ShortTextQuestion(
            "Q?",
            "answer",
            explanation="This is the answer"
        )
        assert q.explanation == "This is the answer"

    def test_with_time_limit(self):
        """Test short text with time limit"""
        q = ShortTextQuestion("Q?", "answer", time_limit=30.0)
        assert q.time_limit == 30.0

    def test_with_metadata(self):
        """Test short text with metadata"""
        q = ShortTextQuestion(
            "Q?",
            "answer",
            metadata={"difficulty": "hard"}
        )
        assert q.metadata["difficulty"] == "hard"

    def test_case_sensitive_false(self):
        """Test case insensitive matching"""
        q = ShortTextQuestion(
            text="Q?", correct_answer="Python", case_sensitive=False
        )
        assert q.check_answer("python") is True
        assert q.check_answer("PYTHON") is True

    def test_accepted_variations_with_case_sensitive(self):
        """Test accepted variations with case sensitivity"""
        q = ShortTextQuestion(
            text="Q?",
            correct_answer="Au",
            case_sensitive=True,
            accepted_variations=["gold"],
        )
        assert q.check_answer("Au") is True
        assert q.check_answer("gold") is True
        assert q.check_answer("au") is False

    def test_whitespace_with_variations(self):
        """Test whitespace trimming with variations"""
        q = ShortTextQuestion(
            text="Q?",
            correct_answer="hello",
            accepted_variations=["hi"],
        )
        assert q.check_answer("  hello  ") is True
        assert q.check_answer("  hi  ") is True

    def test_no_variations_exact_case(self):
        """Test short text without variations - exact case match"""
        q = ShortTextQuestion(
            "Q?",
            "Hello",
            case_sensitive=True
        )
        assert q.check_answer("Hello") is True
        assert q.check_answer("hello") is False

    def test_validate_config(self):
        """Test validation of short text"""
        q = ShortTextQuestion("Q?", "answer")
        is_valid, error = q.validate_config()
        assert is_valid is True

    def test_validate_config_empty_text(self):
        """Test short text validation with empty question text"""
        q = ShortTextQuestion("", "answer")
        is_valid, error = q.validate_config()
        assert is_valid is False

    def test_get_options(self):
        """Test short text get_options returns None"""
        q = ShortTextQuestion("Q?", "answer")
        assert q.get_options() is None

    def test_empty_variations_list(self):
        """Test short text with empty variations"""
        q = ShortTextQuestion(
            "Q?",
            "answer",
            accepted_variations=[]
        )
        assert q.check_answer("answer") is True

    def test_accepted_variations_list(self):
        """Test short text with accepted variations list"""
        q = ShortTextQuestion(
            "Q?",
            "hello",
            accepted_variations=["hi", "hey", "howdy"]
        )
        assert q.check_answer("hi") is True
        assert q.check_answer("hey") is True
        assert q.check_answer("goodbye") is False

    def test_with_variations_case_insensitive_mixed(self):
        """Test case insensitive with variations"""
        q = ShortTextQuestion(
            "Q?",
            "primary",
            case_sensitive=False,
            accepted_variations=["backup"]
        )
        assert q.check_answer("PRIMARY") is True
        assert q.check_answer("BACKUP") is True


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

    def test_with_explanation(self):
        """Test true/false with explanation"""
        q = TrueFalseQuestion(
            "Q?",
            True,
            explanation="True because..."
        )
        assert q.explanation == "True because..."

    def test_yes_variation(self):
        """Test 'yes' as true"""
        q = TrueFalseQuestion("Q?", True)
        assert q.check_answer("yes") is True

    def test_no_variation(self):
        """Test 'no' as false"""
        q = TrueFalseQuestion("Q?", False)
        assert q.check_answer("no") is True

    def test_string_yes_lowercase(self):
        """Test true with lowercase 'yes'"""
        q = TrueFalseQuestion("Q?", True)
        assert q.check_answer("YES") is True

    def test_with_float_zero(self):
        """Test false with float zero"""
        q = TrueFalseQuestion("Q?", False)
        assert q.check_answer(0.0) is True

    def test_with_1_and_0(self):
        """Test 1 as true and 0 as false"""
        q_true = TrueFalseQuestion("?", True)
        q_false = TrueFalseQuestion("?", False)
        assert q_true.check_answer(1) is True
        assert q_false.check_answer(0) is True

    def test_validate_config(self):
        """Test true/false validation"""
        q = TrueFalseQuestion("Q?", True)
        is_valid, error = q.validate_config()
        assert is_valid is True

    def test_validate_config_empty_text(self):
        """Test true/false validation with empty text"""
        q = TrueFalseQuestion("", True)
        is_valid, error = q.validate_config()
        assert is_valid is False


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

    def test_with_explanation(self):
        """Test matching with explanation"""
        q = MatchingQuestion(
            "Match",
            {"A": "1", "B": "2"},
            explanation="Match the pairs"
        )
        assert q.explanation == "Match the pairs"

    def test_with_time_limit(self):
        """Test matching with time limit"""
        q = MatchingQuestion(
            "Match",
            {"A": "1", "B": "2"},
            time_limit=60.0
        )
        assert q.time_limit == 60.0

    def test_shuffle_answers_caching(self):
        """Test matching answers are cached after shuffle"""
        q = MatchingQuestion(
            "Match",
            {"A": "1", "B": "2", "C": "3"},
            shuffle_answers=True
        )
        first = q.display_answers
        second = q.display_answers
        assert first is second

    def test_wrong_type_input(self):
        """Test matching with wrong input type"""
        q = MatchingQuestion("Match", {"A": "1", "B": "2"})
        result = q.check_answer("not a dict")
        assert result is False

    def test_partial_correct(self):
        """Test matching with partial credit"""
        q = MatchingQuestion(
            "Match",
            {"A": "1", "B": "2"},
            allow_partial_credit=True
        )
        result = q.check_answer({"A": "1", "B": "wrong"})
        assert result == 0.5

    def test_no_shuffle(self):
        """Test matching without shuffling"""
        q = MatchingQuestion(
            "Match",
            {"A": "1", "B": "2"},
            shuffle_answers=False
        )
        answers = q.display_answers
        assert answers == ["1", "2"]

    def test_validate_config(self):
        """Test matching validation"""
        q = MatchingQuestion("Q?", {"A": "1", "B": "2"})
        is_valid, error = q.validate_config()
        assert is_valid is True

    def test_validate_config_empty_text(self):
        """Test matching validation with empty text"""
        q = MatchingQuestion("", {"A": "1", "B": "2"})
        is_valid, error = q.validate_config()
        assert is_valid is False

    def test_get_options(self):
        """Test matching get_options returns dict"""
        q = MatchingQuestion("Q?", {"A": "1", "B": "2"})
        options = q.get_options()
        assert isinstance(options, dict)
        assert "prompts" in options
        assert "answers" in options

    def test_get_options_structure(self):
        """Test matching get_options structure"""
        pairs = {"Q1": "A1", "Q2": "A2"}
        q = MatchingQuestion("Match", pairs)
        options = q.get_options()
        assert "prompts" in options
        assert "answers" in options
        assert set(options["prompts"]) == set(pairs.keys())
        assert set(options["answers"]) == set(pairs.values())

    def test_all_correct_partial_credit_disabled(self):
        """Test matching full credit when partial disabled"""
        q = MatchingQuestion(
            "Match",
            {"A": "1", "B": "2"},
            allow_partial_credit=False
        )
        assert q.check_answer({"A": "1", "B": "2"}) is True


class TestQuiz:
    """Test Quiz class"""

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

        answers = ["A", "Y"]
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

        answers = [None, "Y"]
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

    def test_with_time_limit(self):
        """Test quiz with time limit"""
        quiz = Quiz("Test", time_limit=300.0)
        assert quiz.time_limit == 300.0

    def test_remove_question(self):
        """Test removing a question from quiz"""
        quiz = Quiz("Test")
        q1 = MultipleChoiceQuestion("Q1?", ["A", "B"], "A")
        quiz.add_question(q1)
        quiz.remove_question(0)
        assert quiz.get_question_count() == 0

    def test_get_all_questions(self):
        """Test getting all questions from quiz"""
        quiz = Quiz("Test")
        q1 = MultipleChoiceQuestion("Q1?", ["A", "B"], "A")
        q2 = MultipleChoiceQuestion("Q2?", ["X", "Y"], "X")
        quiz.add_question(q1)
        quiz.add_question(q2)
        
        questions = quiz.get_questions()
        assert len(questions) == 2
        assert q1 in questions
        assert q2 in questions

    def test_get_question_count(self):
        """Test getting question count"""
        quiz = Quiz("Test")
        quiz.add_question(MultipleChoiceQuestion("Q1?", ["A", "B"], "A"))
        quiz.add_question(MultipleChoiceQuestion("Q2?", ["X", "Y"], "X"))
        
        assert quiz.get_question_count() == 2

    def test_randomize_order(self):
        """Test randomizing question order"""
        quiz = Quiz("Test", randomize_order=True)
        for i in range(5):
            quiz.add_question(
                MultipleChoiceQuestion(f"Q{i}?", ["A", "B"], "A")
            )
        
        is_valid, errors = quiz.validate()
        assert is_valid is True

    def test_show_progress_false(self):
        """Test quiz with show_progress disabled"""
        quiz = Quiz("Test", show_progress=False)
        quiz.add_question(MultipleChoiceQuestion("Q?", ["A", "B"], "A"))
        is_valid, _ = quiz.validate()
        assert is_valid is True

    def test_allow_skip_true(self):
        """Test quiz with skip enabled"""
        quiz = Quiz("Test", allow_skip=True)
        quiz.add_question(MultipleChoiceQuestion("Q?", ["A", "B"], "A"))
        is_valid, _ = quiz.validate()
        assert is_valid is True

    def test_shuffle_options_true(self):
        """Test quiz with option shuffling"""
        quiz = Quiz("Test", shuffle_options=True)
        quiz.add_question(MultipleChoiceQuestion("Q?", ["A", "B"], "A"))
        is_valid, _ = quiz.validate()
        assert is_valid is True

    def test_multiple_question_types(self):
        """Test quiz with various question types"""
        quiz = Quiz("Mixed Quiz")
        quiz.add_question(
            MultipleChoiceQuestion("MC?", ["A", "B"], "A")
        )
        quiz.add_question(
            TrueFalseQuestion("TF?", True)
        )
        quiz.add_question(
            ShortTextQuestion("ST?", "answer")
        )
        quiz.add_question(
            MatchingQuestion("M?", {"A": "1", "B": "2"})
        )
        
        is_valid, errors = quiz.validate()
        assert is_valid is True

    def test_complex_quiz(self):
        """Test complex quiz with all question types"""
        quiz = Quiz(
            "Complex Quiz",
            time_limit=300.0,
            allow_skip=True,
            shuffle_options=True,
            randomize_order=True
        )
        
        quiz.add_question(
            MultipleChoiceQuestion("MC?", ["A", "B"], "A")
        )
        quiz.add_question(
            TrueFalseQuestion("TF?", True)
        )
        quiz.add_question(
            ShortTextQuestion("ST?", "answer")
        )
        quiz.add_question(
            MatchingQuestion("M?", {"A": "1", "B": "2"})
        )
        quiz.add_question(
            MultipleSelectQuestion(
                "MS?",
                ["A", "B", "C"],
                ["A", "B"]
            )
        )
        
        is_valid, errors = quiz.validate()
        assert is_valid is True
        assert quiz.get_question_count() == 5

    def test_to_dict(self):
        """Test quiz result to dictionary conversion"""
        quiz = Quiz("Test")
        quiz.add_question(
            MultipleChoiceQuestion("Q?", ["A", "B"], correct_answer="A")
        )

        def answer_provider(q, idx):
            return "A"

        result = quiz.execute(answer_provider=answer_provider)
        result_dict = result.to_dict()
        assert "title" in result_dict
        assert "score_percentage" in result_dict
        assert "question_results" in result_dict

    def test_with_explanation(self):
        """Test quiz with explanations"""
        quiz = Quiz("Test")
        quiz.add_question(
            MultipleChoiceQuestion(
                "What is 2+2?",
                ["3", "4", "5"],
                correct_answer="4",
                explanation="2+2 equals 4",
            )
        )

        def answer_provider(q, idx):
            return "4"

        result = quiz.execute(answer_provider=answer_provider)
        assert result.correct_answers == 1


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


class TestEnums:
    """Test enum values"""

    def test_question_type_enum_values(self):
        """Test question type enum has all values"""
        assert QuestionType.MULTIPLE_CHOICE.value == "multiple_choice"
        assert QuestionType.MULTIPLE_SELECT.value == "multiple_select"
        assert QuestionType.SHORT_TEXT.value == "short_text"
        assert QuestionType.TRUE_FALSE.value == "true_false"
        assert QuestionType.MATCHING.value == "matching"

    def test_result_status_enum_values(self):
        """Test result status enum has all values"""
        assert ResultStatus.CORRECT.value == "correct"
        assert ResultStatus.INCORRECT.value == "incorrect"
        assert ResultStatus.TIMEOUT.value == "timeout"
        assert ResultStatus.SKIPPED.value == "skipped"
        assert ResultStatus.PARTIAL.value == "partial"


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
