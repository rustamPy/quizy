# Question Types

Quizy supports multiple question types for different assessment scenarios.

## Multiple Choice

Single answer from options.

```python
from quizy import MultipleChoiceQuestion

q = MultipleChoiceQuestion(
    text="What is the capital of France?",
    options=["London", "Berlin", "Paris", "Madrid"],
    correct_answer="Paris",
    explanation="Paris is the capital of France"
)
```

## Multiple Select

Multiple correct answers - user must select all correct ones.

```python
from quizy import MultipleSelectQuestion

q = MultipleSelectQuestion(
    text="Which are programming languages?",
    options=["Python", "JavaScript", "HTML", "CSS", "Java"],
    correct_answers=["Python", "JavaScript", "Java"],
    explanation="HTML and CSS are markup/style languages"
)
```

## Short Text

Free-form text input with flexible validation.

```python
from quizy import ShortTextQuestion

q = ShortTextQuestion(
    text="What year was Python created?",
    correct_answer="1991",
    case_sensitive=False,
    accepted_variations=["1991"],
    explanation="Python was created in 1991"
)
```

## True/False

Boolean questions with flexible input formats.

```python
from quizy import TrueFalseQuestion

q = TrueFalseQuestion(
    text="Python is interpreted.",
    correct_answer=True
)

# Accepts: True, "true", "yes", "y", "1", 1, etc.
q.check_answer("yes")  # True
q.check_answer("false")  # False
```

## Matching

Match items to corresponding pairs.

```python
from quizy import MatchingQuestion

q = MatchingQuestion(
    text="Match countries to capitals:",
    pairs={
        "France": "Paris",
        "Germany": "Berlin",
        "Italy": "Rome"
    }
)
```

## Complete Example

```python
from quizy import (
    Quiz,
    MultipleChoiceQuestion,
    MultipleSelectQuestion,
    ShortTextQuestion,
    TrueFalseQuestion,
    MatchingQuestion
)

quiz = Quiz("Assessment")

# Add different types
quiz.add_question(MultipleChoiceQuestion(...))
quiz.add_question(MultipleSelectQuestion(...))
quiz.add_question(ShortTextQuestion(...))
quiz.add_question(TrueFalseQuestion(...))
quiz.add_question(MatchingQuestion(...))

# Execute
result = quiz.execute(
    answer_provider=lambda q, idx: "answer"
)

print(f"Score: {result.score_percentage:.1f}%")
```
