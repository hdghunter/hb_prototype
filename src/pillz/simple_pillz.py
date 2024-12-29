# src/pillz/simple_pillz.py
from typing import Optional
from src.effects.types import EffectDuration, EffectTarget, StatType, ActivationCondition
from src.effects.base import Effect, StatModifier
from .pillz import Pillz
from .types import PillzType, PillzActivationType

class GodzillaCakePillz(Pillz):
    """Implementation of Godzilla Cake pillz (Brave effect)"""
    def __init__(self):
        super().__init__(
            type=PillzType.GODZILLA_CAKE,
            name="Godzilla Cake",
            activation_type=PillzActivationType.ANY_MOVE,
            description="Increases Damage value by a random number between 1 and 10 permanently"
        )

    def initialize_effect(self) -> Effect:
        return Effect(
            name="Brave",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[
                StatModifier(
                    stat_type=StatType.DAMAGE,
                    value=10,
                    is_random=True
                )
            ]
        )

    def activate(self, won_round: bool) -> Optional[Effect]:
        """Override activate to create new effect each time (for testing)"""
        if not self.can_activate(won_round):
            return None
        
        # Create new effect each time for testing randomization
        self._effect = self.initialize_effect()
        return self._effect