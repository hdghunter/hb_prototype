"""
Interactive battle system module implementing player vs AI gameplay.
This module extends the base battle system to provide an interactive
command-line interface for human players.

The module is structured around the InteractiveBattleSystem class which handles:
1. Player input collection and validation
2. Game state display
3. Battle flow management
4. AI opponent decision making
"""

import random
from typing import List, Dict, Tuple
from .game_core import Fighter, PillzType
from .battle_system import BattleSystem

class InteractiveBattleSystem(BattleSystem):
    """
    Extends the base battle system to provide interactive gameplay.
    Handles player input, display of game state, and AI opponent behavior.
    """
    
    def play_interactive_battle(self, fighter1: Fighter, fighter2: Fighter) -> List[Dict]:
        """
        Run an interactive battle where player controls fighter1 against AI-controlled fighter2.
        
        This is the main gameplay loop that:
        - Displays the current game state
        - Collects player decisions
        - Generates AI opponent responses
        - Processes combat results
        - Records battle history
        
        Args:
            fighter1: The player-controlled fighter
            fighter2: The AI-controlled fighter
            
        Returns:
            List of dictionaries containing round-by-round battle information
        """
        battle_log = []
        
        for round_num in range(1, 7):
            # Display round information
            self.display_round_start(round_num, fighter1, fighter2)
            
            # Handle pillz phase
            player_pillz = self.get_player_pillz_choice()
            fighter1.apply_pillz(player_pillz)
            
            ai_pillz = self._get_ai_pillz_decision()
            if ai_pillz != PillzType.NONE:
                fighter2.apply_pillz(ai_pillz)
                print(f"\nAI used {fighter2.current_effect.name}")
            
            # Record initial health for damage tracking
            initial_health1 = fighter1.health
            initial_health2 = fighter2.health
            
            # Combat phase
            move1 = self.get_player_move_choice()
            move2 = self._get_ai_move_decision(fighter2, fighter1)
            
            # Process round and get results
            round_result = self._process_round(fighter1, fighter2, move1, move2)
            
            # Calculate health changes
            health_change1 = fighter1.health - initial_health1
            health_change2 = fighter2.health - initial_health2
            
            # Display and log results
            self.display_round_results(
                fighter1, fighter2, move1, move2, 
                round_result, health_change1, health_change2
            )
            
            battle_log.append(self._create_round_log(
                round_num, fighter1, fighter2, 
                move1, move2, round_result
            ))
            
            # Update effects for next round
            fighter1.update_effects()
            fighter2.update_effects()
            
            # Pause for player to review results
            input("\nPress Enter to continue to the next round...")
        
        return battle_log

    def get_player_pillz_choice(self) -> PillzType:
        """
        Prompt player to choose whether to use a pillz, with input validation.
        
        The function displays available options with their effects and ensures
        valid input before returning.
        
        Returns:
            The chosen PillzType
        """
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
        """
        Prompt player to choose a move, showing effectiveness information.
        
        Displays each available move along with what moves it's effective against,
        helping players make strategic decisions.
        
        Returns:
            The chosen move as a string
        """
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
        """
        Display the start of round information in a clear, formatted way.
        
        Shows current round number and both fighters' status including:
        - Current health
        - Active effects
        
        Args:
            round_num: Current round number
            fighter1: First fighter (player)
            fighter2: Second fighter (AI)
        """
        print(f"\n{'='*50}")
        print(f"Round {round_num}")
        print(f"{'='*50}")
        
        # Player status
        print(f"\n{fighter1.name}:")
        print(f"Health: {fighter1.health:.1f}")
        print(f"Current Effect: {fighter1.current_effect.name if fighter1.current_effect else 'None'}")
        
        # AI status
        print(f"\n{fighter2.name}:")
        print(f"Health: {fighter2.health:.1f}")
        print(f"Current Effect: {fighter2.current_effect.name if fighter2.current_effect else 'None'}")

    def display_round_results(self, 
                            fighter1: Fighter, 
                            fighter2: Fighter, 
                            move1: str, 
                            move2: str, 
                            result: str,
                            health_change1: float,
                            health_change2: float):
        """
        Display the results of a combat round with detailed information.
        
        Shows:
        - Moves chosen by both fighters
        - Combat result
        - Health changes
        - Current health status
        
        Args:
            fighter1: First fighter (player)
            fighter2: Second fighter (AI)
            move1: Move chosen by fighter1
            move2: Move chosen by fighter2
            result: Result of the round
            health_change1: Change in fighter1's health
            health_change2: Change in fighter2's health
        """
        print(f"\nRound Results:")
        print(f"{fighter1.name} used {move1}")
        print(f"{fighter2.name} used {move2}")
        print(f"\nResult: {result}")
        
        # Show health changes if any occurred
        if health_change1 != 0:
            print(f"{fighter1.name} lost {abs(health_change1):.1f} health")
        if health_change2 != 0:
            print(f"{fighter2.name} lost {abs(health_change2):.1f} health")
        
        # Show current health status
        print(f"\nCurrent Health:")
        print(f"{fighter1.name}: {fighter1.health:.1f}")
        print(f"{fighter2.name}: {fighter2.health:.1f}")

    def _get_ai_pillz_decision(self) -> PillzType:
        """
        Generate AI decision for pillz usage.
        
        Currently implements a simple random strategy with 20% chance to use each pillz type.
        This could be expanded with more sophisticated decision-making logic.
        
        Returns:
            The chosen PillzType
        """
        if random.random() < 0.2:  # 20% chance to use a pillz
            return random.choice([PillzType.SOUTH_PACIFIC, PillzType.NORDIC_SHIELD])
        return PillzType.NONE

    def _get_ai_move_decision(self, ai_fighter: Fighter, player_fighter: Fighter) -> str:
        """
        Generate AI decision for move selection.
        
        Currently implements a simple random strategy, but could be enhanced with:
        - Pattern recognition of player moves
        - Health-based strategy
        - Counter-move analysis
        
        Args:
            ai_fighter: The AI-controlled fighter
            player_fighter: The player-controlled fighter
            
        Returns:
            The chosen move as a string
        """
        return random.choice(self.moves)

    def _create_round_log(self, 
                         round_num: int, 
                         fighter1: Fighter, 
                         fighter2: Fighter,
                         move1: str,
                         move2: str,
                         result: str) -> Dict:
        """
        Create a log entry for the current round.
        
        Args:
            round_num: Current round number
            fighter1: First fighter (player)
            fighter2: Second fighter (AI)
            move1: Move chosen by fighter1
            move2: Move chosen by fighter2
            result: Result of the round
            
        Returns:
            Dictionary containing round information
        """
        return {
            'round': round_num,
            'move1': move1,
            'move2': move2,
            'fighter1_effect': fighter1.current_effect.name if fighter1.current_effect else 'None',
            'fighter2_effect': fighter2.current_effect.name if fighter2.current_effect else 'None',
            'result': result,
            'fighter1_health': max(0, fighter1.health),
            'fighter2_health': max(0, fighter2.health)
        }

