"""
Interactive battle system module implementing player vs AI gameplay.
Updated to use scoring system instead of health depletion.
"""

import random
from typing import List, Dict, Tuple
from .game_core import Fighter, PillzType
from .battle_system import BattleSystem

class InteractiveBattleSystem(BattleSystem):
    """
    Extends the base battle system to provide interactive gameplay.
    Updated to handle point scoring instead of health reduction.
    """
    
    def play_interactive_battle(self, fighter1: Fighter, fighter2: Fighter) -> List[Dict]:
        """Run an interactive battle where player controls fighter1"""
        battle_log = []
        
        for round_num in range(1, 7):
            self.display_round_start(round_num, fighter1, fighter2)
            
            # Handle pillz phase
            player_pillz = self.get_player_pillz_choice()
            fighter1.apply_pillz(player_pillz)
            
            ai_pillz = self._get_ai_pillz_decision()
            if ai_pillz != PillzType.NONE:
                fighter2.apply_pillz(ai_pillz)
                print(f"\nAI used {fighter2.current_effect.name}")
            
            # Combat phase
            move1 = self.get_player_move_choice()
            move2 = self._get_ai_move_decision(fighter2, fighter1)
            
            # Process round and get results
            result, points1, points2 = self.process_round(fighter1, fighter2, move1, move2)
            
            # Display results
            self.display_round_results(
                fighter1, fighter2, move1, move2, 
                result, points1, points2
            )
            
            battle_log.append(self._create_round_log(
                round_num, fighter1, fighter2, 
                move1, move2, result, points1, points2
            ))
            
            # Update effects for next round
            fighter1.update_effects()
            fighter2.update_effects()
            
            input("\nPress Enter to continue to the next round...")
        
        return battle_log

    def get_player_pillz_choice(self) -> PillzType:
        """Prompt player to choose whether to use a pillz"""
        print("\nDo you want to use a pillz this round?")
        print("1. No pillz")
        print("2. South Pacific (Skip this round, double damage next round)")
        print("3. Nordic Shield (Double resistance this round, no resistance next round)")
        
        while True:
            try:
                choice = int(input("Enter your choice (1-3): "))
                if choice == 1:
                    return PillzType.NONE
                elif choice == 2:
                    return PillzType.SOUTH_PACIFIC
                elif choice == 3:
                    return PillzType.NORDIC_SHIELD
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    def get_player_move_choice(self) -> str:
        """Prompt player to choose a move"""
        print("\nAvailable moves:")
        for i, move in enumerate(self.moves, 1):
            effective_against = self.move_relationships[move]
            print(f"{i}. {move} (Effective against: {', '.join(effective_against)})")
        
        while True:
            try:
                choice = int(input("Choose your move (1-5): "))
                if 1 <= choice <= 5:
                    return self.moves[choice - 1]
                else:
                    print("Invalid choice. Please enter a number between 1 and 5.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def display_round_start(self, round_num: int, fighter1: Fighter, fighter2: Fighter):
        """Display the start of round information with current scores"""
        print(f"\n{'='*50}")
        print(f"Round {round_num}")
        print(f"{'='*50}")
        
        # Player status
        print(f"\n{fighter1.name}:")
        print(f"Current Score: {fighter1.score:.1f} points")
        print(f"Current Effect: {fighter1.current_effect.name if fighter1.current_effect else 'None'}")
        
        # AI status
        print(f"\n{fighter2.name}:")
        print(f"Current Score: {fighter2.score:.1f} points")
        print(f"Current Effect: {fighter2.current_effect.name if fighter2.current_effect else 'None'}")
        
        # Display round separator
        print(f"\n{'-'*50}")

    def display_round_results(self, 
                            fighter1: Fighter, 
                            fighter2: Fighter, 
                            move1: str, 
                            move2: str, 
                            result: str,
                            points1: float,
                            points2: float):
        """Display the results of a combat round with points gained"""
        print(f"\nRound Results:")
        print(f"{fighter1.name} used {move1}")
        print(f"{fighter2.name} used {move2}")
        print(f"\nResult: {result}")
        
        # Show points gained
        if points1 > 0:
            print(f"{fighter1.name} gained {points1:.1f} points!")
        if points2 > 0:
            print(f"{fighter2.name} gained {points2:.1f} points!")
        
        # Show current scores
        print(f"\nCurrent Scores:")
        print(f"{fighter1.name}: {fighter1.score:.1f} points")
        print(f"{fighter2.name}: {fighter2.score:.1f} points")

    def _get_ai_pillz_decision(self) -> PillzType:
        """Generate AI decision for pillz usage"""
        if random.random() < 0.2:  # 20% chance to use a pillz
            return random.choice([PillzType.SOUTH_PACIFIC, PillzType.NORDIC_SHIELD])
        return PillzType.NONE

    def _get_ai_move_decision(self, ai_fighter: Fighter, player_fighter: Fighter) -> str:
        """Generate AI decision for move selection"""
        return random.choice(self.moves)

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
    """Main function to start and run an interactive game session"""
    battle_system = InteractiveBattleSystem()
    
    # Create fighters
    player = Fighter("Player", damage=30, resistance=20)
    ai_opponent = Fighter("AI Opponent", damage=20, resistance=30)
    
    print("\nWelcome to the Interactive Battle System!")
    print("Score points by winning rounds - highest score wins!")
    print(f"\nYour fighter: {player.name}")
    print(f"Damage: {player.damage}")
    print(f"Resistance: {player.resistance}")
    print(f"\nOpponent: {ai_opponent.name}")
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