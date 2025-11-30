"""
CLI utilities for interactive quiz interface.
Provides helper functions for building terminal-based quiz applications.
"""
import sys
import time
from typing import Optional
from .core import Quiz, Question, ResultStatus


class QuizCLI:
    """Helper class for building CLI quiz interfaces"""
    
    @staticmethod
    def display_question(question: Question, question_num: int, total_questions: int) -> None:
        """Display a question and its options"""
        print(f"\nQuestion {question_num}/{total_questions}:")
        print(f"{question.text}\n")
        
        for idx, opt in enumerate(question.options, 1):
            print(f"  {idx}. {opt}")
    
    @staticmethod
    def get_answer(question: Question, allow_skip: bool = False) -> Optional[str]:
        """
        Get user answer from input with validation
        
        Args:
            question: The question to get answer for
            allow_skip: If True, allow empty input to skip
            
        Returns:
            The selected answer or None if skipped
        """
        max_option = len(question.options)
        skip_help = " (or press Enter to skip)" if allow_skip else ""
        
        while True:
            try:
                answer_input = input(f"\nYour answer (1-{max_option}){skip_help}: ").strip()
                
                if not answer_input:
                    if allow_skip:
                        return None
                    print(f"Please enter a number between 1 and {max_option}")
                    continue
                
                answer_idx = int(answer_input) - 1
                
                if 0 <= answer_idx < max_option:
                    return question.options[answer_idx]
                else:
                    print(f"Please enter a number between 1 and {max_option}")
            except ValueError:
                print("Please enter a valid number")
            except (KeyboardInterrupt, EOFError):
                return None
    
    @staticmethod
    def display_result(result) -> None:
        """Display quiz result summary"""
        print(f"\n{'='*60}")
        print(f"  {result.title}")
        print(f"{'='*60}\n")
        
        print(f"Total Questions:   {result.total_questions}")
        print(f"Correct Answers:   {result.correct_answers}")
        print(f"Score:             {result.score_percentage:.1f}%")
        print(f"Time Taken:        {result.time_taken:.1f}s")
        
        if result.skipped_count > 0:
            print(f"Skipped:           {result.skipped_count}")
        if result.timeout_count > 0:
            print(f"Timeout:           {result.timeout_count}")
        
        print(f"\n{'='*60}\n")
    
    @staticmethod
    def display_detailed_results(result) -> None:
        """Display detailed results for each question"""
        print(f"\n{'='*60}")
        print(f"  Detailed Results")
        print(f"{'='*60}\n")
        
        for res in result.question_results:
            status_icon = "✓" if res.status == ResultStatus.CORRECT else "✗"
            print(f"{status_icon} Question {res.question_index + 1}: {res.status.value.upper()}")
            print(f"   Your Answer:     {res.user_answer}")
            print(f"   Correct Answer:  {res.correct_answer}")
            print(f"   Time Taken:      {res.time_taken:.2f}s")
            print()
    
    @staticmethod
    def run_interactive(quiz: Quiz) -> None:
        """
        Run a quiz interactively in the terminal
        
        Args:
            quiz: The Quiz instance to run
        """
        print(f"\n{'='*60}")
        print(f"  {quiz.title}")
        print(f"{'='*60}\n")
        
        if not quiz.questions:
            print("No questions available!")
            return
        
        try:
            result = quiz.execute(
                answer_provider=lambda q, idx: QuizCLI.get_answer(q, quiz.allow_skip),
                question_callback=lambda q, idx, total: QuizCLI.display_question(q, idx, total)
            )
            
            QuizCLI.display_result(result)
            
        except KeyboardInterrupt:
            print("\n\nQuiz interrupted!")
            sys.exit(0)


class TimerManager:
    """Manage time limits for quizzes and questions"""
    
    def __init__(self):
        self._question_start = None
        self._quiz_start = None
        self._question_time_limit = None
        self._quiz_time_limit = None
    
    def start_quiz(self, time_limit: Optional[float] = None) -> None:
        """Start quiz timer"""
        self._quiz_start = time.time()
        self._quiz_time_limit = time_limit
    
    def start_question(self, time_limit: Optional[float] = None) -> None:
        """Start question timer"""
        self._question_start = time.time()
        self._question_time_limit = time_limit
    
    def get_question_elapsed(self) -> float:
        """Get elapsed time for current question"""
        if self._question_start is None:
            return 0.0
        return time.time() - self._question_start
    
    def get_quiz_elapsed(self) -> float:
        """Get elapsed time for quiz"""
        if self._quiz_start is None:
            return 0.0
        return time.time() - self._quiz_start
    
    def is_question_timeout(self) -> bool:
        """Check if question time limit exceeded"""
        if self._question_time_limit is None:
            return False
        return self.get_question_elapsed() >= self._question_time_limit
    
    def is_quiz_timeout(self) -> bool:
        """Check if quiz time limit exceeded"""
        if self._quiz_time_limit is None:
            return False
        return self.get_quiz_elapsed() >= self._quiz_time_limit
    
    def get_question_remaining(self) -> Optional[float]:
        """Get remaining time for question"""
        if self._question_time_limit is None:
            return None
        remaining = self._question_time_limit - self.get_question_elapsed()
        return max(0.0, remaining)
    
    def get_quiz_remaining(self) -> Optional[float]:
        """Get remaining time for quiz"""
        if self._quiz_time_limit is None:
            return None
        remaining = self._quiz_time_limit - self.get_quiz_elapsed()
        return max(0.0, remaining)
