# Quizy

## Overview

A lightweight, API-first Python quiz framework for creating interactive quizzes and assessments. Quizy provides a clean, extensible interface without prescriptive UI constraints, allowing you to build quiz applications that fit your specific needs.

- **Async/Await Support**: Non-blocking quiz execution with `execute_async()`
- **Live Timer Display**: Real-time countdown with visual feedback
- **Partial Credit System**: Award points for partially correct answers
- **Enhanced MatchingQuestion**: Answer shuffling and optional partial credit
- **Improved CLI**: Interactive formatting with progress indicators
- **Better Time Management**: Per-question and quiz-level time limits with countdown

## Important: Unified API

As of v0.3.0, all enhanced features are integrated directly into the core API. There are no separate "improved" modules:

```python
# Single unified import
from quizy import Quiz, MatchingQuestion, QuizCLI, TimerDisplay

# All features are available by default
quiz = Quiz(title="My Quiz", time_limit=60)
```

### 1. Async Quiz Execution

Execute quizzes asynchronously for non-blocking operations:

```python
from quizy import Quiz, MultipleChoiceQuestion, QuizCLI

quiz = Quiz(title="Async Quiz")
# ... add questions ...

# Run asynchronously
result = await quiz.execute_async(
    answer_provider=async_answer_provider,
    question_callback=async_question_callback
)
```

### 2. Enhanced MatchingQuestion

New options for better user experience:

```python
from quizy import MatchingQuestion

question = MatchingQuestion(
    text="Match items",
    pairs={"A": "Apple", "B": "Banana", "C": "Cherry"},
    shuffle_answers=True,        # NEW: Randomize answer options (default: True)
    allow_partial_credit=False,  # NEW: Award partial points (default: False)
    time_limit=15                # Time limit in seconds
)
```

**Partial Credit Calculation**:
- Full match: 100% credit
- Partial match: `correct_matches / total_pairs`
- Wrong selections: 0% credit

### 3. Partial Credit for MultipleSelectQuestion

Award partial credit for incomplete correct answers:

```python
from quizy import MultipleSelectQuestion

question = MultipleSelectQuestion(
    text="Select all correct answers",
    options=["A", "B", "C", "D"],
    correct_answers=["A", "B"],
    allow_partial_credit=True,  # NEW
    shuffle_options=True
)
```

### 4. Live Timer Display

Display countdown timers with visual feedback:

```python
from quizy import TimerDisplay

# Create a timer for a question
timer = TimerDisplay(duration=15)  # 15 seconds

# Check remaining time
remaining = timer.get_remaining()
time_string = timer.format_time(remaining)  # "00:05"

# Visual warning
warning = timer.get_warning_symbol()  # Returns ⚠️, ⏱️, or ✓
```

**Time Warning Indicators**:
- `✓ ` - Plenty of time (>30s remaining)
- `⏱️ ` - Getting short (10-30s remaining)
- `⚠️ ` - Running out (≤10s remaining)
- `❌` - Time expired

### 5. Enhanced Results with Metrics

New metrics in QuizResult:

```python
result = quiz.execute(answer_provider=provide_answer)

# New properties
print(f"Score: {result.score_percentage:.1f}%")           # Includes partial credit
print(f"Partial Answers: {result.partial_answers}")       # Count of partial credit
print(f"Avg Time/Question: {result.average_time_per_question:.1f}s")

# New in QuestionResult
for qr in result.question_results:
    print(f"Score: {qr.score}")      # 0.0 to 1.0 (0.5 for partial)
    print(f"Is Partial: {qr.is_partial}")
```

### 6. Question Shuffling

Shuffle options for variety and fairness:

```python
from quizy import MultipleChoiceQuestion

# Shuffle for this question
q1 = MultipleChoiceQuestion(
    text="What is 2+2?",
    options=["3", "4", "5"],
    correct_answer="4",
    shuffle_options=True
)

# Access shuffled display options
for opt in q1.display_options:
    print(opt)
```

### 7. Quiz Randomization

Randomize quiz question order:

```python
quiz = Quiz(
    title="My Quiz",
    randomize_order=True,  # Shuffle question order
    shuffle_options=True,  # Shuffle all question options
    show_progress=True     # Show progress indicator
)
```

## Enhanced CLI Features

### Interactive Formatting

The `QuizCLI` now provides:

- **Color-coded output**: Green for correct, red for incorrect, yellow for warnings
- **Visual status icons**: ✓, ✗, ◐, ⏱, ⊘ for different result types
- **Progress indicators**: Question numbering with remaining time
- **Better prompts**: Context-aware input requests

