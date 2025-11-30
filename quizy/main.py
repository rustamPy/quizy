import sys
from . import quiz_101, quiz_102

def main():
    """Main CLI function"""
    print("\n🎯 Quiz CLI")
    print("=" * 50)
    print("Available quizzes:")
    print("  1. Python Basics (quiz_101)")
    print("  2. Data Structures (quiz_102)")
    print("=" * 50)
    
    try:
        choice = input("\nSelect quiz (1 or 2): ").strip()
        
        if choice == "1":
            quiz_101.start()
        elif choice == "2":
            quiz_102.start()
        else:
            print("Invalid choice!")
            sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        print("\n\nGoodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()