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

## Manual Questions

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

# Execute
result = quiz.execute(answer_provider=lambda q, idx: input(q.text + "\n> "))
print(f"Score: {result.score_percentage:.1f}%")
```

## AI-Generated Questions

Generate quiz questions automatically using OpenAI and test it on terminal using QuizCLI:

```python
import asyncio
from quizy import Quiz, QuizCLI
from quizy.ai_generator import AIQuestionGenerator
from quizy.core import QuestionType

async def my_quiz():
    # Initialize the AI question generator
    generator = AIQuestionGenerator()

    # Generate questions asynchronously
    questions = await generator.generate_questions_set_async(
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

    # Build the quiz
    quiz = Quiz(title="AI-Generated Python Quiz", time_limit=300)
    for q in questions:
        if q:
            quiz.add_question(q)
    return quiz

if __name__ == "__main__":
    quiz = asyncio.run(my_quiz())
    QuizCLI.run_interactive(quiz)

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
