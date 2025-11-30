# Quizy

A lightweight, API-first Python quiz framework for creating interactive quizzes and assessments. Quizy provides a clean, extensible interface without prescriptive UI constraints, allowing you to build quiz applications that fit your specific needs.

## Features

- Multiple Question Types: Multiple choice, multiple select, short text, true/false, and matching questions
- Flexible API: Built as a library, not a full application—you control the presentation layer
- Timer Support: Per-question and quiz-level time limits with countdown tracking
- Result Tracking: Comprehensive quiz results with scoring, skipped questions, and timeout metrics
- Type Hints: Full type hint support for IDE autocomplete and validation
- No External Dependencies: Pure Python implementation (Python 3.8+)

## Quick Start

```python
from quizy import MultipleChoiceQuestion, Quiz

# Create a question
question = MultipleChoiceQuestion(
    text="What is the capital of France?",
    options=["Paris", "London", "Berlin"],
    correct_option=0
)

# Create and run a quiz
quiz = Quiz(questions=[question])
result = quiz.run(answer_provider=lambda q: 0)

print(f"Score: {result.score_percentage}%")
```

## Documentation

Complete documentation is available in the docs folder:

- [Question Types Guide](https://github.com/rustamPy/quizy/blob/main/docs/QUESTION_TYPES.md) - All supported question types with code examples
- [Usage Examples](https://github.com/rustamPy/quizy/blob/main/docs/EXAMPLES.md) - Real-world examples including timers, callbacks, and web integration
- [API Reference](https://github.com/rustamPy/quizy/blob/main/docs/API.md) - Complete API documentation with constructors and methods

## Installation

```bash
pip install -r requirements.txt
```

## Running Examples

Try the included example quizzes:

```bash
python -m quizy.quiz_101
python -m quizy.quiz_102
```

## Running Tests

```bash
pytest tests/
```

## License

MIT
