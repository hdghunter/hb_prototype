"""
Core game mechanics module with expanded pillz system.
"""

import random
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from uuid import uuid4

class PillzType(Enum):
    """Enumeration of available pillz types"""
    NONE = auto()
    SOUTH_PACIFIC = auto()
    NORDIC_SHIELD = auto()
    GODZILLA_CAKE = auto()
    KISS = auto()
    SAILOR_MOON = auto()

class EffectType(Enum):
    """Categories of effects that pillz can have"""
    NONE = auto()
    DAMAGE = auto()
    RESISTANCE = auto()
    SKIP = auto()
    COUNTER = auto()
    PERMANENT_DAMAGE = auto()
    PERMANENT_RESISTANCE = auto()

class ActivationCondition(Enum):
    """When an effect can be activated"""
    ALWAYS = auto()
    ON_WIN = auto()
    ON_LOSE = auto()
    ON_DRAW = auto()

@dataclass
class PillzEffect:
    """Represents a complex effect that a pillz can have on a fighter"""
    name: str
    duration: int  # Number of rounds this effect lasts, -1 for permanent
    activation_condition: ActivationCondition
    effect_type: EffectType
    priority: int
    permanent_bonus: float = 0  # For permanent stat increases
    counters: List[EffectType] = field(default_factory=list)
    round_effects: Dict[int, Dict[str, float]] = field(default_factory=dict)
    effect_modifiers: Dict[str, Callable] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))

    def is_active(self, current_round: int, activation_round: int, round_result: str) -> bool:
        if self.duration == -1:  # Permanent effect
            return True
        rounds_active = current_round - activation_round
        if rounds_active >= self.duration and self.duration != -1:
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
        if rounds_active not in self.round_effects:
            return {
                'damage_multiplier': 1.0,
                'resistance_multiplier': 1.0,
                'skip_round': False,
                'permanent_damage_bonus': self.permanent_bonus if self.effect_type == EffectType.PERMANENT_DAMAGE else 0,
                'permanent_resistance_bonus': self.permanent_bonus if self.effect_type == EffectType.PERMANENT_RESISTANCE else 0
            }
        
        return self.round_effects[rounds_active]

@dataclass
class Fighter:
    """Represents a fighter with their stats and active effects"""
    name: str
    damage: int
    resistance: int
    score: float = 0
    permanent_damage_bonus: float = 0
    permanent_resistance_bonus: float = 0
    active_effects: List[PillzEffect] = field(default_factory=list)
    _effect_activation_rounds: Dict[str, int] = field(default_factory=dict)

    def add_score(self, points: float):
        """Add points to fighter's score"""
        self.score += points

    def apply_pillz(self, pillz_type: PillzType, current_round: int):
        """Apply a pillz effect to the fighter"""
        effect = Pillz.get_effect(pillz_type)
        if effect:
            # Handle permanent stat bonuses
            if effect.effect_type == EffectType.PERMANENT_DAMAGE:
                self.permanent_damage_bonus += effect.permanent_bonus
            elif effect.effect_type == EffectType.PERMANENT_RESISTANCE:
                self.permanent_resistance_bonus += effect.permanent_bonus
            
            self.active_effects.append(effect)
            self._effect_activation_rounds[effect.id] = current_round

    def get_total_damage(self) -> float:
        """Get total damage including permanent bonuses"""
        return self.damage + self.permanent_damage_bonus

    def get_total_resistance(self) -> float:
        """Get total resistance including permanent bonuses"""
        return self.resistance + self.permanent_resistance_bonus

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
            if effect.effect_type in [EffectType.DAMAGE, EffectType.PERMANENT_DAMAGE]:
                activation_round = self._effect_activation_rounds.get(effect.id)
                if activation_round is not None:
                    rounds_active = len(self.active_effects)
                    values = effect.get_effect_values(rounds_active)
                    damage_multiplier *= values.get('damage_multiplier', 1.0)
        
        return self.get_total_damage() * damage_multiplier

    def reset(self):
        """Reset fighter's score and effects"""
        self.score = 0
        self.permanent_damage_bonus = 0
        self.permanent_resistance_bonus = 0
        self.active_effects = []
        self._effect_activation_rounds = {}

class Pillz:
    """Defines all available pillz and their effects"""
    @staticmethod
    def get_effect(pillz_type: PillzType) -> Optional[PillzEffect]:
        if pillz_type == PillzType.SOUTH_PACIFIC:
            return PillzEffect(
                name="South Pacific (Dexterity)",
                duration=2,  # Effect lasts for current and next round
                activation_condition=ActivationCondition.ALWAYS,  # Activates on any move
                effect_type=EffectType.DAMAGE,
                priority=1,
                round_effects={
                    0: {  # Current round
                        'damage_multiplier': 0.0,  # No damage dealt
                        'skip_round': True,  # Force round skip
                    },
                    1: {  # Next round
                        'damage_multiplier': 2.0,  # Double damage
                        'skip_round': False
                    }
                }
            )
        elif pillz_type == PillzType.NORDIC_SHIELD:
            return PillzEffect(
                name="Nordic Shield (Shield)",
                duration=2,  # Effect lasts for current and next round
                activation_condition=ActivationCondition.ON_LOSE,  # Only activates on losing move
                effect_type=EffectType.RESISTANCE,
                priority=1,
                round_effects={
                    0: {  # Current round - no effect
                        'resistance_multiplier': 1.0,
                        'skip_round': False
                    },
                    1: {  # Next round - double resistance
                        'resistance_multiplier': 2.0,
                        'skip_round': False
                    }
                }
            )
        elif pillz_type == PillzType.GODZILLA_CAKE:
            bonus = random.randint(1, 10)
            return PillzEffect(
                name=f"Godzilla Cake (Brave +{bonus} DMG)",
                duration=-1,  # Permanent effect
                activation_condition=ActivationCondition.ALWAYS,
                effect_type=EffectType.PERMANENT_DAMAGE,
                priority=2,
                permanent_bonus=bonus,
                round_effects={
                    0: {'damage_multiplier': 1.0}
                }
            )
        elif pillz_type == PillzType.KISS:
            return PillzEffect(
                name="Kiss (Don't Cry +10 RES)",
                duration=-1,  # Permanent effect
                activation_condition=ActivationCondition.ON_LOSE,
                effect_type=EffectType.PERMANENT_RESISTANCE,
                priority=2,
                permanent_bonus=10,
                round_effects={
                    0: {'resistance_multiplier': 1.0}
                }
            )
        elif pillz_type == PillzType.SAILOR_MOON:
            bonus = random.randint(1, 10)
            return PillzEffect(
                name=f"Sailor Moon (Resolve +{bonus} RES)",
                duration=-1,  # Permanent effect
                activation_condition=ActivationCondition.ALWAYS,
                effect_type=EffectType.PERMANENT_RESISTANCE,
                priority=2,
                permanent_bonus=bonus,
                round_effects={
                    0: {'resistance_multiplier': 1.0}
                }
            )
        return None