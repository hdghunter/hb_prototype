"""
Core game mechanics module containing fundamental classes and data structures.
This module defines the basic building blocks of the game: fighters, pillz effects,
and their interactions.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum, auto

class PillzType(Enum):
    """
    Enumeration of available pillz types in the game.
    Using Enum ensures type safety and prevents invalid pillz types.
    """
    NONE = auto()
    SOUTH_PACIFIC = auto()
    NORDIC_SHIELD = auto()

@dataclass
class PillzEffect:
    """
    Represents the effect of a pillz on a fighter.
    Using dataclass for automatic initialization and representation of effect properties.
    
    Attributes:
        name: Descriptive name of the effect
        damage_multiplier: How much to multiply damage by this round
        resistance_multiplier: How much to multiply resistance by this round
        skip_round: Whether the fighter must skip their turn
        next_round_damage_multiplier: Damage multiplier for the next round
        next_round_resistance_multiplier: Resistance multiplier for the next round
    """
    name: str
    damage_multiplier: float = 1.0
    resistance_multiplier: float = 1.0
    skip_round: bool = False
    next_round_damage_multiplier: float = 1.0
    next_round_resistance_multiplier: float = 1.0

class Pillz:
    """
    Defines all available pillz and their effects.
    This class serves as a factory for creating pillz effects.
    """
    @staticmethod
    def get_effect(pillz_type: PillzType) -> PillzEffect:
        """
        Creates and returns a PillzEffect based on the pillz type.
        
        Args:
            pillz_type: The type of pillz to create an effect for
            
        Returns:
            A PillzEffect instance with the appropriate modifiers
        """
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
    
    Attributes:
        name: Fighter's name
        damage: Base damage value
        resistance: Base resistance value
        health: Current health points
        initial_health: Starting health points (for resets)
        current_effect: Currently active pillz effect
        next_round_effect: Effect queued for the next round
    """
    name: str
    damage: int
    resistance: int
    health: float = 100
    initial_health: float = 100
    current_effect: Optional[PillzEffect] = None
    next_round_effect: Optional[PillzEffect] = None
    
    def calculate_damage(self, opponent: 'Fighter') -> float:
        """
        Calculate effective damage considering opponent's resistance and pillz effects.
        
        Args:
            opponent: The defending fighter
            
        Returns:
            The final damage value after applying all modifiers
        """
        damage_multiplier = 1.0
        if self.current_effect:
            damage_multiplier *= self.current_effect.damage_multiplier
        
        base_damage = self.damage * damage_multiplier
        
        opponent_resistance = opponent.resistance
        if opponent.current_effect:
            opponent_resistance *= opponent.current_effect.resistance_multiplier
            
        return base_damage * (1 - min(opponent_resistance/100, 1))
    
    def apply_pillz(self, pillz_type: PillzType):
        """
        Apply a pillz effect to the fighter.
        
        Args:
            pillz_type: The type of pillz to apply
        """
        self.current_effect = Pillz.get_effect(pillz_type)
    
    def update_effects(self):
        """
        Update effects after each round.
        Handles transitioning from current effects to next round effects.
        """
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
        """Reset fighter's health and effects to initial state."""
        self.health = self.initial_health
        self.current_effect = None
        self.next_round_effect = None