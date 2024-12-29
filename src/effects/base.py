from dataclasses import dataclass
from typing import Optional, List, Dict, Callable
import random
from .types import EffectDuration, EffectTarget, StatType, ActivationCondition, EffectValue

@dataclass
class StatModifier:
    stat_type: StatType
    value: EffectValue
    is_random: bool = False
    _cached_random_value: Optional[int] = None
    _testing_mode: bool = False  # New flag for testing

    def get_value(self) -> int:
        """Get the modifier value"""
        if not self.is_random:
            return self.value if isinstance(self.value, int) else -1  # -1 signals HALF
        
        if self._testing_mode:
            # In testing mode, always generate new value
            return random.randint(1, self.value if isinstance(self.value, int) else 10)
        
        # In normal mode, cache and reuse the value
        if self._cached_random_value is None:
            self._cached_random_value = random.randint(1, self.value if isinstance(self.value, int) else 10)
        return self._cached_random_value

    def set_testing_mode(self, enabled: bool = True):
        """Enable or disable testing mode"""
        self._testing_mode = enabled
        if enabled:
            self._cached_random_value = None  # Clear cache when entering testing mode

@dataclass
class Effect:
    name: str
    duration: EffectDuration
    target: EffectTarget
    activation: ActivationCondition
    modifiers: List[StatModifier]
    
    # State tracking
    is_active: bool = False
    pending_condition: Optional[str] = None
    applied_at_round: Optional[int] = None
    expires_at_round: Optional[int] = None

    def can_activate(self, won_round: bool) -> bool:
        if self.activation == ActivationCondition.ANY:
            return True
        if self.activation == ActivationCondition.WIN_ONLY:
            return won_round
        if self.activation == ActivationCondition.LOSE_ONLY:
            return not won_round
        return False

    def apply(self, current_round: int) -> None:
        self.is_active = True
        self.applied_at_round = current_round
        if self.duration == EffectDuration.CURRENT:
            self.expires_at_round = current_round

    def should_expire(self, current_round: int) -> bool:
        if not self.is_active:
            return False
        if self.duration == EffectDuration.PERMANENT:
            return False
        return self.expires_at_round == current_round