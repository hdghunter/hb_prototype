"""
Base battle system module implementing the core battle mechanics.
Updated to use scoring system instead of health depletion.
"""

import random
from typing import List, Dict, Tuple
from .game_core import Fighter, PillzType

class BattleSystem:
    """
    Implements the core battle mechanics and rules.
    Updated to handle point scoring instead of health reduction.
    """
    def __init__(self):
        self.move_relationships = {
            'Rush': ['Strike', 'Sweep'],
            'Strike': ['Sweep', 'Grapple'],
            'Sweep': ['Guard', 'Grapple'],
            'Guard': ['Rush', 'Strike'],
            'Grapple': ['Rush', 'Guard']
        }
        self.moves = list(self.move_relationships.keys())
    
    def does_move_win(self, move1: str, move2: str) -> bool:
        """Determine if move1 wins against move2 based on move relationships"""
        return move2 in self.move_relationships[move1]
    
    def process_round(self, fighter1: Fighter, fighter2: Fighter, 
                     move1: str, move2: str) -> Tuple[str, float, float]:
        """
        Process a single round of combat between two fighters.
        Returns the result and potential points scored by each fighter.
        
        Args:
            fighter1: First fighter
            fighter2: Second fighter
            move1: Move chosen by fighter1
            move2: Move chosen by fighter2
            
        Returns:
            Tuple of (result string, fighter1 points, fighter2 points)
        """
        fighter1_skip = fighter1.current_effect and fighter1.current_effect.skip_round
        fighter2_skip = fighter2.current_effect and fighter2.current_effect.skip_round
        
        if fighter1_skip and fighter2_skip:
            return 'Both fighters skip (Pillz effect)', 0, 0
        elif fighter1_skip:
            points = fighter2.calculate_damage(fighter1)
            fighter2.add_score(points)
            return f'{fighter2.name} wins (Opponent used {fighter1.current_effect.name})', 0, points
        elif fighter2_skip:
            points = fighter1.calculate_damage(fighter2)
            fighter1.add_score(points)
            return f'{fighter1.name} wins (Opponent used {fighter2.current_effect.name})', points, 0
        
        if move1 == move2:
            return 'Draw', 0, 0
        elif self.does_move_win(move1, move2):
            points = fighter1.calculate_damage(fighter2)
            fighter1.add_score(points)
            return f'{fighter1.name} wins', points, 0
        elif self.does_move_win(move2, move1):
            points = fighter2.calculate_damage(fighter1)
            fighter2.add_score(points)
            return f'{fighter2.name} wins', 0, points
        
        return 'No effect', 0, 0
    
    def simulate_single_battle(self, fighter1: Fighter, fighter2: Fighter) -> List[Dict]:
        """Simulate a complete battle between two fighters"""
        battle_log = []
        
        for round_num in range(1, 7):
            # Randomly decide if fighters use pillz
            if random.random() < 0.2:
                fighter1.apply_pillz(PillzType.SOUTH_PACIFIC)
            if random.random() < 0.2:
                fighter2.apply_pillz(PillzType.NORDIC_SHIELD)
            
            move1 = random.choice(self.moves)
            move2 = random.choice(self.moves)
            
            # Process round
            result, points1, points2 = self.process_round(fighter1, fighter2, move1, move2)
            
            # Record round results
            battle_log.append({
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
            })
            
            # Update effects for next round
            fighter1.update_effects()
            fighter2.update_effects()
        
        return battle_log