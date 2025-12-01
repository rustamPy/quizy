"""CLI tests - interactive quiz session tests"""
import pytest
import sys
import io
import time
from unittest.mock import patch, MagicMock
from datetime import timedelta

from quizy.cli import QuizCLI, TimerDisplay
from quizy.core import (
    Quiz,
    MultipleChoiceQuestion,
    MultipleSelectQuestion,
    TrueFalseQuestion,
    MatchingQuestion,
    ShortTextQuestion,
    ResultStatus,
    QuizResult,
    QuestionResult,
)


class TestTimerDisplay:
    """Test TimerDisplay class"""

    def test_timer_initialization(self):
        """Test timer initialization"""
        timer = TimerDisplay(60.0)
        assert timer.duration == 60.0
        assert timer.is_paused is False

    def test_timer_get_elapsed(self):
        """Test elapsed time calculation"""
        timer = TimerDisplay(60.0)
        elapsed = timer.get_elapsed()
        assert 0 <= elapsed < 1

    def test_timer_get_remaining(self):
        """Test remaining time calculation"""
        timer = TimerDisplay(60.0)
        remaining = timer.get_remaining()
        assert 59 < remaining <= 60

    def test_timer_pause_resume(self):
        """Test pause and resume functionality"""
        timer = TimerDisplay(60.0)
        timer.pause()
        assert timer.is_paused is True
        paused_elapsed = timer.get_elapsed()
        timer.resume()
        assert timer.is_paused is False
        assert abs(timer.get_elapsed() - paused_elapsed) < 0.1

    def test_timer_is_expired(self):
        """Test expiration check"""
        timer = TimerDisplay(0.01)
        time.sleep(0.02)
        assert timer.is_expired() is True

    def test_timer_is_not_expired(self):
        """Test non-expiration"""
        timer = TimerDisplay(60.0)
        assert timer.is_expired() is False

    def test_timer_format_time(self):
        """Test time formatting"""
        timer = TimerDisplay(60.0)
        assert timer.format_time(125) == "02:05"
        assert timer.format_time(5) == "00:05"
        assert timer.format_time(0) == "00:00"

    def test_timer_get_warning_symbol_expired(self):
        """Test warning symbol when expired"""
        timer = TimerDisplay(0.01)
        time.sleep(0.02)
        assert timer.get_warning_symbol() == "❌"

    def test_timer_get_warning_symbol_low_time(self):
        """Test warning symbol with low time"""
        timer = TimerDisplay(5.0)
        symbol = timer.get_warning_symbol()
        assert symbol == "⚠️ "

    def test_timer_get_warning_symbol_medium_time(self):
        """Test warning symbol with medium time"""
        timer = TimerDisplay(60.0)
        symbol = timer.get_warning_symbol()
        assert symbol == "✓ "

    def test_timer_pause_when_paused(self):
        """Test pausing an already paused timer"""
        timer = TimerDisplay(60.0)
        timer.pause()
        timer.pause()
        assert timer.is_paused is True

    def test_timer_remaining_after_expiry(self):
        """Test remaining time after expiry"""
        timer = TimerDisplay(0.01)
        time.sleep(0.02)
        remaining = timer.get_remaining()
        assert remaining == 0.0

    def test_timer_display_remaining_exact(self):
        """Test exact remaining time calculation"""
        timer = TimerDisplay(100.0)
        remaining = timer.get_remaining()
        assert 99 < remaining <= 100

    def test_timer_format_large_duration(self):
        """Test formatting large time duration"""
        timer = TimerDisplay(3600.0)
        formatted = timer.format_time(3661)
        assert ":" in formatted


class TestQuizCLIFormatting:
    """Test QuizCLI formatting methods"""

    def test_format_header(self):
        """Test header formatting"""
        header = QuizCLI.format_header("Test Header")
        assert "Test Header" in header
        assert "=" in header

    def test_format_question_header_without_timer(self):
        """Test question header without timer"""
        header = QuizCLI.format_question_header(1, 5)
        assert "Question 1/5" in header
        assert "⏱️" not in header

    def test_format_question_header_with_timer(self):
        """Test question header with timer"""
        header = QuizCLI.format_question_header(1, 5, time_limit=30.0)
        assert "Question 1/5" in header
        assert "⏱️" in header
        assert "30" in header

    def test_format_header_contains_border(self):
        """Test header formatting includes border"""
        header = QuizCLI.format_header("Test Header")
        assert "=" in header
        assert "Test Header" in header


