"""
Battle system module integrating state management and effect processing.
"""
import random
from typing import List, Dict, Tuple
from .game_core import Fighter, PillzType
from .battle_state import BattleState
from .effect_manager import EffectManager

class BattleSystem:
    """Implements the core battle mechanics and coordinates game components"""
    
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
    
    def _get_base_round_result(self, move1: str, move2: str) -> str:
        """Determine the base outcome before effects are applied"""
        if move1 == move2:
            return 'draw'
        elif self.does_move_win(move1, move2):
            return 'fighter1 wins'
        elif self.does_move_win(move2, move1):
            return 'fighter2 wins'
        return 'no effect'
    
    def process_round(self, 
                     battle_state: BattleState,
                     move1: str, 
                     move2: str) -> Tuple[str, float, float]:
        """Process a single round of combat"""
        # Record moves in battle state
        battle_state.record_move(battle_state.fighter1, move1)
        battle_state.record_move(battle_state.fighter2, move2)
        
        # Determine the base outcome before effects
        base_result = self._get_base_round_result(move1, move2)
        
        # Process all active effects with this pre-determined result
        modified_stats = self.effect_manager.process_effects(battle_state)
        
        # Get modified stats for both fighters
        stats1 = modified_stats.get('fighter1', {})
        stats2 = modified_stats.get('fighter2', {})
        
        # Check for skipped rounds due to effects (South Pacific)
        fighter1_skip = stats1.get('skip_round', False)
        fighter2_skip = stats2.get('skip_round', False)
        
        # Initialize points
        points1 = 0
        points2 = 0
        
        # Determine final round result
        if fighter1_skip and fighter2_skip:
            result = 'Both fighters skip (Pillz effect)'
        elif fighter1_skip:
            damage = (battle_state.fighter2.damage * 
                     stats2.get('damage_multiplier', 1.0))
            points2 = damage
            battle_state.fighter2.add_score(points2)
            result = f'{battle_state.fighter2.name} wins (Opponent skipped)'
        elif fighter2_skip:
            damage = (battle_state.fighter1.damage * 
                     stats1.get('damage_multiplier', 1.0))
            points1 = damage
            battle_state.fighter1.add_score(points1)
            result = f'{battle_state.fighter1.name} wins (Opponent skipped)'
        else:
            result, points1, points2 = self._resolve_moves(
                battle_state, move1, move2, stats1, stats2
            )
        
        # Record result in battle state
        battle_state.record_result(result, points1, points2)
        
        # Update effects based on the final result
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
            damage = (battle_state.fighter1.get_total_damage() * 
                     stats1.get('damage_multiplier', 1.0))
            points1 = damage
            battle_state.fighter1.add_score(points1)
            result = f'{battle_state.fighter1.name} wins'
        elif self.does_move_win(move2, move1):
            damage = (battle_state.fighter2.get_total_damage() * 
                     stats2.get('damage_multiplier', 1.0))
            points2 = damage
            battle_state.fighter2.add_score(points2)
            result = f'{battle_state.fighter2.name} wins'
        else:
            result = 'No effect'
        
        return result, points1, points2

    def simulate_single_battle(self, fighter1: Fighter, fighter2: Fighter) -> List[Dict]:
        """Simulate a complete battle between two fighters"""
        battle_state = BattleState(fighter1, fighter2)
        battle_log = []
        
        while True:
            move1 = random.choice(self.moves)
            move2 = random.choice(self.moves)
            
            result, points1, points2 = self.process_round(
                battle_state, move1, move2
            )
            
            battle_log.append({
                'round': battle_state.current_round,
                'move1': move1,
                'move2': move2,
                'fighter1_effect': (battle_state.current_round_state.fighter1_effect.name 
                                  if battle_state.current_round_state.fighter1_effect 
                                  else 'None'),
                'fighter2_effect': (battle_state.current_round_state.fighter2_effect.name
                                  if battle_state.current_round_state.fighter2_effect
                                  else 'None'),
                'result': result,
                'fighter1_score': fighter1.score,
                'fighter2_score': fighter2.score,
                'points_gained1': points1,
                'points_gained2': points2
            })
            
            if not battle_state.advance_round():
                break
        
        return battle_log