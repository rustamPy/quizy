from .core import Quiz, Question

quiz_101 = Quiz("Python Basics - Quiz 101")

quiz_101.add_question(Question(
    text="What is the output of: print(2 ** 3)?",
    options=["6", "8", "9", "23"],
    correct_answer="8",
    explanation="The ** operator is exponentiation. 2^3 = 8"
))

quiz_101.add_question(Question(
    text="Which data type is mutable in Python?",
    options=["tuple", "string", "list", "int"],
    correct_answer="list",
    explanation="Lists are mutable, meaning you can change their contents after creation"
))

quiz_101.add_question(Question(
    text="What keyword is used to create a function in Python?",
    options=["func", "function", "def", "define"],
    correct_answer="def",
    explanation="The 'def' keyword is used to define functions in Python"
))

quiz_101.add_question(Question(
    text="What is the correct way to start a for loop in Python?",
    options=[
        "for i in range(5):",
        "for (i = 0; i < 5; i++)",
        "foreach i in range(5):",
        "for i = 0 to 5:"
    ],
    correct_answer="for i in range(5):",
    explanation="Python uses 'for variable in iterable:' syntax"
))