class TestQuizCLIDisplayQuestion:
    """Test QuizCLI question display methods"""

    def test_display_multiple_choice_question(self, capsys):
        """Test displaying multiple choice question"""
        q = MultipleChoiceQuestion("What is 2+2?", ["3", "4", "5"], "4")
        QuizCLI.display_question(q, 1, 5)
        captured = capsys.readouterr()
        assert "What is 2+2?" in captured.out
        assert "3" in captured.out
        assert "4" in captured.out

    def test_display_true_false_question(self, capsys):
        """Test displaying true/false question"""
        q = TrueFalseQuestion("Is Python awesome?", True)
        QuizCLI.display_question(q, 1, 3)
        captured = capsys.readouterr()
        assert "Is Python awesome?" in captured.out
        assert "True" in captured.out
        assert "False" in captured.out

    def test_display_matching_question(self, capsys):
        """Test displaying matching question"""
        q = MatchingQuestion("Match countries", {"France": "Paris", "Germany": "Berlin"})
        QuizCLI.display_question(q, 1, 2)
        captured = capsys.readouterr()
        assert "Match countries" in captured.out
        assert "France" in captured.out
        assert "Paris" in captured.out

    def test_display_short_text_question(self, capsys):
        """Test displaying short text question"""
        q = ShortTextQuestion("What year?", "1991")
        QuizCLI.display_question(q, 1, 2)
        captured = capsys.readouterr()
        assert "What year?" in captured.out
        assert "Text input" in captured.out

    def test_display_question_with_timer(self, capsys):
        """Test displaying question with time limit"""
        q = MultipleChoiceQuestion("Q?", ["A", "B"], "A", time_limit=30.0)
        QuizCLI.display_question(q, 1, 1, timer=None)
        captured = capsys.readouterr()
        assert "Q?" in captured.out

    def test_display_multiple_select_question(self, capsys):
        """Test displaying multiple select question"""
        q = MultipleSelectQuestion("Select all", ["A", "B", "C"], ["A", "B"])
        QuizCLI.display_question(q, 1, 2)
        captured = capsys.readouterr()
        assert "Select all" in captured.out

    def test_display_question_with_matching(self, capsys):
        """Test displaying matching question"""
        q = MatchingQuestion("Match", {"France": "Paris", "Germany": "Berlin"})
        QuizCLI.display_question(q, 1, 1)
        captured = capsys.readouterr()
        assert "France" in captured.out or "Match" in captured.out

    def test_display_question_with_short_text_variations(self, capsys):
        """Test displaying short text with variations"""
        q = ShortTextQuestion("Q?", "answer", accepted_variations=["alternate", "other"])
        QuizCLI.display_question(q, 1, 1)
        captured = capsys.readouterr()
        assert "alternate" in captured.out or "Q?" in captured.out


class TestQuizCLIGetAnswer:
    """Test QuizCLI get_answer methods"""

    def test_get_answer_multiple_choice(self):
        """Test getting multiple choice answer"""
        q = MultipleChoiceQuestion("Q?", ["A", "B", "C"], "B")
        with patch("builtins.input", return_value="2"):
            answer = QuizCLI.get_answer(q, allow_skip=False)
            assert answer == "B"

    def test_get_answer_true_false_true(self):
        """Test getting true/false answer (true)"""
        q = TrueFalseQuestion("Q?", True)
        with patch("builtins.input", return_value="1"):
            answer = QuizCLI.get_answer(q, allow_skip=False)
            assert answer is True

    def test_get_answer_true_false_false(self):
        """Test getting true/false answer (false)"""
        q = TrueFalseQuestion("Q?", False)
        with patch("builtins.input", return_value="2"):
            answer = QuizCLI.get_answer(q, allow_skip=False)
            assert answer is False

    def test_get_answer_short_text(self):
        """Test getting short text answer"""
        q = ShortTextQuestion("Q?", "hello")
        with patch("builtins.input", return_value="hello"):
            answer = QuizCLI.get_answer(q, allow_skip=False)
            assert answer == "hello"

    def test_get_answer_with_skip_none(self):
        """Test getting answer with skip enabled"""
        q = MultipleChoiceQuestion("Q?", ["A", "B"], "A")
        with patch("builtins.input", return_value=""):
            answer = QuizCLI.get_answer(q, allow_skip=True)
            assert answer is None

    def test_get_answer_keyboard_interrupt(self):
        """Test handling keyboard interrupt"""
        q = MultipleChoiceQuestion("Q?", ["A", "B"], "A")
        with patch("builtins.input", side_effect=KeyboardInterrupt()):
            answer = QuizCLI.get_answer(q, allow_skip=False)
            assert answer is None

    def test_get_answer_eof_error(self):
        """Test handling EOF error"""
        q = MultipleChoiceQuestion("Q?", ["A", "B"], "A")
        with patch("builtins.input", side_effect=EOFError()):
            answer = QuizCLI.get_answer(q, allow_skip=False)
            assert answer is None


