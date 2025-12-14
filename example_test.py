from quizy import Quiz, MatchingQuestion, MultipleChoiceQuestion, QuizCLI
from quizy.ai_generator import AIQuestionGenerator
from quizy.core import QuestionType

custom_quiz = Quiz(title="Sample", allow_skip=True)
ai_generator = AIQuestionGenerator()


custom_quiz.add_questions(
    questions=[
        MatchingQuestion(
            text="In which years were the following programming languages created?",
            pairs={"Python": "1991", "Java": "1995", "C": "1972"},
            time_limit=20,
            metadata={"prompt_key": "created in"},
            allow_partial_credit=True,
        ),
        ai_generator.generate_question(
            topic="jane eyre",
            question_type=QuestionType.MATCHING,
            time_limit=60,
            context="About the book",
        ),
    ]
)


if __name__ == "__main__":
    QuizCLI.run_interactive(custom_quiz, show_timer=True)
