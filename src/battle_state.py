"""
Battle state management module that tracks and updates the complete state
of an ongoing battle, including round history, active effects, and current actions.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from .game_core import Fighter, PillzEffect

@dataclass
class RoundState:
    """Represents the state of a single round"""
    round_number: int
    fighter1_move: Optional[str] = None
    fighter2_move: Optional[str] = None
    fighter1_effect: Optional[PillzEffect] = None
    fighter2_effect: Optional[PillzEffect] = None
    result: Optional[str] = None
    points_gained1: float = 0
    points_gained2: float = 0

class BattleState:
    """
    Tracks and manages the complete state of a battle.
    This includes current round information, history, and active effects.
    """
    def __init__(self, fighter1: Fighter, fighter2: Fighter):
        self.fighter1 = fighter1
        self.fighter2 = fighter2
        self.current_round = 1
        self.max_rounds = 6
        self.round_history: List[RoundState] = []
        self.current_round_state = RoundState(round_number=self.current_round)
    
    def record_move(self, fighter: Fighter, move: str):
        """Record a fighter's move for the current round"""
        if fighter is self.fighter1:
            self.current_round_state.fighter1_move = move
        else:
            self.current_round_state.fighter2_move = move
    
    def record_effect(self, fighter: Fighter, effect: Optional[PillzEffect]):
        """Record a fighter's pillz effect for the current round"""
        if fighter is self.fighter1:
            self.current_round_state.fighter1_effect = effect
        else:
            self.current_round_state.fighter2_effect = effect
    
    def record_result(self, result: str, points1: float, points2: float):
        """Record the result of the current round"""
        self.current_round_state.result = result
        self.current_round_state.points_gained1 = points1
        self.current_round_state.points_gained2 = points2
        
        # Add current round to history
        self.round_history.append(self.current_round_state)
    
    def advance_round(self) -> bool:
        """Move to the next round and initialize new round state"""
        if self.current_round >= self.max_rounds:
            return False
        
        self.current_round += 1
        self.current_round_state = RoundState(round_number=self.current_round)
        return True
    
    def get_active_effects(self, fighter: Fighter) -> List[PillzEffect]:
        """Get all currently active effects for a fighter"""
        return fighter.active_effects
    
    def get_round_result_for_fighter(self, fighter: Fighter) -> str:
        """Get the result of the current round from a specific fighter's perspective"""
        result = self.current_round_state.result
        if not result:
            return 'none'
        if result == 'draw':
            return 'draw'
        
        if fighter is self.fighter1:
            return 'win' if 'fighter1 wins' in result.lower() else 'lose'
        else:
            return 'win' if 'fighter2 wins' in result.lower() else 'lose'
    
    def get_move_matchup(self) -> Optional[Tuple[str, str]]:
        """Get the current round's move matchup"""
        if (self.current_round_state.fighter1_move and 
            self.current_round_state.fighter2_move):
            return (self.current_round_state.fighter1_move,
                   self.current_round_state.fighter2_move)
        return None
    
    def get_win_counts(self) -> Dict[str, int]:
        """Get the number of rounds won by each fighter"""
        wins = {'fighter1': 0, 'fighter2': 0}
        
        for round_state in self.round_history:
            if 'fighter1 wins' in round_state.result.lower():
                wins['fighter1'] += 1
            elif 'fighter2 wins' in round_state.result.lower():
                wins['fighter2'] += 1
        
        return wins
    
    def get_streak(self, fighter: Fighter) -> int:
        """Get the current winning streak for a fighter"""
        streak = 0
        for round_state in reversed(self.round_history):
            result = round_state.result.lower() if round_state.result else ''
            is_win = (('fighter1 wins' in result and fighter is self.fighter1) or
                     ('fighter2 wins' in result and fighter is self.fighter2))
            
            if is_win:
                streak += 1
            else:
                break
        return streak
    
    def get_effect_history(self, fighter: Fighter) -> List[PillzEffect]:
        """Get the history of effects used by a fighter"""
        effects = []
        for round_state in self.round_history:
            effect = (round_state.fighter1_effect if fighter is self.fighter1 
                     else round_state.fighter2_effect)
            if effect:
                effects.append(effect)
        return effects
    
    def get_battle_summary(self) -> Dict:
        """Get a complete summary of the battle state"""
        win_counts = self.get_win_counts()
        return {
            'current_round': self.current_round,
            'fighter1_score': self.fighter1.score,
            'fighter2_score': self.fighter2.score,
            'fighter1_wins': win_counts['fighter1'],
            'fighter2_wins': win_counts['fighter2'],
            'fighter1_streak': self.get_streak(self.fighter1),
            'fighter2_streak': self.get_streak(self.fighter2),
            'round_history': self.round_history
        }