class TestQuizCLIChoiceAnswer:
    """Test choice answer handling"""

    def test_get_choice_answer_valid(self):
        """Test valid choice input"""
        q = MultipleChoiceQuestion("Q?", ["A", "B", "C"], "B")
        with patch.object(QuizCLI, "_prompt_input", return_value="2"):
            answer = QuizCLI._get_choice_answer(q, False, "", None)
            assert answer == "B"

    def test_get_choice_answer_invalid_range(self):
        """Test invalid choice - out of range"""
        q = MultipleChoiceQuestion("Q?", ["A", "B"], "A")
        with patch.object(QuizCLI, "_prompt_input", side_effect=["5", "1"]):
            with patch("builtins.print"):
                answer = QuizCLI._get_choice_answer(q, False, "", None)
                assert answer == "A"

    def test_get_choice_answer_invalid_input(self):
        """Test invalid choice - non-numeric"""
        q = MultipleChoiceQuestion("Q?", ["A", "B"], "A")
        with patch.object(QuizCLI, "_prompt_input", side_effect=["abc", "1"]):
            with patch("builtins.print"):
                answer = QuizCLI._get_choice_answer(q, False, "", None)
                assert answer == "A"

    def test_get_choice_answer_empty_with_skip(self):
        """Test empty answer with skip enabled"""
        q = MultipleChoiceQuestion("Q?", ["A", "B"], "A")
        with patch.object(QuizCLI, "_prompt_input", return_value=""):
            answer = QuizCLI._get_choice_answer(q, allow_skip=True, skip_help="", timer=None)
            assert answer is None

    def test_get_multiple_select_answer(self):
        """Test multiple select answer"""
        q = MultipleSelectQuestion("Q?", ["A", "B", "C"], ["A", "B"])
        with patch.object(QuizCLI, "_prompt_input", return_value="1,2"):
            answer = QuizCLI._get_choice_answer(q, False, "", None)
            assert answer == ["A", "B"]

    def test_get_multiple_select_answer_invalid(self):
        """Test multiple select with invalid number"""
        q = MultipleSelectQuestion("Q?", ["A", "B", "C"], ["A", "B"])
        with patch.object(QuizCLI, "_prompt_input", side_effect=["not_a_number", "1,2"]):
            with patch("builtins.print"):
                answer = QuizCLI._get_choice_answer(q, False, "", None)
                assert answer == ["A", "B"]

    def test_get_choice_answer_handles_comma_separated(self):
        """Test choice answer parsing comma-separated input"""
        q = MultipleSelectQuestion("Q?", ["A", "B", "C"], ["A", "B"])
        with patch.object(QuizCLI, "_prompt_input", return_value="1, 2"):
            result = QuizCLI._get_choice_answer(q, False, "", None)
            assert "A" in result
            assert "B" in result


class TestQuizCLITrueFalseAnswer:
    """Test true/false answer handling"""

    def test_get_true_false_answer_true(self):
        """Test true answer input"""
        with patch.object(QuizCLI, "_prompt_input", return_value="1"):
            answer = QuizCLI._get_true_false_answer(False, "", None)
            assert answer is True

    def test_get_true_false_answer_false(self):
        """Test false answer input"""
        with patch.object(QuizCLI, "_prompt_input", return_value="2"):
            answer = QuizCLI._get_true_false_answer(False, "", None)
            assert answer is False

    def test_get_true_false_answer_invalid(self):
        """Test invalid true/false input"""
        with patch.object(QuizCLI, "_prompt_input", side_effect=["3", "1"]):
            with patch("builtins.print"):
                answer = QuizCLI._get_true_false_answer(False, "", None)
                assert answer is True

    def test_get_true_false_answer_non_numeric(self):
        """Test non-numeric true/false input"""
        with patch.object(QuizCLI, "_prompt_input", side_effect=["abc", "2"]):
            with patch("builtins.print"):
                answer = QuizCLI._get_true_false_answer(False, "", None)
                assert answer is False

    def test_get_true_false_answer_empty_with_skip(self):
        """Test empty true/false with skip"""
        with patch.object(QuizCLI, "_prompt_input", return_value=""):
            answer = QuizCLI._get_true_false_answer(True, "", None)
            assert answer is None