def play_interactive_game():
    """
    Main function to start and run an interactive game session.
    
    Creates fighters, initializes the battle system, and manages the game flow.
    Displays introduction and final results.
    """
    battle_system = InteractiveBattleSystem()
    
    # Create fighters with balanced but different strengths
    player = Fighter("Player", damage=30, resistance=20)
    ai_opponent = Fighter("AI Opponent", damage=20, resistance=30)
    
    # Display game introduction
    print("\nWelcome to the Interactive Battle System!")
    print(f"\nYour fighter: {player.name}")
    print(f"Damage: {player.damage}")
    print(f"Resistance: {player.resistance}")
    print(f"\nOpponent: {ai_opponent.name}")
    print(f"Damage: {ai_opponent.damage}")
    print(f"Resistance: {ai_opponent.resistance}")
    
    input("\nPress Enter to start the battle...")
    
    # Run the battle
    battle_log = battle_system.play_interactive_battle(player, ai_opponent)
    
    # Display final results
    print("\nBattle Complete!")
    final_health1 = battle_log[-1]['fighter1_health']
    final_health2 = battle_log[-1]['fighter2_health']
    
    print(f"\nFinal Health:")
    print(f"{player.name}: {final_health1:.1f}")
    print(f"{ai_opponent.name}: {final_health2:.1f}")
    
    if final_health1 > final_health2:
        print(f"\n{player.name} wins!")
    elif final_health2 > final_health1:
        print(f"\n{ai_opponent.name} wins!")
    else:
        print("\nIt's a draw!")

if __name__ == "__main__":
    play_interactive_game()