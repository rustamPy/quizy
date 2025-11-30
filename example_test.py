from quizy import Quiz, MatchingQuestion, MultipleChoiceQuestion, QuizCLI, TimerDisplay


q = Quiz(title="Sample", allow_skip=True)

q.add_question(
    MatchingQuestion(
        text="In which years were the following programming languages created?",
        pairs={"Python": "1991", "Java": "1995", "C": "1972"},
        time_limit=20,
        metadata={"prompt_key": "created in"},
        allow_partial_credit=True
    )
)

q.add_questions(
    questions=[
        MultipleChoiceQuestion(
            text="Who is your daddy?",
            options=["Bio Daddy", "Your daddy"],
            correct_answer="Bio Daddy",
            time_limit=10
        )
    ]
)

if __name__ == "__main__":
    QuizCLI.run_interactive(q)
