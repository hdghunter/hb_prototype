"""
Main script to run the 2Pillz battle game.
This script serves as the entry point for the game, handling initialization
and game session management.
"""

from src.interactive_battle import play_interactive_game

def main():
    """
    Main function to start the game.
    Handles any high-level initialization and error handling.
    """
    print("Welcome to 2Pillz Battle Game!")
    print("Get ready to fight!\n")
    
    try:
        play_interactive_game()
    except KeyboardInterrupt:
        print("\nGame terminated by user. Thanks for playing!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please report this error if it persists.")
    
    print("\nGame session ended. Come back soon!")

if __name__ == "__main__":
    main()