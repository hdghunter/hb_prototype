from typing import List, Optional
import random
from src.game_mechanics import Fighter, Move
from src.game.round import Round
from src.effects.manager import EffectManager
from src.pillz.factory import PillzFactory
from src.pillz.types import PillzType
from src.pillz.pillz import Pillz

def get_valid_stat_input(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if 0 <= value <= 100:
                return value
            print("Value must be between 0 and 100")
        except ValueError:
            print("Please enter a valid number")

def display_move_guide():
    """Display available moves and what they beat"""
    print("\nAvailable moves:")
    for move in Move:
        print(f"{move.value}: {move.name}")
    print("\nMove relationships:")
    print("RUSH beats: STRIKE, SWEEP")
    print("STRIKE beats: SWEEP, GRAPPLE")
    print("SWEEP beats: GUARD, GRAPPLE")
    print("GUARD beats: RUSH, STRIKE")
    print("GRAPPLE beats: RUSH, GUARD")

def get_player_move() -> Move:
    """Get move selection from player"""
    while True:
        try:
            display_move_guide()
            choice = int(input("\nSelect your move (1-5): "))
            return Move(choice)
        except (ValueError, KeyError):
            print("Invalid input! Please enter a number between 1 and 5.")

def display_available_pillz() -> None:
    """Display available pillz and their effects"""
    print("\nAvailable Pillz:")
    for pillz_type, pillz_name in PillzFactory.get_available_pillz().items():
        pillz = PillzFactory.create_pillz(pillz_type)
        print(f"{pillz_type.value}: {pillz_name} - {pillz.description}")

def get_player_pillz() -> Optional[Pillz]:
    """Get pillz selection from player"""
    while True:
        try:
            display_available_pillz()
            choice = input("\nSelect your pillz (enter number or press Enter to skip): ").strip()
            
            if not choice:  # Player skips pillz
                return None
                
            pillz_type = PillzType(int(choice))
            return PillzFactory.create_pillz(pillz_type)
        except (ValueError, KeyError):
            print("Invalid input! Please enter a valid pillz number or press Enter to skip.")

def get_ai_pillz() -> Optional[Pillz]:
    """Random pillz selection for AI"""
    if random.random() < 0.7:  # 70% chance to use a pillz
        pillz_types = list(PillzType)
        return PillzFactory.create_pillz(random.choice(pillz_types))
    return None

def get_ai_move() -> Move:
    """Random move selection for AI"""
    return random.choice(list(Move))

def main():
    print("Welcome to the Fighting Game!")
    
    # Initialize fighters
    print("\nEnter Player fighter stats:")
    player_damage = get_valid_stat_input("Enter damage (0-100): ")
    player_resistance = get_valid_stat_input("Enter resistance (0-100): ")
    player = Fighter("Player", player_damage, player_resistance)
    
    print("\nEnter AI fighter stats:")
    ai_damage = get_valid_stat_input("Enter damage (0-100): ")
    ai_resistance = get_valid_stat_input("Enter resistance (0-100): ")
    ai = Fighter("AI", ai_damage, ai_resistance)
    
    print("\nFighter Stats Summary:")
    print(f"Player - Damage: {player_damage}, Resistance: {player_resistance}")
    print(f"AI - Damage: {ai_damage}, Resistance: {ai_resistance}")
    
    # Initialize effect manager
    effect_manager = EffectManager()
    round_num = 1
    max_rounds = 6
    
    while True:
        print(f"\nRound {round_num}")
        
        # Create and process round
        current_round = Round(player, ai, round_num, effect_manager)
        
        # Move selection phase
        player_move = get_player_move()
        ai_move = get_ai_move()
        
        current_round.set_move(player.name, player_move)
        current_round.set_move(ai.name, ai_move)
        
        # Pillz selection phase
        player_pillz = get_player_pillz()
        if player_pillz:
            current_round.set_pillz(player.name, player_pillz)
            
        ai_pillz = get_ai_pillz()
        if ai_pillz:
            current_round.set_pillz(ai.name, ai_pillz)
        
        # Resolve round and display results
        round_summary = current_round.resolve()
        print(round_summary)
        
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