### Example Output

```
============================================================
Question 1/5 | ⏱️  15s
============================================================

What is the capital of France?

  1. London
  2. Berlin
  3. Paris
  4. Madrid

⏱️  Time remaining: 00:12
Your answer (1-4): 3

============================================================
  Results: Quiz Title
============================================================

Overall Performance:
  Total Questions:     5
  Correct Answers:     4
  Partial Answers:     1
  Score:               90.0%
  Time Taken:          00:34
  Avg Time/Question:   6.8s
```

### Running Interactive Quiz

```python
from quizy import QuizCLI

# With timer display
QuizCLI.run_interactive(quiz, show_timer=True)

# Async version
await QuizCLI.run_interactive_async(quiz, show_timer=True)
```

### Showing Detailed Results

```python
# Display breakdown for each question
QuizCLI.display_detailed_results(result)
```

## API Compatibility

### Unified Single API

v0.3.0 uses a single unified API. All enhanced features are directly integrated:

```python
# Single import source
from quizy import (
    Quiz,
    MultipleChoiceQuestion,
    MatchingQuestion,
    QuizCLI,
    TimerDisplay
)

# All features available by default
quiz = Quiz(title="My Quiz", time_limit=60)
```

## Performance Considerations

### Async vs Sync

**Use `execute()` when**:
- Simple synchronous answer providers
- No blocking I/O operations
- Standard quiz application

**Use `execute_async()` when**:
- Answer provider makes network calls
- Integrating with web servers (FastAPI, Django)
- Real-time quiz systems
- Complex async workflows

### Timer Overhead

Timer display has minimal overhead:
- Time checking: ~0.1ms per check
- Display formatting: ~0.5ms per update
- No separate threads needed (can be added for UI updates)

## Migration Guide

### From v0.2 to v0.3

1. **Questions still work the same**:
   ```python
   # v0.2
   q = MultipleChoiceQuestion(text="?", options=[...], correct_answer="...")
   
   # v0.3 - same, but can add new features
   q = MultipleChoiceQuestion(
       text="?",
       options=[...],
       correct_answer="...",
       shuffle_options=True  # NEW option
   )
   ```

2. **Add timer support gradually**:
   ```python
   # Add time_limit to existing questions
   q.time_limit = 15  # or in constructor
   ```


## Examples

### Complete Example: Timed Quiz with Async

```python
import asyncio
from quizy import (
    Quiz,
    MultipleChoiceQuestion,
    MatchingQuestion,
    QuizCLI
)

async def main():
    quiz = Quiz(
        title="Python Fundamentals",
        time_limit=120,  # 2 minutes total
        allow_skip=False,
        shuffle_options=True,
        randomize_order=True
    )
    
    # Add timed questions
    quiz.add_question(MultipleChoiceQuestion(
        text="What does OOP stand for?",
        options=["Object Oriented Programming", "Other Object Patterns", "Outer Object Procedure"],
        correct_answer="Object Oriented Programming",
        time_limit=10
    ))
    
    quiz.add_question(MatchingQuestion(
        text="Match methods to descriptions",
        pairs={
            "__init__": "Constructor",
            "__str__": "String representation",
            "__len__": "Length"
        },
        shuffle_answers=True,
        allow_partial_credit=False,  # Disable by default
        time_limit=20
    ))
    
    # Run async
    result = await quiz.execute_async(
        answer_provider=async_get_answer,
        question_callback=async_display_question
    )
    
    QuizCLI.display_result(result)

async def async_get_answer(question, idx):
    # Your async answer logic here
    return "answer"

async def async_display_question(question, idx, total):
    # Your async display logic here
    pass

# Run
asyncio.run(main())
```

## Known Limitations

1. **Terminal-based timer**: Countdown display works best in interactive terminals
2. **Async input**: Currently uses blocking `input()` - can be enhanced with `aioinput`
3. **Option shuffling**: Once shuffled, cannot be re-shuffled in same instance
4. **Partial credit**: Some question types (Short Text) don't support partial credit

## Future Enhancements

Planned for v0.4+:
- Web-based UI components
- Database integration for result persistence
- Advanced analytics and reporting
- Real-time leaderboards
- Ai-powered question generation
- More partial credit options

## Support & Contributions

For issues, feature requests, or contributions:
- GitHub: https://github.com/rustampy/quizy
- Issues: https://github.com/rustampy/quizy/issues
