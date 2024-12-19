"""
Interactive battle system module implementing player vs AI gameplay.
Updated with fair AI behavior and sequential player-then-AI turns.
"""

import random
from typing import List, Dict, Tuple
from .game_core import Fighter, PillzType
from .battle_system import BattleSystem

def get_valid_stat_input(prompt: str, min_value: int = 1, max_value: int = 50) -> int:
    """Helper function to get valid numerical input for fighter stats"""
    while True:
        try:
            value = int(input(prompt))
            if min_value <= value <= max_value:
                return value
            print(f"Please enter a value between {min_value} and {max_value}.")
        except ValueError:
            print("Please enter a valid number.")

def create_fighter(is_player: bool = True) -> Fighter:
    """Create a fighter with user-input stats"""
    fighter_type = "your fighter" if is_player else "the AI fighter"
    print(f"\nSet stats for {fighter_type}:")
    
    damage = get_valid_stat_input(
        f"Enter damage value for {fighter_type} (1-50): "
    )
    resistance = get_valid_stat_input(
        f"Enter resistance value for {fighter_type} (1-50): "
    )
    
    name = "Player" if is_player else "AI Opponent"
    return Fighter(name, damage, resistance)

class InteractiveBattleSystem(BattleSystem):
    def play_interactive_battle(self, fighter1: Fighter, fighter2: Fighter) -> List[Dict]:
        """Run an interactive battle with clear player-then-AI turn structure"""
        battle_log = []
        
        for round_num in range(1, 7):
            self.display_round_start(round_num, fighter1, fighter2)
            
            # Player's turn (two steps)
            print("\nYOUR TURN")
            print("---------")
            move1 = self.get_player_move_choice()
            player_pillz = self.get_player_pillz_choice()
            fighter1.apply_pillz(player_pillz)
            
            # AI's turn (random decisions)
            print("\nAI OPPONENT'S TURN")
            print("-----------------")
            move2, ai_pillz = self._get_ai_decisions()
            fighter2.apply_pillz(ai_pillz)
            
            # Show both fighters' choices
            self.display_choices(fighter1, fighter2, move1, move2)
            
            # Process round and get results
            result, points1, points2 = self.process_round(fighter1, fighter2, move1, move2)
            
            self.display_round_results(
                fighter1, fighter2, move1, move2, 
                result, points1, points2
            )
            
            battle_log.append(self._create_round_log(
                round_num, fighter1, fighter2, 
                move1, move2, result, points1, points2
            ))
            
            fighter1.update_effects()
            fighter2.update_effects()
            
            input("\nPress Enter to continue to the next round...")
        
        return battle_log

    def display_round_start(self, round_num: int, fighter1: Fighter, fighter2: Fighter):
        """Display the start of round information"""
        print(f"\n{'='*20} ROUND {round_num} {'='*20}")
        
        # Player status
        print(f"\n{fighter1.name}:")
        print(f"Current Score: {fighter1.score:.1f} points")
        if fighter1.current_effect:
            print(f"Active Effect: {fighter1.current_effect.name}")
        
        # AI status
        print(f"\n{fighter2.name}:")
        print(f"Current Score: {fighter2.score:.1f} points")
        if fighter2.current_effect:
            print(f"Active Effect: {fighter2.current_effect.name}")
        
        print(f"\n{'='*50}")

    def get_player_move_choice(self) -> str:
        """Prompt player to choose a move"""
        print("\nSelect your move:")
        for i, move in enumerate(self.moves, 1):
            effective_against = self.move_relationships[move]
            print(f"{i}. {move} (Effective against: {', '.join(effective_against)})")
        
        while True:
            try:
                choice = int(input("Choose your move (1-5): "))
                if 1 <= choice <= 5:
                    chosen_move = self.moves[choice - 1]
                    print(f"\nYou chose: {chosen_move}")
                    return chosen_move
                else:
                    print("Invalid choice. Please enter a number between 1 and 5.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def get_player_pillz_choice(self) -> PillzType:
        """Prompt player to choose pillz"""
        print("\nSelect your pillz:")
        print("1. No pillz")
        print("2. South Pacific (Skip this round, double damage next round)")
        print("3. Nordic Shield (Double resistance this round, no resistance next round)")
        
        while True:
            try:
                choice = int(input("Enter your choice (1-3): "))
                if choice == 1:
                    print("\nYou chose: No pillz")
                    return PillzType.NONE
                elif choice == 2:
                    print("\nYou chose: South Pacific")
                    return PillzType.SOUTH_PACIFIC
                elif choice == 3:
                    print("\nYou chose: Nordic Shield")
                    return PillzType.NORDIC_SHIELD
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def _get_ai_decisions(self) -> Tuple[str, PillzType]:
        """Generate random AI decisions for both move and pillz"""
        # Randomly select move
        move = random.choice(self.moves)
        
        # Randomly select pillz (20% chance for each pillz type)
        pillz_choices = [PillzType.NONE] * 6 + [PillzType.SOUTH_PACIFIC] * 2 + [PillzType.NORDIC_SHIELD] * 2
        pillz = random.choice(pillz_choices)
        
        # Display AI's choices
        print(f"AI selected its move and pillz...")
        
        return move, pillz

    def display_choices(self, fighter1: Fighter, fighter2: Fighter, move1: str, move2: str):
        """Display both fighters' choices"""
        print("\nSelected Moves and Effects:")
        print("--------------------------")
        print(f"{fighter1.name}:")
        print(f"Move: {move1}")
        print(f"Effect: {fighter1.current_effect.name if fighter1.current_effect else 'None'}")
        
        print(f"\n{fighter2.name}:")
        print(f"Move: {move2}")
        print(f"Effect: {fighter2.current_effect.name if fighter2.current_effect else 'None'}")

    def display_round_results(self, 
                            fighter1: Fighter, 
                            fighter2: Fighter, 
                            move1: str, 
                            move2: str, 
                            result: str,
                            points1: float,
                            points2: float):
        """Display the results of a combat round with points gained"""
        print(f"\n{'='*20} ROUND RESULTS {'='*20}")
        
        # Show round outcome
        print(f"\n{result}")
        
        # Show points gained
        if points1 > 0:
            print(f"{fighter1.name} gained {points1:.1f} points!")
        if points2 > 0:
            print(f"{fighter2.name} gained {points2:.1f} points!")
        
        # Show current scores
        print(f"\nCurrent Scores:")
        print(f"{fighter1.name}: {fighter1.score:.1f} points")
        print(f"{fighter2.name}: {fighter2.score:.1f} points")
        print(f"\n{'='*50}")

    def _create_round_log(self, 
                         round_num: int, 
                         fighter1: Fighter, 
                         fighter2: Fighter,
                         move1: str,
                         move2: str,
                         result: str,
                         points1: float,
                         points2: float) -> Dict:
        """Create a log entry for the current round"""
        return {
            'round': round_num,
            'move1': move1,
            'move2': move2,
            'fighter1_effect': fighter1.current_effect.name if fighter1.current_effect else 'None',
            'fighter2_effect': fighter2.current_effect.name if fighter2.current_effect else 'None',
            'result': result,
            'fighter1_score': fighter1.score,
            'fighter2_score': fighter2.score,
            'points_gained1': points1,
            'points_gained2': points2
        }

def play_interactive_game():
    """Main function with enhanced fighter creation"""
    battle_system = InteractiveBattleSystem()
    
    print("\nWelcome to the Interactive Battle System!")
    print("Score points by winning rounds - highest score wins!")
    print("\nFirst, let's set up the fighters...")
    
    # Create fighters with custom stats
    player = create_fighter(is_player=True)
    ai_opponent = create_fighter(is_player=False)
    
    print("\nFighter Stats Summary:")
    print(f"\nYour fighter:")
    print(f"Damage: {player.damage}")
    print(f"Resistance: {player.resistance}")
    print(f"\nOpponent:")
    print(f"Damage: {ai_opponent.damage}")
    print(f"Resistance: {ai_opponent.resistance}")
    
    input("\nPress Enter to start the battle...")
    
    battle_log = battle_system.play_interactive_battle(player, ai_opponent)
    
    # Display final results
    print("\nBattle Complete!")
    final_score1 = battle_log[-1]['fighter1_score']
    final_score2 = battle_log[-1]['fighter2_score']
    
    print(f"\nFinal Scores:")
    print(f"{player.name}: {final_score1:.1f} points")
    print(f"{ai_opponent.name}: {final_score2:.1f} points")
    
    if final_score1 > final_score2:
        print(f"\n{player.name} wins!")
    elif final_score2 > final_score1:
        print(f"\n{ai_opponent.name} wins!")
    else:
        print("\nIt's a draw!")

if __name__ == "__main__":
    play_interactive_game()