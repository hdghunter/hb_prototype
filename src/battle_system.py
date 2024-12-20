"""
Battle system module integrating state management and effect processing.
"""

from typing import List, Dict, Tuple
from .game_core import Fighter, PillzType
from .battle_state import BattleState
from .effect_manager import EffectManager

class BattleSystem:
    def __init__(self):
        """Initialize the battle system with all required components"""
        self.move_relationships = {
            'Rush': ['Strike', 'Sweep'],
            'Strike': ['Sweep', 'Grapple'],
            'Sweep': ['Guard', 'Grapple'],
            'Guard': ['Rush', 'Strike'],
            'Grapple': ['Rush', 'Guard']
        }
        self.moves = list(self.move_relationships.keys())
        self.effect_manager = EffectManager()
    
    def does_move_win(self, move1: str, move2: str) -> bool:
        """Determine if move1 wins against move2"""
        return move2 in self.move_relationships[move1]
    
    def process_round(self, 
                     battle_state: BattleState,
                     move1: str, 
                     move2: str) -> Tuple[str, float, float]:
        """Process a single round of combat"""
        # Record moves in battle state
        battle_state.record_move(battle_state.fighter1, move1)
        battle_state.record_move(battle_state.fighter2, move2)
        
        # Process all active effects
        modified_stats = self.effect_manager.process_effects(battle_state)
        
        # Get modified stats for both fighters
        stats1 = modified_stats['fighter1']
        stats2 = modified_stats['fighter2']
        
        # Check for skipped rounds due to effects
        fighter1_skip = stats1.get('skip_round', False)
        fighter2_skip = stats2.get('skip_round', False)
        
        # Initialize points
        points1 = 0
        points2 = 0
        
        # Determine round result
        if fighter1_skip and fighter2_skip:
            result = 'Both fighters skip (Pillz effect)'
        elif fighter1_skip:
            damage = (battle_state.fighter2.damage * 
                     stats2['damage_multiplier'])
            points2 = damage
            battle_state.fighter2.add_score(points2)
            result = f'{battle_state.fighter2.name} wins (Opponent skipped)'
        elif fighter2_skip:
            damage = (battle_state.fighter1.damage * 
                     stats1['damage_multiplier'])
            points1 = damage
            battle_state.fighter1.add_score(points1)
            result = f'{battle_state.fighter1.name} wins (Opponent skipped)'
        else:
            result, points1, points2 = self._resolve_moves(
                battle_state, move1, move2, stats1, stats2
            )
        
        # Record result in battle state
        battle_state.record_result(result, points1, points2)
        
        # Update effects
        self.effect_manager.cleanup_expired_effects(battle_state)
        
        return result, points1, points2
    
    def _resolve_moves(self, 
                      battle_state: BattleState,
                      move1: str,
                      move2: str,
                      stats1: Dict[str, float],
                      stats2: Dict[str, float]) -> Tuple[str, float, float]:
        """Resolve the outcome of two moves considering modified stats"""
        points1 = 0
        points2 = 0
        
        if move1 == move2:
            result = 'Draw'
        elif self.does_move_win(move1, move2):
            damage = (battle_state.fighter1.damage * 
                     stats1['damage_multiplier'])
            points1 = damage
            battle_state.fighter1.add_score(points1)
            result = f'{battle_state.fighter1.name} wins'
        elif self.does_move_win(move2, move1):
            damage = (battle_state.fighter2.damage * 
                     stats2['damage_multiplier'])
            points2 = damage
            battle_state.fighter2.add_score(points2)
            result = f'{battle_state.fighter2.name} wins'
        else:
            result = 'No effect'
        
        return result, points1, points2