class TestQuizCLITextAnswer:
    """Test short text answer handling"""

    def test_get_text_answer(self):
        """Test getting text answer"""
        with patch.object(QuizCLI, "_prompt_input", return_value="hello"):
            answer = QuizCLI._get_text_answer(False, "", None)
            assert answer == "hello"

    def test_get_text_answer_empty_with_skip(self):
        """Test empty text answer with skip"""
        with patch.object(QuizCLI, "_prompt_input", return_value=""):
            answer = QuizCLI._get_text_answer(True, "", None)
            assert answer is None

    def test_get_text_answer_empty_no_skip(self):
        """Test empty text answer without skip - retry"""
        with patch.object(QuizCLI, "_prompt_input", side_effect=["", "answer"]):
            with patch("builtins.print"):
                answer = QuizCLI._get_text_answer(False, "", None)
                assert answer == "answer"

    def test_get_text_answer_retries_on_empty(self):
        """Test text answer retries when empty"""
        q = ShortTextQuestion("Q?", "answer")
        with patch.object(QuizCLI, "_prompt_input", side_effect=["", "test"]):
            result = QuizCLI._get_text_answer(allow_skip=False, skip_help="", timer=None)
            assert result == "test"


class TestQuizCLIMatchingAnswer:
    """Test matching answer handling"""

    def test_get_matching_answer_empty_with_skip(self):
        """Test empty matching answer with skip"""
        q = MatchingQuestion("Match", {"A": "1", "B": "2"})
        with patch.object(QuizCLI, "_prompt_input", return_value=""):
            answer = QuizCLI._get_matching_answer(q, True, "", None)
            assert answer is None


class TestQuizCLIPromptInput:
    """Test prompt input methods"""

    def test_prompt_input_without_timer(self):
        """Test basic prompt input without timer"""
        with patch("builtins.input", return_value="test input"):
            result = QuizCLI._prompt_input("Enter: ", None)
            assert result == "test input"


class TestQuizCLIHelperMethods:
    """Test QuizCLI helper methods"""

    def test_get_status_icon_correct(self):
        """Test status icon for correct answer"""
        icon = QuizCLI._get_status_icon(ResultStatus.CORRECT)
        assert "✓" in icon

    def test_get_status_icon_incorrect(self):
        """Test status icon for incorrect answer"""
        icon = QuizCLI._get_status_icon(ResultStatus.INCORRECT)
        assert "✗" in icon

    def test_get_status_icon_skipped(self):
        """Test status icon for skipped question"""
        icon = QuizCLI._get_status_icon(ResultStatus.SKIPPED)
        assert "⊘" in icon

    def test_get_status_icon_timeout(self):
        """Test status icon for timeout"""
        icon = QuizCLI._get_status_icon(ResultStatus.TIMEOUT)
        assert "⏱" in icon

    def test_display_result(self, capsys):
        """Test displaying quiz result"""
        result = QuizResult(
            title="Test Quiz",
            total_questions=10,
            correct_answers=8,
            time_taken=60.0
        )
        QuizCLI.display_result(result)
        captured = capsys.readouterr()
        assert "8" in captured.out or "Test Quiz" in captured.out

    def test_display_detailed_results(self, capsys):
        """Test displaying detailed results"""
        result = QuizResult(
            title="Test",
            total_questions=2,
            correct_answers=1,
            time_taken=20.0
        )
        result.question_results = [
            QuestionResult(0, "A", "A", ResultStatus.CORRECT, 10.0, 1.0),
            QuestionResult(1, "Y", "X", ResultStatus.INCORRECT, 10.0, 0.0),
        ]
        QuizCLI.display_detailed_results(result)
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_color_constants_are_strings(self):
        """Test that color constants are valid ANSI codes"""
        assert isinstance(QuizCLI.BOLD, str)
        assert isinstance(QuizCLI.GREEN, str)
        assert isinstance(QuizCLI.RED, str)

    def test_clear_line_defined(self):
        """Test that clear line code is defined"""
        assert hasattr(QuizCLI, "CLEAR_LINE")

    def test_timer_warning_levels(self):
        """Test different timer warning levels"""
        # Low time
        timer_low = TimerDisplay(5.0)
        symbol_low = timer_low.get_warning_symbol()
        assert symbol_low in ["⚠️ ", "❌"]
        
        # Medium time
        timer_med = TimerDisplay(60.0)
        symbol_med = timer_med.get_warning_symbol()
        assert symbol_med in ["⏱️ ", "✓ "]
        
        # High time
        timer_high = TimerDisplay(300.0)
        symbol_high = timer_high.get_warning_symbol()
        assert symbol_high == "✓ "
