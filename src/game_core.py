"""
Core game mechanics module containing fundamental classes and data structures.
Updated to use scoring system instead of health depletion.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum, auto

class PillzType(Enum):
    """Enumeration of available pillz types in the game."""
    NONE = auto()
    SOUTH_PACIFIC = auto()
    NORDIC_SHIELD = auto()

@dataclass
class PillzEffect:
    """Represents the effect of a pillz on a fighter"""
    name: str
    damage_multiplier: float = 1.0
    resistance_multiplier: float = 1.0
    skip_round: bool = False
    next_round_damage_multiplier: float = 1.0
    next_round_resistance_multiplier: float = 1.0

class Pillz:
    """Defines all available pillz and their effects"""
    @staticmethod
    def get_effect(pillz_type: PillzType) -> PillzEffect:
        if pillz_type == PillzType.SOUTH_PACIFIC:
            return PillzEffect(
                name="South Pacific",
                damage_multiplier=0,  # Skip this round
                skip_round=True,
                next_round_damage_multiplier=2.0  # Double damage next round
            )
        elif pillz_type == PillzType.NORDIC_SHIELD:
            return PillzEffect(
                name="Nordic Shield",
                resistance_multiplier=2.0,  # Double resistance this round
                next_round_resistance_multiplier=0  # No resistance next round
            )
        return PillzEffect(name="None")

@dataclass
class Fighter:
    """
    Represents a fighter in the game with their stats and current state.
    Updated to use score instead of health.
    """
    name: str
    damage: int
    resistance: int
    score: float = 0  # New attribute for point accumulation
    current_effect: Optional[PillzEffect] = None
    next_round_effect: Optional[PillzEffect] = None
    
    def calculate_damage(self, opponent: 'Fighter') -> float:
        """
        Calculate effective damage considering opponent's resistance and pillz effects.
        This now represents potential points to be gained rather than health reduction.
        """
        damage_multiplier = 1.0
        if self.current_effect:
            damage_multiplier *= self.current_effect.damage_multiplier
        
        base_damage = self.damage * damage_multiplier
        
        opponent_resistance = opponent.resistance
        if opponent.current_effect:
            opponent_resistance *= opponent.current_effect.resistance_multiplier
            
        return base_damage * (1 - min(opponent_resistance/100, 1))
    
    def add_score(self, points: float):
        """Add points to fighter's score from winning a round"""
        self.score += points
    
    def apply_pillz(self, pillz_type: PillzType):
        """Apply a pillz effect to the fighter"""
        self.current_effect = Pillz.get_effect(pillz_type)
    
    def update_effects(self):
        """Update effects after each round"""
        if self.current_effect and self.current_effect.next_round_damage_multiplier != 1.0:
            self.next_round_effect = PillzEffect(
                name=f"{self.current_effect.name} (Next Round)",
                damage_multiplier=self.current_effect.next_round_damage_multiplier
            )
        elif self.current_effect and self.current_effect.next_round_resistance_multiplier != 1.0:
            self.next_round_effect = PillzEffect(
                name=f"{self.current_effect.name} (Next Round)",
                resistance_multiplier=self.current_effect.next_round_resistance_multiplier
            )
        
        self.current_effect = self.next_round_effect
        self.next_round_effect = None
    
    def reset(self):
        """Reset fighter's score and effects"""
        self.score = 0
        self.current_effect = None
        self.next_round_effect = None