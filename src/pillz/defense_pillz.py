# src/pillz/defense_pillz.py
from typing import Optional
from src.effects.types import EffectDuration, EffectTarget, StatType, ActivationCondition
from src.effects.base import Effect, StatModifier
from .pillz import Pillz
from .types import PillzType, PillzActivationType

class NordicShieldPillz(Pillz):
    """Implementation of Nordic Shield pillz (Shield effect)"""
    def __init__(self):
        super().__init__(
            type=PillzType.NORDIC_SHIELD,
            name="Nordic Shield",
            activation_type=PillzActivationType.LOSE_MOVE_ONLY,
            description="Doubles the fighter's resistance value for next round"
        )

    def initialize_effect(self) -> Effect:
        return Effect(
            name="Shield",
            duration=EffectDuration.NEXT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.LOSE_ONLY,
            modifiers=[
                StatModifier(
                    stat_type=StatType.RESISTANCE,
                    value=2,  # Multiplier for doubling
                    is_random=False
                )
            ]
        )

    def activate(self, won_round: bool) -> Optional[Effect]:
        if not self.can_activate(won_round):
            return None
        
        self._effect = self.initialize_effect()
        return self._effect