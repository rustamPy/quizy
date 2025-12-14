# MCP Server Setup Guide

## What is the MCP Server?

The MCP (Model Context Protocol) server allows AI assistants GitHub Copilot to directly interact with Quizy. Instead of just reading code, AI can:

- **Generate quizzes** on any topic
- **Validate questions** for quality
- **Analyze difficulty** of question sets
- **Create quiz objects** programmatically


## Install MCP Dependencies

```bash
pip install quizy[mcp]
```

## Integration with GitHub Copilot (VS Code)

### 1. Install Copilot Chat Extension

In VS Code, install "GitHub Copilot Chat" extension.

### 2. Create `.copilot/mcp-server.json`

```json
{
  "mcpServers": {
    "quizy": {
      "command": "python",
      "args": ["-m", "quizy.mcp_server"],
      "env": {
        "PYTHONPATH": "/path/to/quizy"
      }
    }
  }
}
```

### 3. Use in Chat

```
@quizy Generate a Python quiz with 5 hard questions
```

---

## Available Tools

### 1. `generate_quiz`
Generate AI-powered quiz questions.

**Parameters:**
- `topic` (required): Subject to generate questions about
- `num_questions`: Number of questions (default: 5)
- `difficulty`: "easy", "medium", or "hard"
- `question_types`: List of question types

**Example:**
```
Topic: Python Async Programming
Num Questions: 5
Difficulty: hard
Question Types: MULTIPLE_CHOICE, TRUE_FALSE, SHORT_TEXT
```

### 2. `validate_question`
Check a question for quality issues.

**Parameters:**
- `question_text`: The question
- `question_type`: Type of question
- `options`: Answer choices (for choice questions)
- `correct_answer`: The correct answer
- `pairs`: Item pairs (for matching)

**Returns:**
- List of issues found
- Quality score (0-100)

### 3. `create_quiz_from_questions`
Create a quiz object from questions.

**Parameters:**
- `title`: Quiz name
- `questions_json`: JSON from generate_quiz
- `time_limit`: Total time in seconds
- `shuffle_options`: Randomize options

### 4. `analyze_difficulty`
Analyze question distribution and difficulty.

**Parameters:**
- `questions_json`: JSON question set

**Returns:**
- Type distribution
- Recommendations

---

## Usage Examples

### VS Code Copilot Chat

```
@quizy Create a hard Python quiz with 5 questions covering async/await concepts
```

Copilot will:
1. Call `generate_quiz`
2. Validate the questions with `validate_question`
3. Create the quiz with `create_quiz_from_questions`
4. Show you a formatted quiz ready to use

---

## Advanced Usage

### Multi-Step Quiz Generation

```
1. Generate 5 questions about Docker
2. Validate each question for quality
3. If any issues found, regenerate that question
4. Create a final quiz object
```

---

For issues: https://github.com/rustampy/quizy/issues
