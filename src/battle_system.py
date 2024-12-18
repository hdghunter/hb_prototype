"""
Base battle system module implementing the core battle mechanics.
This module handles the rules of combat, move relationships, and battle simulation.
"""

import random
from typing import List, Dict
from .game_core import Fighter, PillzType

class BattleSystem:
    """
    Implements the core battle mechanics and rules.
    Handles move relationships and battle simulation.
    """
    def __init__(self):
        """
        Initialize the battle system with move relationships.
        Each move is effective against specific other moves in a balanced network.
        """
        self.move_relationships = {
            'Rush': ['Strike', 'Sweep'],
            'Strike': ['Sweep', 'Grapple'],
            'Sweep': ['Guard', 'Grapple'],
            'Guard': ['Rush', 'Strike'],
            'Grapple': ['Rush', 'Guard']
        }
        self.moves = list(self.move_relationships.keys())
    
    def does_move_win(self, move1: str, move2: str) -> bool:
        """
        Determine if move1 wins against move2 based on move relationships.
        
        Args:
            move1: The first move
            move2: The second move
            
        Returns:
            True if move1 beats move2, False otherwise
        """
        return move2 in self.move_relationships[move1]
    
    def simulate_single_battle(self, fighter1: Fighter, fighter2: Fighter) -> List[Dict]:
        """
        Simulate a complete battle between two fighters with random moves and pillz usage.
        
        Args:
            fighter1: First fighter
            fighter2: Second fighter
            
        Returns:
            List of dictionaries containing round-by-round battle information
        """
        battle_log = []
        
        for round_num in range(1, 7):
            # Randomly decide if fighters use pillz (for simulation purposes)
            if random.random() < 0.2:  # 20% chance to use South Pacific
                fighter1.apply_pillz(PillzType.SOUTH_PACIFIC)
            if random.random() < 0.2:  # 20% chance to use Nordic Shield
                fighter2.apply_pillz(PillzType.NORDIC_SHIELD)
            
            move1 = random.choice(self.moves)
            move2 = random.choice(self.moves)
            
            # Process round results
            round_result = self._process_round(fighter1, fighter2, move1, move2)
            
            # Record round results
            battle_log.append({
                'round': round_num,
                'move1': move1,
                'move2': move2,
                'fighter1_effect': fighter1.current_effect.name if fighter1.current_effect else 'None',
                'fighter2_effect': fighter2.current_effect.name if fighter2.current_effect else 'None',
                'result': round_result,
                'fighter1_health': max(0, fighter1.health),
                'fighter2_health': max(0, fighter2.health)
            })
            
            # Update effects for next round
            fighter1.update_effects()
            fighter2.update_effects()
        
        return battle_log

    def _process_round(self, fighter1: Fighter, fighter2: Fighter, move1: str, move2: str) -> str:
        """
        Process a single round of combat between two fighters.
        
        Args:
            fighter1: First fighter
            fighter2: Second fighter
            move1: Move chosen by fighter1
            move2: Move chosen by fighter2
            
        Returns:
            String describing the round result
        """
        # Check if either fighter is skipping due to pillz effect
        fighter1_skip = fighter1.current_effect and fighter1.current_effect.skip_round
        fighter2_skip = fighter2.current_effect and fighter2.current_effect.skip_round
        
        if fighter1_skip and fighter2_skip:
            return 'Both fighters skip (Pillz effect)'
        elif fighter1_skip:
            damage = fighter2.calculate_damage(fighter1)
            fighter1.health -= damage
            return f'{fighter2.name} wins (Opponent used {fighter1.current_effect.name})'
        elif fighter2_skip:
            damage = fighter1.calculate_damage(fighter2)
            fighter2.health -= damage
            return f'{fighter1.name} wins (Opponent used {fighter2.current_effect.name})'
        
        # Normal combat resolution
        if move1 == move2:
            return 'Draw'
        elif self.does_move_win(move1, move2):
            damage = fighter1.calculate_damage(fighter2)
            fighter2.health -= damage
            return f'{fighter1.name} wins'
        elif self.does_move_win(move2, move1):
            damage = fighter2.calculate_damage(fighter1)
            fighter1.health -= damage
            return f'{fighter2.name} wins'
        
        return 'No effect'