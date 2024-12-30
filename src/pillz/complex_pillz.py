# src/pillz/complex_pillz.py
import random
from src.effects.types import EffectDuration, EffectTarget, StatType, ActivationCondition
from typing import Optional
from src.effects.base import Effect, StatModifier
from .pillz import Pillz
from .types import PillzType, PillzActivationType

class SouthPacificPillz(Pillz):
    """Implementation of South Pacific pillz (Dexterity effect)"""
    def __init__(self):
        super().__init__(
            type=PillzType.SOUTH_PACIFIC,
            name="South Pacific",
            activation_type=PillzActivationType.ANY_MOVE,
            description="Skip the round but double the Damage value for the first consecutive round that comes as a win"
        )

    def initialize_effect(self) -> Effect:
        return Effect(
            name="Dexterity",
            duration=EffectDuration.NEXT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[
                StatModifier(
                    stat_type=StatType.DAMAGE,
                    value=2,  # Double damage
                    is_random=False
                )
            ],
            pending_condition="WIN"  # Will activate on next win
        )

class AprilPillz(Pillz):
    """Implementation of April pillz (Rainbow effect)"""
    def __init__(self):
        super().__init__(
            type=PillzType.APRIL,
            name="April",
            activation_type=PillzActivationType.ANY_MOVE,
            description="Takes a random effect out of: Brave, Resolve, Don't Cry"
        )
        # Store possible effects for random selection
        self.available_effects = [
            ("Brave", self._create_brave_effect),
            ("Resolve", self._create_resolve_effect),
            ("Don't Cry", self._create_dont_cry_effect)
        ]

    def _create_brave_effect(self) -> Effect:
        return Effect(
            name="Rainbow(Brave)",
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

    def _create_resolve_effect(self) -> Effect:
        return Effect(
            name="Rainbow(Resolve)",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[
                StatModifier(
                    stat_type=StatType.RESISTANCE,
                    value=10,
                    is_random=True
                )
            ]
        )

    def _create_dont_cry_effect(self) -> Effect:
        return Effect(
            name="Rainbow(Don't Cry)",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.LOSE_ONLY,
            modifiers=[
                StatModifier(
                    stat_type=StatType.RESISTANCE,
                    value=10,
                    is_random=False
                )
            ]
        )

    def initialize_effect(self) -> Effect:
        # Explicitly choose from available effects using random index
        effect_name, effect_creator = random.choice(self.available_effects)
        return effect_creator()

    def activate(self, won_round: bool) -> Optional[Effect]:
        """Override activate to create new effect each time (for testing)"""
        if not self.can_activate(won_round):
            return None
            
        # Create new effect each time for testing randomization
        self._effect = self.initialize_effect()
        return self._effect
    
class JurassicPillz(Pillz):
    """Implementation of Jurassic pillz (Spike effect)"""
    def __init__(self):
        super().__init__(
            type=PillzType.JURASSIC,
            name="Jurassic",
            activation_type=PillzActivationType.LOSE_MOVE_ONLY,
            description="Copies the opponent's Damage value and all effects they used in the round and applies these back to them"
        )

    def initialize_effect(self) -> Effect:
        return Effect(
            name="Spike",
            duration=EffectDuration.CURRENT,
            target=EffectTarget.OPPONENT,
            activation=ActivationCondition.LOSE_ONLY,
            modifiers=[
                StatModifier(
                    stat_type=StatType.DAMAGE,
                    value=-1,  # Special value to indicate copying
                    is_random=False
                )
            ]
        )

    def activate(self, won_round: bool) -> Optional[Effect]:
        if not self.can_activate(won_round):
            return None
        self._effect = self.initialize_effect()
        return self._effect