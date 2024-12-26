from game_mechanics import Fighter, GameRound, get_player_move, get_ai_move, display_score
import random

def get_valid_stat_input(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if 0 <= value <= 100:
                return value
            print("Value must be between 0 and 100")
        except ValueError:
            print("Please enter a valid number")

def main():
    print("Welcome to the Fighting Game!")
    
    # Initialize player fighter
    print("\nEnter Player fighter stats:")
    player_damage = get_valid_stat_input("Enter damage (0-100): ")
    player_resistance = get_valid_stat_input("Enter resistance (0-100): ")
    player = Fighter("Player", player_damage, player_resistance)
    
    # Initialize AI fighter
    print("\nEnter AI fighter stats:")
    ai_damage = get_valid_stat_input("Enter damage (0-100): ")
    ai_resistance = get_valid_stat_input("Enter resistance (0-100): ")
    ai = Fighter("AI", ai_damage, ai_resistance)
    
    print("\nFighter Stats Summary:")
    print(f"Player - Damage: {player_damage}, Resistance: {player_resistance}")
    print(f"AI - Damage: {ai_damage}, Resistance: {ai_resistance}")
    
    round_num = 1
    max_rounds = 6
    
    while True:
        print(f"\nRound {round_num}")
        
        # Create and process round
        current_round = GameRound(player, ai)
        current_round.move1 = get_player_move()
        current_round.move2 = get_ai_move()
        
        print(f"\nAI chose: {current_round.move2.name}")
        result = current_round.resolve_round()
        print(result)
        display_score(player, ai)
        
        # Check if we need to continue
        if round_num >= max_rounds:
            if player.points == ai.points:
                print("\nScores tied! Starting tie-breaker round...")
                round_num += 1
                continue
            break
        round_num += 1
    
    # Announce winner
    print("\nGame Over!")
    if player.points > ai.points:
        print(f"You win! Final score - Player: {player.points}, AI: {ai.points}")
    else:
        print(f"AI wins! Final score - AI: {ai.points}, Player: {player.points}")

if __name__ == "__main__":
    main()