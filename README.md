# Quizy

## Overview

A lightweight, API-first Python quiz framework for creating interactive quizzes and assessments. Features async execution, timers, partial credit, shuffling, and AI-powered question generation.

**Key Features**:
- Async/await support with `execute_async()`
- Real-time countdown timers with visual feedback
- Partial credit for flexible grading
- Question option shuffling and randomization
- Interactive CLI with color-coded results
- AI-powered question generation via OpenAI

## Installation

```bash
pip install quizy # comes with OpenAI
```

## Adding Manual Questions

Create different question types:

```python
from quizy import Quiz, MultipleChoiceQuestion, MatchingQuestion

quiz = Quiz(title="My Quiz", time_limit=60)

# Multiple Choice
quiz.add_question(MultipleChoiceQuestion(
    text="What is the capital of France?",
    options=["London", "Berlin", "Paris", "Madrid"],
    correct_answer="Paris",
    shuffle_options=True,
    time_limit=10
))

# Matching
quiz.add_question(MatchingQuestion(
    text="Match programming terms",
    pairs={
        "def": "Function definition",
        "class": "Class definition",
        "async": "Asynchronous function"
    },
    shuffle_answers=True,
    allow_partial_credit=True,
    time_limit=15
))

# Define a synchronous answer provider for terminal input
def your_answer_provider(question, idx):
    print(f"\nQuestion {idx+1}: {question.text}")

    # Show options if available
    options = question.get_options()
    if options:
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")

    # Get user input
    user_input = input("> ")

    # Convert input to correct option if needed
    if options:
        try:
            choice = int(user_input)
            return question.get_option_by_index(choice)
        except:
            return user_input.strip()
    return user_input.strip()


# Run the quiz synchronously (if you use in the terminal)
result = quiz.execute(your_answer_provider)
print(f"Score: {result.score_percentage:.1f}%")
```

## Adding AI-Generated Questions

Generate quiz questions automatically using OpenAI and test it on terminal using QuizCLI:

```python
from quizy import Quiz, QuestionType
from quizy.ai_generator import AIQuestionGenerator
import time

# Initialize AI generator
generator = AIQuestionGenerator()

# Generate questions (synchronously)
questions = generator.generate_questions_set(
    topic="Python Programming",
    num_questions=5,
    question_types=[
        QuestionType.MULTIPLE_CHOICE,
        QuestionType.TRUE_FALSE,
        QuestionType.MULTIPLE_SELECT,
        QuestionType.SHORT_TEXT,
        QuestionType.MATCHING,
    ],
    difficulty="medium"
)

# Create the quiz
quiz = Quiz(title="AI-Generated Python Quiz")
for q in questions:
    if q:
        quiz.add_question(q)

# Define a synchronous answer provider for terminal input
def your_answer_provider(question, idx):
    print(f"\nQuestion {idx+1}: {question.text}")

    # Show options if available
    options = question.get_options()
    if options:
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")

    # Get user input
    user_input = input("> ")

    # Convert input to correct option if needed
    if options:
        try:
            choice = int(user_input)
            return question.get_option_by_index(choice)
        except:
            return user_input.strip()
    return user_input.strip()

# Run the quiz synchronously (if you use in the terminal)
result = quiz.execute(your_answer_provider)

# Show results
print(f"\nQuiz completed! Score: {result.score_percentage:.1f}%")
print(f"Correct answers: {result.correct_answers}/{result.total_questions}")
```

## Running Interactive Quizzes

Use the CLI for formatted output with timers and progress:

```python
from quizy import QuizCLI

# Run with timer display
QuizCLI.run_interactive(quiz, show_timer=True)

# Get detailed results breakdown
QuizCLI.display_detailed_results(result)
```

## Question Types

- **MultipleChoiceQuestion**: Single correct answer
- **MultipleSelectQuestion**: Select all correct answers (supports partial credit)
- **MatchingQuestion**: Match items to descriptions (supports partial credit)
- **TrueFalseQuestion**: Binary choice
- **ShortTextQuestion**: Free-form text answers

## Future Enhancements (v0.5+)

- Web-based UI components
- Database integration for result persistence
- Advanced analytics and reporting
- Real-time leaderboards
- Support for more AI providers (Claude, Gemini, etc.)
- More partial credit options
- Fine-tuning for domain-specific questions

## Support

GitHub: https://github.com/rustampy/quizy | Issues: https://github.com/rustampy/quizy/issues
