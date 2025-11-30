# Usage Examples

## Basic Quiz

```python
from quizy import Quiz, MultipleChoiceQuestion, QuizCLI

# Create quiz
quiz = Quiz("Python Basics", allow_skip=True)

# Add questions
quiz.add_question(MultipleChoiceQuestion(
    text="What is 2 + 2?",
    options=["3", "4", "5"],
    correct_answer="4"
))

quiz.add_question(MultipleChoiceQuestion(
    text="Which is a Python keyword?",
    options=["class", "func", "function"],
    correct_answer="class"
))

# Run interactively
QuizCLI.run_interactive(quiz)
```

## Quiz with Timers

```python
from quizy import Quiz, MultipleChoiceQuestion, TimerManager

timer = TimerManager()
quiz = Quiz("Speed Challenge", time_limit=30.0)

quiz.add_question(MultipleChoiceQuestion(
    text="Q1?",
    options=["A", "B"],
    correct_answer="A",
    time_limit=10.0  # 10 seconds per question
))

def on_question(q, idx, total):
    timer.start_question(q.time_limit)
    print(f"{q.text} ({timer.get_question_remaining():.1f}s)")

timer.start_quiz(quiz.time_limit)
result = quiz.execute(
    answer_provider=lambda q, idx: input("Answer: "),
    question_callback=on_question
)

print(f"Score: {result.score_percentage:.1f}%")
```

## Programmatic Execution

```python
from quizy import Quiz, MultipleChoiceQuestion, TrueFalseQuestion

quiz = Quiz("Auto Quiz")
quiz.add_question(MultipleChoiceQuestion(
    text="Q1?", options=["A", "B"], correct_answer="A"
))
quiz.add_question(TrueFalseQuestion(
    text="Q2?", correct_answer=True
))

# Execute with predefined answers
answers = ["A", True]
answer_idx = [0]

def answer_provider(q, idx):
    answer = answers[answer_idx[0]]
    answer_idx[0] += 1
    return answer

result = quiz.execute(answer_provider=answer_provider)
print(f"Score: {result.score_percentage:.1f}%")
```

## Mixed Question Types

```python
from quizy import (
    Quiz,
    MultipleChoiceQuestion,
    MultipleSelectQuestion,
    ShortTextQuestion,
    TrueFalseQuestion,
    MatchingQuestion
)

quiz = Quiz("Comprehensive")

quiz.add_question(MultipleChoiceQuestion(
    text="Capital of France?",
    options=["London", "Paris", "Berlin"],
    correct_answer="Paris"
))

quiz.add_question(TrueFalseQuestion(
    text="Earth is round?",
    correct_answer=True
))

quiz.add_question(ShortTextQuestion(
    text="Spell 'hello':",
    correct_answer="hello",
    case_sensitive=False
))

quiz.add_question(MultipleSelectQuestion(
    text="Select vowels:",
    options=["A", "B", "E", "I"],
    correct_answers=["A", "E", "I"]
))

quiz.add_question(MatchingQuestion(
    text="Match capitals:",
    pairs={
        "France": "Paris",
        "Germany": "Berlin"
    }
))

result = quiz.execute(
    answer_provider=lambda q, idx: "A"  # Simplified
)
```

## Web API Integration

```python
from quizy import Quiz, MultipleChoiceQuestion
import json

def handle_quiz_submission(quiz_id, user_answers):
    # Load or create quiz
    quiz = Quiz("Assessment")
    quiz.add_question(MultipleChoiceQuestion(...))
    
    # Execute with user answers
    result = quiz.execute(
        answer_provider=lambda q, idx: user_answers[idx]
    )
    
    # Return JSON response
    return json.dumps(result.to_dict())
```

## Quiz with Callbacks

```python
from quizy import Quiz, MultipleChoiceQuestion, ResultStatus

quiz = Quiz("Quiz")
quiz.add_question(MultipleChoiceQuestion(
    text="Q1?", options=["A", "B"], correct_answer="A"
))

def on_question(q, idx, total):
    print(f"\n[Question {idx}/{total}]")
    print(q.text)

def on_result(q, idx, answer, status, time_taken):
    icon = "✓" if status == ResultStatus.CORRECT else "✗"
    print(f"{icon} {status.value} ({time_taken:.2f}s)")

result = quiz.execute(
    answer_provider=lambda q, idx: input("Answer: "),
    question_callback=on_question,
    result_callback=on_result
)

print(f"\nFinal Score: {result.score_percentage:.1f}%")
```

## Result Analysis

```python
result = quiz.execute(answer_provider=...)

# Overall stats
print(f"Score: {result.correct_answers}/{result.total_questions}")
print(f"Percentage: {result.score_percentage:.1f}%")
print(f"Time: {result.time_taken:.2f}s")

# Per-question breakdown
for q_result in result.question_results:
    print(f"Q{q_result.question_index + 1}: {q_result.status.value}")
    print(f"  Your answer: {q_result.user_answer}")
    print(f"  Time: {q_result.time_taken:.2f}s")

# Export as JSON
import json
json_data = json.dumps(result.to_dict(), indent=2)
```
