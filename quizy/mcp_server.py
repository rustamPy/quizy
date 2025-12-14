"""
MCP Server for Quizy - Exposes quiz functionality to AI assistants
"""

import asyncio
import json
import logging

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server("quizy-server")

try:
    from quizy.core import QuestionType
    from quizy.ai_generator import AIQuestionGenerator
except ImportError as e:
    logger.error(f"Failed to import Quizy modules: {e}")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="generate_quiz",
            description="Generate a quiz using AI on a given topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic for questions"},
                    "num_questions": {"type": "integer", "description": "Number of questions (default 5)"},
                    "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"], "description": "Difficulty level"},
                    "question_types": {"type": "array", "description": "Question types to generate"}
                },
                "required": ["topic"]
            }
        ),
        types.Tool(
            name="validate_question",
            description="Validate a question for quality issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "question_text": {"type": "string"},
                    "question_type": {"type": "string"},
                    "options": {"type": "array"},
                    "correct_answer": {"type": "string"},
                    "pairs": {"type": "object"}
                },
                "required": ["question_text", "question_type"]
            }
        ),
        types.Tool(
            name="create_quiz_from_questions",
            description="Create a quiz object from questions",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "questions_json": {"type": "string"},
                    "time_limit": {"type": "integer"},
                    "shuffle_options": {"type": "boolean"}
                },
                "required": ["title", "questions_json"]
            }
        ),
        types.Tool(
            name="analyze_difficulty",
            description="Analyze question difficulty distribution",
            inputSchema={
                "type": "object",
                "properties": {"questions_json": {"type": "string"}},
                "required": ["questions_json"]
            }
        )
    ]


@server.call_tool()
async def handle_generate_quiz(topic: str, num_questions: int = 5, difficulty: str = "medium", question_types: list = None) -> list[types.TextContent]:
    if not topic or not topic.strip():
        return [types.TextContent(type="text", text=json.dumps({"error": "Topic cannot be empty"}))]

    if question_types is None:
        question_types = [
            QuestionType.MULTIPLE_CHOICE,
            QuestionType.TRUE_FALSE,
            QuestionType.MULTIPLE_SELECT,
            QuestionType.SHORT_TEXT,
        ]

    try:
        generator = AIQuestionGenerator()
        questions = await generator.generate_questions_set_async(topic=topic, num_questions=num_questions, question_types=question_types, difficulty=difficulty)

        questions_data = []
        for q in questions:
            q_dict = {"text": q.text, "type": q.__class__.__name__, "time_limit": getattr(q, "time_limit", None)}
            if hasattr(q, "options"):
                q_dict["options"] = q.options
            if hasattr(q, "correct_answer"):
                q_dict["correct_answer"] = q.correct_answer
            if hasattr(q, "correct_answers"):
                q_dict["correct_answers"] = q.correct_answers
            if hasattr(q, "pairs"):
                q_dict["pairs"] = q.pairs
            questions_data.append(q_dict)

        result = {"topic": topic, "num_questions": len(questions_data), "difficulty": difficulty, "questions": questions_data}
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]


@server.call_tool()
async def validate_question(question_text: str, question_type: str, options: list = None, correct_answer: str = None, pairs: dict = None) -> list[types.TextContent]:
    issues = []

    if not question_text or len(question_text.strip()) < 10:
        issues.append("Question text too short (minimum 10 characters)")

    if question_type == "MULTIPLE_CHOICE":
        if not options or len(options) < 2:
            issues.append("Need at least 2 options")
        if not correct_answer:
            issues.append("Correct answer required")
        elif correct_answer not in options:
            issues.append("Correct answer must be in options")

    elif question_type == "TRUE_FALSE":
        if correct_answer not in ["True", "False", "true", "false"]:
            issues.append("Answer must be True or False")

    elif question_type == "MATCHING":
        if not pairs or len(pairs) < 2:
            issues.append("Need at least 2 pairs")

    result = {"valid": len(issues) == 0, "issues": issues, "score": max(0, 100 - len(issues) * 20)}
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


@server.call_tool()
async def create_quiz_from_questions(title: str, questions_json: str, time_limit: int = None, shuffle_options: bool = False) -> list[types.TextContent]:
    try:
        questions_data = json.loads(questions_json)
        result = {
            "title": title,
            "time_limit": time_limit,
            "shuffle_options": shuffle_options,
            "num_questions": len(questions_data),
            "questions_summary": [{"text": q.get("text", ""), "type": q.get("type", "")} for q in questions_data],
            "ready_to_execute": True
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    except json.JSONDecodeError:
        return [types.TextContent(type="text", text=json.dumps({"error": "Invalid JSON format"}))]
    except Exception as e:
        logger.error(f"Error creating quiz: {e}")
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]


@server.call_tool()
async def analyze_difficulty(questions_json: str) -> list[types.TextContent]:
    try:
        questions_data = json.loads(questions_json)
        type_count = {}
        for q in questions_data:
            q_type = q.get("type", "Unknown")
            type_count[q_type] = type_count.get(q_type, 0) + 1

        recommendations = ["Good mix of question types" if len(type_count) >= 3 else "Consider adding more variety in question types"]

        result = {"total_questions": len(questions_data), "type_distribution": type_count, "recommendations": recommendations}
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        logger.error(f"Error analyzing difficulty: {e}")
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    logger.info("Quizy MCP Server starting...")
    logger.info("Available tools: generate_quiz, validate_question, create_quiz_from_questions, analyze_difficulty")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, asyncio.get_event_loop())


if __name__ == "__main__":
    asyncio.run(main())
