"""
Core game mechanics module containing fundamental classes and data structures.
Enhanced with flexible effect system to support complex pillz mechanics.
"""

from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from uuid import uuid4

class PillzType(Enum):
    """Enumeration of available pillz types"""
    NONE = auto()
    SOUTH_PACIFIC = auto()
    NORDIC_SHIELD = auto()

class EffectType(Enum):
    """Categories of effects that pillz can have"""
    NONE = auto()
    DAMAGE = auto()
    RESISTANCE = auto()
    SKIP = auto()
    COUNTER = auto()

class ActivationCondition(Enum):
    """When an effect can be activated"""
    ALWAYS = auto()
    ON_WIN = auto()
    ON_LOSE = auto()
    ON_DRAW = auto()

@dataclass
class PillzEffect:
    """
    Represents a complex effect that a pillz can have on a fighter.
    Supports conditional activation and multi-round effects.
    """
    name: str
    duration: int  # Number of rounds this effect lasts
    activation_condition: ActivationCondition
    effect_type: EffectType
    priority: int  # Higher priority effects are processed first
    counters: List[EffectType] = field(default_factory=list)
    round_effects: Dict[int, Dict[str, float]] = field(default_factory=dict)
    effect_modifiers: Dict[str, Callable] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))  # Unique identifier for each effect

    def is_active(self, current_round: int, activation_round: int, round_result: str) -> bool:
        """Check if effect should be active based on conditions"""
        rounds_active = current_round - activation_round
        if rounds_active >= self.duration:
            return False
        
        if self.activation_condition == ActivationCondition.ALWAYS:
            return True
        elif self.activation_condition == ActivationCondition.ON_WIN:
            return round_result == 'win'
        elif self.activation_condition == ActivationCondition.ON_LOSE:
            return round_result == 'lose'
        elif self.activation_condition == ActivationCondition.ON_DRAW:
            return round_result == 'draw'
        
        return False
    
    def get_effect_values(self, rounds_active: int) -> Dict[str, float]:
        """Get effect values for the current round"""
        if rounds_active not in self.round_effects:
            return {
                'damage_multiplier': 1.0,
                'resistance_multiplier': 1.0,
                'skip_round': False
            }
        
        return self.round_effects[rounds_active]

@dataclass
class Fighter:
    """
    Represents a fighter with their stats and active effects.
    Enhanced to handle complex effect tracking.
    """
    name: str
    damage: int
    resistance: int
    score: float = 0
    active_effects: List[PillzEffect] = field(default_factory=list)
    _effect_activation_rounds: Dict[str, int] = field(default_factory=dict)  # Using effect ID as key
    
    def apply_pillz(self, pillz_type: PillzType, current_round: int):
        """Apply a pillz effect to the fighter"""
        effect = Pillz.get_effect(pillz_type)
        if effect:
            self.active_effects.append(effect)
            self._effect_activation_rounds[effect.id] = current_round
    
    def update_effects(self, current_round: int, round_result: str):
        """Update active effects based on battle results"""
        active_effects = []
        active_rounds = {}
        
        for effect in self.active_effects:
            activation_round = self._effect_activation_rounds.get(effect.id)
            if activation_round is not None and effect.is_active(current_round, activation_round, round_result):
                active_effects.append(effect)
                active_rounds[effect.id] = activation_round
        
        self.active_effects = active_effects
        self._effect_activation_rounds = active_rounds
    
    def calculate_damage(self, opponent: 'Fighter', round_result: str) -> float:
        """Calculate effective damage considering all active effects"""
        damage_multiplier = 1.0
        
        sorted_effects = sorted(
            self.active_effects,
            key=lambda x: x.priority,
            reverse=True
        )
        
        for effect in sorted_effects:
            if effect.effect_type == EffectType.DAMAGE:
                activation_round = self._effect_activation_rounds.get(effect.id)
                if activation_round is not None:
                    rounds_active = len(self.active_effects)
                    values = effect.get_effect_values(rounds_active)
                    damage_multiplier *= values.get('damage_multiplier', 1.0)
        
        return self.damage * damage_multiplier
    
    def get_effect_activation_round(self, effect: PillzEffect) -> Optional[int]:
        """Get the activation round for a specific effect"""
        return self._effect_activation_rounds.get(effect.id)
    
    def add_score(self, points: float):
        """Add points to fighter's score"""
        self.score += points
    
    def reset(self):
        """Reset fighter's score and effects"""
        self.score = 0
        self.active_effects = []
        self._effect_activation_rounds = {}

class Pillz:
    """Defines all available pillz and their effects"""
    @staticmethod
    def get_effect(pillz_type: PillzType) -> Optional[PillzEffect]:
        """Create and return a pillz effect based on type"""
        if pillz_type == PillzType.SOUTH_PACIFIC:
            return PillzEffect(
                name="South Pacific",
                duration=2,
                activation_condition=ActivationCondition.ALWAYS,
                effect_type=EffectType.DAMAGE,
                priority=1,
                round_effects={
                    0: {'damage_multiplier': 0.0, 'skip_round': True},
                    1: {'damage_multiplier': 2.0}
                }
            )
        elif pillz_type == PillzType.NORDIC_SHIELD:
            return PillzEffect(
                name="Nordic Shield",
                duration=2,
                activation_condition=ActivationCondition.ALWAYS,
                effect_type=EffectType.RESISTANCE,
                priority=1,
                round_effects={
                    0: {'resistance_multiplier': 2.0},
                    1: {'resistance_multiplier': 0.0}
                }
            )
        return None