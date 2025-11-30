# API Reference

## Question Classes

### MultipleChoiceQuestion

Single answer from options.

```python
MultipleChoiceQuestion(
    text: str,
    options: List[str],
    correct_answer: str,
    explanation: Optional[str] = None,
    time_limit: Optional[float] = None,
    metadata: Optional[Dict] = None
)
```

**Methods:**
- `check_answer(answer: str) -> bool`
- `get_options() -> List[str]`
- `get_option_by_index(index: int) -> Optional[str]`

### MultipleSelectQuestion

Multiple correct answers required.

```python
MultipleSelectQuestion(
    text: str,
    options: List[str],
    correct_answers: List[str],  # Min 2
    explanation: Optional[str] = None,
    time_limit: Optional[float] = None,
    metadata: Optional[Dict] = None
)
```

**Methods:**
- `check_answer(answer: List[str]) -> bool`
- `get_options() -> List[str]`

### ShortTextQuestion

Free-form text with flexible validation.

```python
ShortTextQuestion(
    text: str,
    correct_answer: str,
    explanation: Optional[str] = None,
    time_limit: Optional[float] = None,
    metadata: Optional[Dict] = None,
    case_sensitive: bool = False,
    accepted_variations: Optional[List[str]] = None
)
```

**Methods:**
- `check_answer(answer: str) -> bool`

### TrueFalseQuestion

Boolean statement.

```python
TrueFalseQuestion(
    text: str,
    correct_answer: bool,
    explanation: Optional[str] = None,
    time_limit: Optional[float] = None,
    metadata: Optional[Dict] = None
)
```

**Methods:**
- `check_answer(answer: Any) -> bool`

Accepts: `True`, `"true"`, `"yes"`, `1`, etc.

### MatchingQuestion

Match items to pairs.

```python
MatchingQuestion(
    text: str,
    pairs: Dict[str, str],  # Min 2 pairs
    explanation: Optional[str] = None,
    time_limit: Optional[float] = None,
    metadata: Optional[Dict] = None
)
```

**Methods:**
- `check_answer(answer: Dict[str, str]) -> bool`
- `get_options() -> Dict[str, List[str]]`

## Quiz Class

```python
Quiz(
    title: str,
    questions: Optional[List[Question]] = None,
    time_limit: Optional[float] = None,
    allow_skip: bool = False,
    shuffle_options: bool = False,
    randomize_order: bool = False
)
```

**Methods:**
- `add_question(question: Question) -> None`
- `add_questions(questions: List[Question]) -> None`
- `remove_question(index: int) -> None`
- `get_questions() -> List[Question]`
- `get_question_count() -> int`
- `get_result() -> Optional[QuizResult]`
- `clear() -> None`
- `execute(answer_provider, result_callback=None, question_callback=None) -> QuizResult`
- `validate() -> Tuple[bool, List[str]]`

## Result Classes

### QuestionResult

```python
@dataclass
class QuestionResult:
    question_index: int
    user_answer: str
    correct_answer: str
    status: ResultStatus
    time_taken: float
    
    @property
    def is_correct(self) -> bool
```

### QuizResult

```python
@dataclass
class QuizResult:
    title: str
    total_questions: int
    correct_answers: int
    time_taken: float
    question_results: List[QuestionResult]
    
    @property
    def score_percentage(self) -> float
    
    @property
    def skipped_count(self) -> int
    
    @property
    def timeout_count(self) -> int
    
    def to_dict(self) -> Dict[str, Any]
```

### ResultStatus

```python
class ResultStatus(Enum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"
```

## Helper Classes

### QuizCLI

Terminal-based quiz utilities.

**Static Methods:**
- `display_question(question, num, total) -> None`
- `get_answer(question, allow_skip=False) -> Optional[str]`
- `display_result(result) -> None`
- `display_detailed_results(result) -> None`
- `run_interactive(quiz) -> None`

### TimerManager

```python
timer = TimerManager()
timer.start_quiz(time_limit=60.0)
timer.start_question(time_limit=10.0)
timer.get_quiz_elapsed() -> float
timer.get_question_elapsed() -> float
timer.get_quiz_remaining() -> Optional[float]
timer.get_question_remaining() -> Optional[float]
timer.is_quiz_timeout() -> bool
timer.is_question_timeout() -> bool
```

## QuestionType Enum

```python
class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_ANSWER = "single_answer"
    MULTIPLE_SELECT = "multiple_select"
    SHORT_TEXT = "short_text"
    MATCHING = "matching"
    TRUE_FALSE = "true_false"
```
