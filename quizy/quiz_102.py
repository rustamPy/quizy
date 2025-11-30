from .core import Quiz, Question

quiz_102 = Quiz("Data Structures - Quiz 102")

quiz_102.add_question(Question(
    text="Which data structure uses LIFO (Last In First Out)?",
    options=["Queue", "Stack", "List", "Dictionary"],
    correct_answer="Stack",
    explanation="A stack follows LIFO principle - the last element added is the first one removed"
))

quiz_102.add_question(Question(
    text="What is the time complexity of accessing an element in a dictionary by key?",
    options=["O(1)", "O(n)", "O(log n)", "O(n²)"],
    correct_answer="O(1)",
    explanation="Dictionary (hash table) lookup is O(1) on average"
))

quiz_102.add_question(Question(
    text="Which collection in Python does NOT allow duplicate values?",
    options=["list", "tuple", "set", "dict"],
    correct_answer="set",
    explanation="Sets automatically remove duplicates, storing only unique values"
))