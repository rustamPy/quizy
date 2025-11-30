"""
Core quizy functionality
"""

class Question:
    """Represents a single quiz question"""
    
    def __init__(self, text, options, correct_answer, explanation=None):
        """
        Args:
            text: The question text
            options: List of possible answers
            correct_answer: The correct answer (must be in options)
            explanation: Optional explanation for the answer
        """
        self.text = text
        self.options = options
        self.correct_answer = correct_answer
        self.explanation = explanation
        
        if correct_answer not in options:
            raise ValueError("Correct answer must be one of the options")
    
    def check_answer(self, user_answer):
        """Check if the user's answer is correct"""
        return user_answer == self.correct_answer


class Quiz:
    """A quiz containing multiple questions"""
    
    def __init__(self, title, questions=None):
        """
        Args:
            title: Quiz title
            questions: List of Question objects
        """
        self.title = title
        self.questions = questions or []
        self.score = 0
        self.total = 0
    
    def add_question(self, question):
        """Add a question to the quiz"""
        if not isinstance(question, Question):
            raise TypeError("Must be a Question instance")
        self.questions.append(question)
    
    def start(self):
        """Start the quiz interactively"""
        print(f"\n{'='*50}")
        print(f"  {self.title}")
        print(f"{'='*50}\n")
        
        if not self.questions:
            print("No questions available!")
            return
        
        self.score = 0
        self.total = len(self.questions)
        
        for i, q in enumerate(self.questions, 1):
            print(f"Question {i}/{self.total}:")
            print(f"{q.text}\n")
            
            for idx, opt in enumerate(q.options, 1):
                print(f"  {idx}. {opt}")
            
            while True:
                try:
                    answer_idx = input("\nYour answer (enter number): ").strip()
                    answer_idx = int(answer_idx) - 1
                    
                    if 0 <= answer_idx < len(q.options):
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(q.options)}")
                except ValueError:
                    print("Please enter a valid number")
                except (KeyboardInterrupt, EOFError):
                    print("\n\nQuiz interrupted!")
                    return
            
            user_answer = q.options[answer_idx]
            
            if q.check_answer(user_answer):
                print("✓ Correct!")
                self.score += 1
            else:
                print(f"✗ Wrong! The correct answer was: {q.correct_answer}")
            
            if q.explanation:
                print(f"💡 {q.explanation}")
            
            print()
        
        print(f"{'='*50}")
        print(f"Final Score: {self.score}/{self.total} ({self.score/self.total*100:.1f}%)")
        print(f"{'='*50}\n")
    
    def get_questions(self):
        """Return all questions"""
        return self.questions
    
    def clear(self):
        """Clear all questions"""
        self.questions = []
        self.score = 0
        self.total = 0