"""
Interactive battle system module implementing player vs AI gameplay.
Updated to use the new state management and effect processing systems.
"""

import random
from typing import List, Dict, Tuple
from .game_core import Fighter, PillzType
from .battle_system import BattleSystem
from .battle_state import BattleState
from .effect_manager import EffectManager

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
    """
    Extends the base battle system to provide interactive gameplay.
    Updated to use battle state and effect manager.
    """
    
    def play_interactive_battle(self, fighter1: Fighter, fighter2: Fighter) -> List[Dict]:
        """Run an interactive battle with clear player-then-AI turn structure"""
        battle_state = BattleState(fighter1, fighter2)
        battle_log = []
        
        while True:
            self.display_round_start(battle_state)
            
            # Player's turn (two steps)
            print("\nYOUR TURN")
            print("---------")
            move1 = self.get_player_move_choice()
            battle_state.record_move(fighter1, move1)
            
            player_pillz = self.get_player_pillz_choice()
            if player_pillz != PillzType.NONE:
                fighter1.apply_pillz(player_pillz, battle_state.current_round)
                battle_state.record_effect(fighter1, fighter1.active_effects[-1])
            
            # AI's turn (random decisions)
            print("\nAI OPPONENT'S TURN")
            print("-----------------")
            move2, ai_pillz = self._get_ai_decisions()
            battle_state.record_move(fighter2, move2)
            
            if ai_pillz != PillzType.NONE:
                fighter2.apply_pillz(ai_pillz, battle_state.current_round)
                battle_state.record_effect(fighter2, fighter2.active_effects[-1])
                print(f"AI used {ai_pillz.name}")
            
            # Show both fighters' choices
            self.display_choices(battle_state)
            
            # Process round and get results
            result, points1, points2 = self.process_round(
                battle_state, move1, move2
            )
            
            self.display_round_results(battle_state, points1, points2)
            
            battle_log.append(self._create_round_log(
                battle_state, points1, points2
            ))
            
            if not battle_state.advance_round():
                break
            
            input("\nPress Enter to continue to the next round...")
        
        return battle_log

    def display_round_start(self, battle_state: BattleState):
        """Display the start of round information"""
        print(f"\n{'='*20} ROUND {battle_state.current_round} {'='*20}")
        
        # Player status
        print(f"\n{battle_state.fighter1.name}:")
        print(f"Current Score: {battle_state.fighter1.score:.1f} points")
        for effect in battle_state.get_active_effects(battle_state.fighter1):
            print(f"Active Effect: {effect.name}")
        
        # AI status
        print(f"\n{battle_state.fighter2.name}:")
        print(f"Current Score: {battle_state.fighter2.score:.1f} points")
        for effect in battle_state.get_active_effects(battle_state.fighter2):
            print(f"Active Effect: {effect.name}")
        
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
        
        print(f"AI selected its move and pillz...")
        
        return move, pillz

    def display_choices(self, battle_state: BattleState):
        """Display both fighters' choices"""
        print("\nSelected Moves and Effects:")
        print("--------------------------")
        print(f"{battle_state.fighter1.name}:")
        print(f"Move: {battle_state.current_round_state.fighter1_move}")
        if battle_state.current_round_state.fighter1_effect:
            print(f"Effect: {battle_state.current_round_state.fighter1_effect.name}")
        
        print(f"\n{battle_state.fighter2.name}:")
        print(f"Move: {battle_state.current_round_state.fighter2_move}")
        if battle_state.current_round_state.fighter2_effect:
            print(f"Effect: {battle_state.current_round_state.fighter2_effect.name}")

    def display_round_results(self, battle_state: BattleState, points1: float, points2: float):
        """Display the results of a combat round"""
        print(f"\n{'='*20} ROUND RESULTS {'='*20}")
        
        print(f"\n{battle_state.current_round_state.result}")
        
        if points1 > 0:
            print(f"{battle_state.fighter1.name} gained {points1:.1f} points!")
        if points2 > 0:
            print(f"{battle_state.fighter2.name} gained {points2:.1f} points!")
        
        print(f"\nCurrent Scores:")
        print(f"{battle_state.fighter1.name}: {battle_state.fighter1.score:.1f} points")
        print(f"{battle_state.fighter2.name}: {battle_state.fighter2.score:.1f} points")
        
        # Display any special achievements
        streak = battle_state.get_streak(battle_state.fighter1)
        if streak > 1:
            print(f"\n{battle_state.fighter1.name} is on a {streak} win streak!")
        
        streak = battle_state.get_streak(battle_state.fighter2)
        if streak > 1:
            print(f"\n{battle_state.fighter2.name} is on a {streak} win streak!")
        
        print(f"\n{'='*50}")

    def _create_round_log(self, 
                         battle_state: BattleState,
                         points1: float,
                         points2: float) -> Dict:
        """Create a log entry for the current round"""
        return {
            'round': battle_state.current_round,
            'move1': battle_state.current_round_state.fighter1_move,
            'move2': battle_state.current_round_state.fighter2_move,
            'fighter1_effect': (battle_state.current_round_state.fighter1_effect.name 
                              if battle_state.current_round_state.fighter1_effect 
                              else 'None'),
            'fighter2_effect': (battle_state.current_round_state.fighter2_effect.name
                              if battle_state.current_round_state.fighter2_effect
                              else 'None'),
            'result': battle_state.current_round_state.result,
            'fighter1_score': battle_state.fighter1.score,
            'fighter2_score': battle_state.fighter2.score,
            'points_gained1': points1,
            'points_gained2': points2
        }

def play_interactive_game():
    """Main function to start and run an interactive game session"""
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
    
    # Display final results with battle summary
    print("\nBattle Complete!")
    
    final_log = battle_log[-1]
    print(f"\nFinal Scores:")
    print(f"{player.name}: {final_log['fighter1_score']:.1f} points")
    print(f"{ai_opponent.name}: {final_log['fighter2_score']:.1f} points")
    
    if final_log['fighter1_score'] > final_log['fighter2_score']:
        print(f"\n{player.name} wins!")
    elif final_log['fighter2_score'] > final_log['fighter1_score']:
        print(f"\n{ai_opponent.name} wins!")
    else:
        print("\nIt's a draw!")

if __name__ == "__main__":
    play_interactive_game()