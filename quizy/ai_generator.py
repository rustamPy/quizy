import os
import json
from typing import List, Dict, Any, Optional, Union
import asyncio

from openai import OpenAI, AsyncOpenAI
from quizy.core import (
    MultipleChoiceQuestion,
    TrueFalseQuestion,
    ShortTextQuestion,
    MultipleSelectQuestion,
    MatchingQuestion,
    Question,
    QuestionType,
)


class AIQuestionGenerator:
    """Generate quiz questions using OpenAI's API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",  # default
        temperature: float = 0.9,
    ):
        """
        Initialize the AI question generator

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env variable)
            model: OpenAI model to use (default: gpt-4o-mini)
            temperature: Temperature for generation (0.0-1.0, higher = more creative)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter"
            )

        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
        self.temperature = temperature

    def generate_questions_set(
        self,
        topic: str,
        num_questions: int = 5,
        question_types: Optional[List[QuestionType]] = None,
        difficulty: str = "medium",
        context: Optional[str] = None,
    ) -> List[Question]:
        """
        Generate multiple questions for a quiz synchronously.

        Internally uses async but runs synchronously for ease of use.

        Args:
            topic: Topic for all questions
            num_questions: Number of questions to generate
            question_types: Types of questions (cycles through if provided)
            difficulty: Difficulty level (easy, medium, hard)
            context: Optional context/reading material

        Returns:
            List of generated Question objects
        """
        return asyncio.run(
            self.generate_questions_set_async(
                topic=topic,
                num_questions=num_questions,
                question_types=question_types,
                difficulty=difficulty,
                context=context,
            )
        )

    def generate_question(
        self,
        topic: str,
        question_type: Union[QuestionType, str] = QuestionType.MULTIPLE_CHOICE,
        difficulty: str = "medium",
        num_options: int = 4,
        time_limit: int = 20,
        context: Optional[str] = None,
    ) -> Optional[Question]:
        """
        Generate a single question synchronously.

        Internally uses async but runs synchronously for ease of use.

        Args:
            topic: Topic for the question
            question_type: Type of question to generate
            difficulty: Difficulty level (easy, medium, hard)
            num_options: Number of options for multiple choice
            time_limit: Optional time limit for question in seconds
            context: Optional context/reading material

        Returns:
            Generated Question object or None if generation fails
        """
        return asyncio.run(
            self.generate_question_async(
                topic=topic,
                question_type=question_type,
                difficulty=difficulty,
                num_options=num_options,
                time_limit=time_limit,
                context=context,
            )
        )

    async def generate_question_async(
        self,
        topic: str,
        question_type: Union[QuestionType, str] = QuestionType.MULTIPLE_CHOICE,
        difficulty: str = "medium",
        num_options: int = 4,
        time_limit: int = 20,
        context: Optional[str] = None,
    ) -> Optional[Question]:
        """Generate a single question asynchronously (internal)"""
        if isinstance(question_type, str):
            type_str = question_type.upper()
            if type_str == "SHORT_ANSWER":
                type_str = "SHORT_TEXT"
            question_type = QuestionType[type_str]

        prompt = self._create_prompt(
            topic, question_type, difficulty, num_options, context
        )

        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )

            content = response.choices[0].message.content
            question_data = json.loads(content)

            return self._parse_question_data(question_data, question_type, time_limit)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error parsing AI response: {e}")
            return None

    async def generate_questions_set_async(
        self,
        topic: str,
        num_questions: int = 5,
        question_types: Optional[List[QuestionType]] = None,
        difficulty: str = "medium",
        context: Optional[str] = None,
    ) -> List[Question]:
        """Generate multiple questions for a quiz asynchronously (internal)"""
        if question_types is None:
            question_types = [QuestionType.MULTIPLE_CHOICE]

        tasks = []
        for i in range(num_questions):
            qtype = question_types[i % len(question_types)]
            task = self.generate_question_async(
                topic, qtype, difficulty, context=context
            )
            tasks.append(task)

        return await asyncio.gather(*tasks)

    def _create_prompt(
        self,
        topic: str,
        question_type: QuestionType,
        difficulty: str = "medium",
        num_options: int = 4,
        context: Optional[str] = None,
    ) -> str:
        """Create a prompt for question generation"""

        # Map SHORT_TEXT to "short answer" for prompt
        type_display = (
            "short answer"
            if question_type == QuestionType.SHORT_TEXT
            else question_type.value.replace("_", " ")
        )
        base_prompt = f"""Generate a {difficulty} difficulty {type_display} question about: {topic}"""

        if context:
            base_prompt += f"\n\nContext: {context}"

        if question_type == QuestionType.MULTIPLE_CHOICE:
            return f"""{base_prompt}

Return a JSON object with the following structure:
{{
    "question": "The question text",
    "options": should contain {num_options} options and options should be array e.g. ["option1", "option2", ..., "optionN"],
    "correct_answer": "correct option",
    "explanation": "Why this is the correct answer"
}}

Ensure options are plausible but clearly distinguishable. Return only valid JSON."""

        elif question_type == QuestionType.TRUE_FALSE:
            return f"""{base_prompt}

Return a JSON object with the following structure:
{{
    "question": "The statement to evaluate as true or false",
    "correct_answer": true,
    "explanation": "Why this statement is true/false"
}}

Return only valid JSON."""

        elif question_type == QuestionType.SHORT_TEXT:
            return f"""{base_prompt}

Return a JSON object with the following structure:
{{
    "question": "The question text",
    "correct_answer": "The expected answer",
    "acceptable_variations": ["alternative answer 1", "alternative answer 2"],
    "explanation": "Explanation of the answer"
}}

Return only valid JSON."""

        elif question_type == QuestionType.MULTIPLE_SELECT:
            return f"""{base_prompt}

Return a JSON object with the following structure:
{{
    "question": "The question text (should ask to select all correct answers)",
    "options": ["option1", "option2", "option3", "option4", "option5"],
    "correct_answers": ["correct1", "correct2"],
    "explanation": "Why these are the correct answers"
}}

Ensure at least 2 correct answers and 2 incorrect options. Return only valid JSON."""

        elif question_type == QuestionType.MATCHING:
            return f"""{base_prompt}

Return a JSON object with the following structure:
{{
    "question": "Matching question prompt",
    "pairs": {{
        "item1": "match1",
        "item2": "match2",
        "item3": "match3"
    }},
    "explanation": "Explanation of the matches"
}}

Ensure 3-5 pairs of logically related items. Return only valid JSON."""

        return base_prompt

    @staticmethod
    def _parse_question_data(
        data: Dict[str, Any],
        question_type: QuestionType,
        time_limit: int,
    ) -> Optional[Question]:
        """Parse AI response data into Question objects"""

        try:
            if question_type == QuestionType.MULTIPLE_CHOICE:
                return MultipleChoiceQuestion(
                    text=data["question"],
                    options=data["options"],
                    correct_answer=data["correct_answer"],
                    explanation=data.get("explanation"),
                    time_limit=time_limit,
                )

            elif question_type == QuestionType.TRUE_FALSE:
                return TrueFalseQuestion(
                    text=data["question"],
                    correct_answer=data["correct_answer"],
                    explanation=data.get("explanation"),
                )

            elif question_type == QuestionType.SHORT_TEXT:
                return ShortTextQuestion(
                    text=data["question"],
                    correct_answer=data["correct_answer"],
                    explanation=data.get("explanation"),
                    time_limit=time_limit,
                )

            elif question_type == QuestionType.MULTIPLE_SELECT:
                return MultipleSelectQuestion(
                    text=data["question"],
                    options=data["options"],
                    correct_answers=data["correct_answers"],
                    explanation=data.get("explanation"),
                    time_limit=time_limit,
                )

            elif question_type == QuestionType.MATCHING:
                return MatchingQuestion(
                    text=data["question"],
                    pairs=data["pairs"],
                    explanation=data.get("explanation"),
                    time_limit=time_limit,
                )

        except (KeyError, TypeError, ValueError) as e:
            print(f"Error creating question from AI data: {e}")
            return None

        return None
