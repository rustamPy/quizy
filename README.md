# Quizy 🎯

**A simple, elegant Python framework for creating and running interactive quizzes**

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Quizy makes it incredibly easy to create educational quizzes, assessments, and interactive learning experiences in Python. Whether you're a teacher, student, or developer, Quizy provides a clean API for building engaging quiz applications.

## ✨ Features

- 🚀 **Simple API** - Create quizzes in just a few lines of code
- 📝 **Interactive CLI** - Built-in command-line interface for running quizzes
- 🎨 **Customizable** - Add explanations, customize questions, and build complex quizzes
- 🔌 **Extensible** - Easy to integrate into your own applications
- 📦 **Zero Dependencies** - Pure Python, no external packages required
- ✅ **Type-Safe** - Clean, well-documented code with proper error handling

## 🚀 Quick Start

### Installation

```bash
pip install quizy
```

Or install from source:

```bash
git clone https://github.com/rustampy/quizy.git
cd quizy
pip install -e .
```

### Your First Quiz in 30 Seconds

```python
import quizy as q

# Use a built-in quiz
quiz_101 = q.quiz_101
quiz_101.start()
```

That's it! You'll get an interactive quiz experience right in your terminal.

## 📖 Usage Guide

### Using Built-in Quizzes

Quizy comes with sample quizzes to get you started:

```python
import quizy as q

# Python Basics Quiz
quiz_101 = q.quiz_101
quiz_101.start()

# Data Structures Quiz
quiz_102 = q.quiz_102
quiz_102.start()
```

### Creating Custom Quizzes

Build your own quizzes with the `Quiz` and `Question` classes:

```python
from quizy import Quiz, Question

# Create a new quiz
geography_quiz = Quiz("World Geography Challenge")

# Add questions with multiple choice options
geography_quiz.add_question(Question(
    text="What is the capital of France?",
    options=["London", "Berlin", "Paris", "Madrid"],
    correct_answer="Paris",
    explanation="Paris has been the capital of France since the 12th century"
))

geography_quiz.add_question(Question(
    text="Which is the largest ocean?",
    options=["Atlantic", "Indian", "Arctic", "Pacific"],
    correct_answer="Pacific",
    explanation="The Pacific Ocean covers about 63 million square miles"
))

# Start the quiz
geography_quiz.start()
```

### Advanced Example: Programming Quiz

```python
from quizy import Quiz, Question

# Create a coding quiz
coding_quiz = Quiz("Python Programming Quiz")

# Add technical questions
coding_quiz.add_question(Question(
    text="What is the time complexity of list.append() in Python?",
    options=["O(1)", "O(log n)", "O(n)", "O(n²)"],
    correct_answer="O(1)",
    explanation="List append is amortized O(1) due to dynamic array implementation"
))

coding_quiz.add_question(Question(
    text="Which keyword is used to create a generator in Python?",
    options=["return", "yield", "generate", "async"],
    correct_answer="yield",
    explanation="The yield keyword creates a generator that can pause and resume execution"
))

coding_quiz.add_question(Question(
    text="What does the __init__ method do in Python classes?",
    options=[
        "Deletes an object",
        "Initializes a new instance",
        "Imports a module",
        "Defines a static method"
    ],
    correct_answer="Initializes a new instance",
    explanation="__init__ is the constructor method called when creating new class instances"
))

# Run the quiz
coding_quiz.start()
```

### Working with Quiz Data Programmatically

```python
from quizy import Quiz, Question

# Create a quiz
my_quiz = Quiz("Math Quiz")
my_quiz.add_question(Question(
    text="What is 12 × 15?",
    options=["150", "180", "200", "175"],
    correct_answer="180"
))

# Inspect quiz contents
print(f"Title: {my_quiz.title}")
print(f"Questions: {len(my_quiz.get_questions())}")

# Iterate through questions
for i, question in enumerate(my_quiz.get_questions(), 1):
    print(f"{i}. {question.text}")
    print(f"   Answer: {question.correct_answer}")
```

### CLI Usage

After installation, run quizzes directly from your terminal:

```bash
quizy
```

This launches an interactive menu where you can select from available quizzes.

## 📚 API Reference

### `Question`

Creates a single quiz question with multiple choice answers.

```python
Question(text, options, correct_answer, explanation=None)
```

**Parameters:**
- `text` (str): The question text
- `options` (list): List of possible answers (strings)
- `correct_answer` (str): The correct answer (must be in options)
- `explanation` (str, optional): Explanation shown after answering

**Methods:**
- `check_answer(user_answer)` - Returns True if the answer is correct

**Example:**
```python
q = Question(
    text="What is 2 + 2?",
    options=["3", "4", "5", "6"],
    correct_answer="4",
    explanation="Basic arithmetic: 2 plus 2 equals 4"
)
```

### `Quiz`

Creates a quiz containing multiple questions.

```python
Quiz(title, questions=None)
```

**Parameters:**
- `title` (str): Quiz title displayed to users
- `questions` (list, optional): Initial list of Question objects

**Methods:**
- `add_question(question)` - Add a Question to the quiz
- `start()` - Launch interactive quiz session
- `get_questions()` - Return list of all questions
- `clear()` - Remove all questions and reset score

**Attributes:**
- `title` - Quiz title
- `questions` - List of Question objects
- `score` - Current score (after running quiz)
- `total` - Total number of questions

**Example:**
```python
quiz = Quiz("Science Quiz")
quiz.add_question(Question(...))
quiz.add_question(Question(...))
quiz.start()  # Runs interactively

print(f"Final Score: {quiz.score}/{quiz.total}")
```

## 🏗️ Project Structure

```
quizy/
├── pyproject.toml       # Package configuration
├── README.md            # This file
├── LICENSE              # MIT License
└── quizy/
    ├── __init__.py      # Package exports
    ├── core.py          # Quiz and Question classes
    ├── quiz_101.py      # Sample: Python Basics
    ├── quiz_102.py      # Sample: Data Structures
    └── main.py          # CLI entry point
```

## 🛠️ Development

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/rustampy/quizy.git
cd quizy

# Install in editable mode
pip install -e .

# Test your changes
python -c "import quizy; print(quizy.__version__)"
```

### Building the Package

```bash
# Install build tools
pip install build

# Build distribution packages
python -m build

# Output: dist/quizy-0.1.0.tar.gz and dist/quizy-0.1.0-py3-none-any.whl
```

### Publishing to PyPI

```bash
# Install twine
pip install twine

# Upload to PyPI (requires PyPI account)
twine upload dist/*

# Or upload to TestPyPI first
twine upload --repository testpypi dist/*
```

## 🎓 Use Cases

- **Education**: Create interactive learning materials for students
- **Training**: Build corporate training quizzes and assessments
- **Interviews**: Develop technical screening questions
- **Self-Study**: Create personal study aids for exam preparation
- **Gamification**: Add quiz elements to your applications

## 🤝 Contributing

Contributions are welcome! Here are some ways you can help:

- 🐛 Report bugs and issues
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit pull requests

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

Built with ❤️ for educators, students, and developers who believe in the power of interactive learning.

---

**Happy Quizzing! 🎉**

For questions, issues, or suggestions, please visit [GitHub Issues](https://github.com/rustampy/quizy/issues).