"""
Enhanced CLI utilities with async support, live timer display, and interactive feedback
Improvements:
- Live countdown timer display
- Better formatted output with progress indicators
- Async support for non-blocking I/O
- Enhanced user feedback and visual formatting
- Smart time management and warnings
"""

import asyncio
import sys
import time
import threading
from typing import Optional, Any, Callable, Coroutine
from datetime import timedelta

from .core import (
    Quiz,
    Question,
    ResultStatus,
    MultipleChoiceQuestion,
    MultipleSelectQuestion,
    ShortTextQuestion,
    TrueFalseQuestion,
    MatchingQuestion,
)


class TimerDisplay:
    """Displays and manages live countdown timer"""

    def __init__(self, duration: float):
        self.duration = duration
        self.start_time = time.time()
        self.paused_time = 0.0
        self.is_paused = False

    def get_elapsed(self) -> float:
        """Get elapsed time in seconds"""
        if self.is_paused:
            return self.paused_time
        return time.time() - self.start_time

    def get_remaining(self) -> float:
        """Get remaining time"""
        return max(0.0, self.duration - self.get_elapsed())

    def pause(self) -> None:
        """Pause the timer"""
        self.paused_time = self.get_elapsed()
        self.is_paused = True

    def resume(self) -> None:
        """Resume the timer"""
        if self.is_paused:
            self.start_time = time.time() - self.paused_time
            self.is_paused = False

    def is_expired(self) -> bool:
        """Check if time is up"""
        return self.get_remaining() <= 0

    def format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS"""
        td = timedelta(seconds=int(seconds))
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def get_warning_symbol(self) -> str:
        """Get visual indicator based on remaining time"""
        remaining = self.get_remaining()
        if remaining <= 10:
            return "⚠️ " if remaining > 0 else "❌"
        elif remaining <= 30:
            return "⏱️ "
        else:
            return "✓ "


class QuizCLI:
    """Enhanced CLI for interactive quiz sessions with live feedback"""

    # ANSI color codes
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    CLEAR_LINE = "\033[K"

    @staticmethod
    def format_header(text: str) -> str:
        """Format a header"""
        width = 60
        return f"\n{QuizCLI.BOLD}{QuizCLI.BLUE}{'=' * width}{QuizCLI.RESET}\n{QuizCLI.BOLD}  {text}{QuizCLI.RESET}\n{QuizCLI.BOLD}{QuizCLI.BLUE}{'=' * width}{QuizCLI.RESET}\n"

    @staticmethod
    def format_question_header(
        question_num: int, total: int, time_limit: Optional[float] = None
    ) -> str:
        """Format question header with optional timer"""
        time_str = f" | ⏱️  {int(time_limit)}s" if time_limit else ""
        return (
            f"\n{QuizCLI.BOLD}Question {question_num}/{total}{time_str}{QuizCLI.RESET}"
        )

    @staticmethod
    def display_question(
        question: Question,
        question_num: int,
        total_questions: int,
        timer: Optional[TimerDisplay] = None,
    ) -> None:
        """Display a question with appropriate format for its type"""
        header = QuizCLI.format_question_header(
            question_num, total_questions, question.time_limit
        )
        print(header)
        print(f"{QuizCLI.BOLD}{question.text}{QuizCLI.RESET}\n")

        if isinstance(question, (MultipleChoiceQuestion, MultipleSelectQuestion)):
            for idx, opt in enumerate(question.display_options, 1):
                print(f"  {QuizCLI.BLUE}{idx}.{QuizCLI.RESET} {opt}")

        elif isinstance(question, TrueFalseQuestion):
            print(f"  {QuizCLI.BLUE}1.{QuizCLI.RESET} True")
            print(f"  {QuizCLI.BLUE}2.{QuizCLI.RESET} False")

        elif isinstance(question, MatchingQuestion):
            print(f"{QuizCLI.BOLD}Left side (prompts):{QuizCLI.RESET}")
            for i, prompt in enumerate(question.prompts, 1):
                print(f"  {QuizCLI.BLUE}{i}.{QuizCLI.RESET} {prompt}")

            print(f"\n{QuizCLI.BOLD}Right side (options):{QuizCLI.RESET}")
            for j, answer in enumerate(question.display_answers, 1):
                print(f"  {QuizCLI.BLUE}{chr(96+j)}.{QuizCLI.RESET} {answer}")

        elif isinstance(question, ShortTextQuestion):
            print(f"{QuizCLI.BLUE}Answer type:{QuizCLI.RESET} Text input")
            if question.accepted_variations:
                print(
                    f"{QuizCLI.BLUE}Accepted variations:{QuizCLI.RESET} {', '.join(question.accepted_variations)}"
                )

    @staticmethod
    def get_answer(
        question: Question,
        allow_skip: bool = False,
        timer: Optional[TimerDisplay] = None,
    ) -> Optional[Any]:
        """Get user answer with optional timer display"""
        skip_help = " (or press Enter to skip)" if allow_skip else ""

        try:
            if isinstance(question, (MultipleChoiceQuestion, MultipleSelectQuestion)):
                return QuizCLI._get_choice_answer(
                    question, allow_skip, skip_help, timer
                )
            elif isinstance(question, TrueFalseQuestion):
                return QuizCLI._get_true_false_answer(allow_skip, skip_help, timer)
            elif isinstance(question, MatchingQuestion):
                return QuizCLI._get_matching_answer(
                    question, allow_skip, skip_help, timer
                )
            elif isinstance(question, ShortTextQuestion):
                return QuizCLI._get_text_answer(allow_skip, skip_help, timer)
            else:
                answer = QuizCLI._prompt_input(f"Your answer{skip_help}: ", timer)
                if not answer and allow_skip:
                    return None
                return answer

        except (KeyboardInterrupt, EOFError):
            return None

    @staticmethod
    def _prompt_input(prompt: str, timer: Optional[TimerDisplay] = None) -> str:
        """Get input with optional timer display"""
        if timer:
            QuizCLI._display_timer_prompt(prompt, timer)
        return input(f"\n{prompt}").strip()

    @staticmethod
    def _display_timer_prompt(prompt: str, timer: TimerDisplay) -> None:
        """Show prompt with timer"""
        remaining = timer.get_remaining()
        warning = timer.get_warning_symbol()
        time_str = timer.format_time(remaining)
        print(f"{warning} Time remaining: {time_str}")

    @staticmethod
    def _get_choice_answer(
        question: Question,
        allow_skip: bool,
        skip_help: str,
        timer: Optional[TimerDisplay] = None,
    ) -> Optional[Any]:
        """Get answer for multiple choice or multiple select"""
        max_option = len(question.display_options)
        is_multiple = isinstance(question, MultipleSelectQuestion)
        prompt_text = f"Enter option number(s) 1-{max_option}{skip_help}: "

        while True:
            try:
                answer_input = QuizCLI._prompt_input(prompt_text, timer)

                if not answer_input:
                    if allow_skip:
                        return None
                    print(
                        f"{QuizCLI.YELLOW}Please enter a number between 1 and {max_option}{QuizCLI.RESET}"
                    )
                    continue

                if is_multiple:
                    selections = [s.strip() for s in answer_input.split(",")]
                    indices = []

                    for sel in selections:
                        try:
                            idx = int(sel) - 1
                            if 0 <= idx < max_option:
                                indices.append(idx)
                            else:
                                print(
                                    f"{QuizCLI.RED}Option {idx + 1} out of range{QuizCLI.RESET}"
                                )
                        except ValueError:
                            print(f"{QuizCLI.RED}Invalid number: {sel}{QuizCLI.RESET}")

                    if indices:
                        return [question.display_options[i] for i in indices]
                else:
                    answer_idx = int(answer_input) - 1
                    if 0 <= answer_idx < max_option:
                        return question.display_options[answer_idx]
                    else:
                        print(
                            f"{QuizCLI.YELLOW}Please enter 1-{max_option}{QuizCLI.RESET}"
                        )

            except ValueError:
                print(f"{QuizCLI.RED}Invalid input{QuizCLI.RESET}")

    @staticmethod
    def _get_true_false_answer(
        allow_skip: bool,
        skip_help: str,
        timer: Optional[TimerDisplay] = None,
    ) -> Optional[bool]:
        """Get answer for true/false questions"""
        prompt_text = f"Your answer (1=True, 2=False){skip_help}: "

        while True:
            try:
                answer_input = QuizCLI._prompt_input(prompt_text, timer)

                if not answer_input:
                    if allow_skip:
                        return None
                    print(
                        f"{QuizCLI.YELLOW}Enter 1 for True or 2 for False{QuizCLI.RESET}"
                    )
                    continue

                if answer_input == "1":
                    return True
                elif answer_input == "2":
                    return False
                else:
                    print(f"{QuizCLI.YELLOW}Enter 1 or 2{QuizCLI.RESET}")

            except (ValueError, KeyError):
                print(f"{QuizCLI.RED}Invalid option{QuizCLI.RESET}")

    @staticmethod
    def _get_matching_answer(
        question: MatchingQuestion,
        allow_skip: bool,
        skip_help: str,
        timer: Optional[TimerDisplay] = None,
    ) -> Optional[dict]:
        """Get answer for matching questions"""
        matches = {}

        print(
            f"\n{QuizCLI.BOLD}Match each item on the left with one on the right:{QuizCLI.RESET}"
        )

        for prompt in question.prompts:
            print(
                f"\n{QuizCLI.BLUE}{prompt}{QuizCLI.RESET} {"matches with" if not question.metadata.get("prompt_key") else question.metadata.get("prompt_key")}:"
            )
            for idx, answer in enumerate(question.display_answers, 1):
                print(f"  {QuizCLI.BLUE}{idx}.{QuizCLI.RESET} {answer}")

            prompt_text = f"Match with (1-{len(question.display_answers)}){' or skip' if allow_skip else ''}: "

            while True:
                try:
                    answer_input = QuizCLI._prompt_input(prompt_text, timer)

                    if not answer_input:
                        if allow_skip:
                            break
                        continue

                    idx = int(answer_input) - 1
                    if 0 <= idx < len(question.display_answers):
                        matches[prompt] = question.display_answers[idx]
                        break
                    else:
                        print(
                            f"{QuizCLI.YELLOW}Select 1-{len(question.display_answers)}{QuizCLI.RESET}"
                        )

                except ValueError:
                    print(f"{QuizCLI.RED}Invalid number{QuizCLI.RESET}")

        return matches if matches else (None if allow_skip else {})

    @staticmethod
    def _get_text_answer(
        allow_skip: bool,
        skip_help: str,
        timer: Optional[TimerDisplay] = None,
    ) -> Optional[str]:
        """Get answer for short text questions"""
        prompt_text = f"Your answer{skip_help}: "

        try:
            answer = QuizCLI._prompt_input(prompt_text, timer)

            if not answer:
                if allow_skip:
                    return None
                print(f"{QuizCLI.YELLOW}Please enter an answer{QuizCLI.RESET}")
                return QuizCLI._get_text_answer(allow_skip, skip_help, timer)

            return answer

        except (ValueError, KeyError):
            print(f"{QuizCLI.RED}Invalid input{QuizCLI.RESET}")
            return QuizCLI._get_text_answer(allow_skip, skip_help, timer)

    @staticmethod
    def display_result(result) -> None:
        """Display quiz result summary"""
        print(QuizCLI.format_header(f"Quiz Results - {result.title}"))

        print(f"{QuizCLI.BOLD}Overall Performance:{QuizCLI.RESET}")
        print(f"  Total Questions:     {result.total_questions}")
        print(
            f"  Correct Answers:     {QuizCLI.GREEN}{result.correct_answers}{QuizCLI.RESET}"
        )
        print(
            f"  Partial Answers:     {QuizCLI.YELLOW}{result.partial_answers}{QuizCLI.RESET}"
            if result.partial_answers > 0
            else ""
        )
        print(
            f"  Score:               {QuizCLI._format_score(result.score_percentage)}"
        )
        print(
            f"  Time Taken:          {QuizCLI._format_time_duration(result.time_taken)}"
        )
        print(f"  Avg Time/Question:   {result.average_time_per_question:.1f}s")

        if result.skipped_count > 0:
            print(
                f"  Skipped:             {QuizCLI.YELLOW}{result.skipped_count}{QuizCLI.RESET}"
            )
        if result.timeout_count > 0:
            print(
                f"  Timeout:             {QuizCLI.RED}{result.timeout_count}{QuizCLI.RESET}"
            )

        print(f"\n{QuizCLI.BOLD}{QuizCLI.BLUE}{'=' * 60}{QuizCLI.RESET}\n")

    @staticmethod
    def display_detailed_results(result) -> None:
        """Display detailed results for each question"""
        print(QuizCLI.format_header("Detailed Results"))

        for res in result.question_results:
            status_icon = QuizCLI._get_status_icon(res.status)
            print(
                f"{status_icon} Question {res.question_index + 1}: {QuizCLI._format_status(res.status)}"
            )
            print(f"   Your Answer:     {res.user_answer}")
            print(f"   Correct Answer:  {res.correct_answer}")
            print(f"   Time Taken:      {res.time_taken:.2f}s")
            if res.score < 1.0:
                print(f"   Score:           {res.score * 100:.0f}%")
            print()

    @staticmethod
    def run_interactive(quiz: Quiz, show_timer: bool = True) -> None:
        """
        Run a quiz interactively in the terminal with timer display

        Args:
            quiz: The Quiz instance to run
            show_timer: Whether to show live timer
        """
        print(QuizCLI.format_header(f"Starting: {quiz.title}"))

        if not quiz.questions:
            print(f"{QuizCLI.RED}No questions available!{QuizCLI.RESET}")
            return

        try:
            # Create quiz timer if total time limit set
            quiz_timer = (
                TimerDisplay(quiz.time_limit)
                if quiz.time_limit and show_timer
                else None
            )

            def question_callback(q: Question, idx: int, total: int) -> None:
                """Display question before answering"""
                QuizCLI.display_question(
                    q, idx, total, quiz_timer if show_timer else None
                )

            def answer_provider(q: Question, idx: int) -> Optional[Any]:
                """Get answer from user"""
                question_timer = (
                    TimerDisplay(q.time_limit) if q.time_limit and show_timer else None
                )
                return QuizCLI.get_answer(q, quiz.allow_skip, question_timer)

            result = quiz.execute(
                answer_provider=answer_provider,
                question_callback=question_callback,
            )

            QuizCLI.display_result(result)

            # Ask to show detailed results
            try:
                show_detail = input("Show detailed results? (y/n): ").strip().lower()
                if show_detail == "y":
                    QuizCLI.display_detailed_results(result)
            except (EOFError, KeyboardInterrupt):
                pass

        except KeyboardInterrupt:
            print(f"\n\n{QuizCLI.YELLOW}Quiz interrupted!{QuizCLI.RESET}")
            sys.exit(0)

    @staticmethod
    async def run_interactive_async(quiz: Quiz, show_timer: bool = True) -> None:
        """
        Run a quiz asynchronously with non-blocking timer

        Args:
            quiz: The Quiz instance to run
            show_timer: Whether to show live timer
        """
        print(QuizCLI.format_header(f"Starting (Async): {quiz.title}"))

        if not quiz.questions:
            print(f"{QuizCLI.RED}No questions available!{QuizCLI.RESET}")
            return

        try:
            quiz_timer = (
                TimerDisplay(quiz.time_limit)
                if quiz.time_limit and show_timer
                else None
            )

            async def question_callback(q: Question, idx: int, total: int) -> None:
                """Display question before answering"""
                QuizCLI.display_question(
                    q, idx, total, quiz_timer if show_timer else None
                )

            async def answer_provider(q: Question, idx: int) -> Optional[Any]:
                """Get answer asynchronously"""
                # For now, still synchronous - can be enhanced with aioinput
                question_timer = (
                    TimerDisplay(q.time_limit) if q.time_limit and show_timer else None
                )
                return QuizCLI.get_answer(q, quiz.allow_skip, question_timer)

            result = await quiz.execute_async(
                answer_provider=answer_provider,
                question_callback=question_callback,
            )

            QuizCLI.display_result(result)

        except KeyboardInterrupt:
            print(f"\n\n{QuizCLI.YELLOW}Quiz interrupted!{QuizCLI.RESET}")
            sys.exit(0)

    @staticmethod
    def _format_score(percentage: float) -> str:
        """Format score with color coding"""
        if percentage >= 80:
            color = QuizCLI.GREEN
        elif percentage >= 60:
            color = QuizCLI.YELLOW
        else:
            color = QuizCLI.RED
        return f"{color}{percentage:.1f}%{QuizCLI.RESET}"

    @staticmethod
    def _format_time_duration(seconds: float) -> str:
        """Format duration as HH:MM:SS"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    @staticmethod
    def _format_status(status: ResultStatus) -> str:
        """Format status with color"""
        status_text = status.value.upper()
        if status == ResultStatus.CORRECT:
            return f"{QuizCLI.GREEN}{status_text}{QuizCLI.RESET}"
        elif status == ResultStatus.PARTIAL:
            return f"{QuizCLI.YELLOW}{status_text}{QuizCLI.RESET}"
        elif status == ResultStatus.TIMEOUT:
            return f"{QuizCLI.RED}{status_text}{QuizCLI.RESET}"
        else:
            return status_text

    @staticmethod
    def _get_status_icon(status: ResultStatus) -> str:
        """Get icon for status"""
        icons = {
            ResultStatus.CORRECT: f"{QuizCLI.GREEN}✓{QuizCLI.RESET}",
            ResultStatus.INCORRECT: f"{QuizCLI.RED}✗{QuizCLI.RESET}",
            ResultStatus.PARTIAL: f"{QuizCLI.YELLOW}◐{QuizCLI.RESET}",
            ResultStatus.TIMEOUT: f"{QuizCLI.RED}⏱{QuizCLI.RESET}",
            ResultStatus.SKIPPED: f"{QuizCLI.YELLOW}⊘{QuizCLI.RESET}",
        }
        return icons.get(status, "?")
