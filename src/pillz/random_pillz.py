# src/pillz/random_pillz.py
import random
from typing import Optional
from src.effects.types import EffectDuration, EffectTarget, StatType, ActivationCondition
from src.effects.base import Effect, StatModifier
from .pillz import Pillz
from .types import PillzType, PillzActivationType

class SailorMoonPillz(Pillz):
    """Implementation of Sailor Moon pillz (Resolve effect)"""
    def __init__(self):
        super().__init__(
            type=PillzType.SAILOR_MOON,
            name="Sailor Moon",
            activation_type=PillzActivationType.ANY_MOVE,
            description="Increases Resistance value by a random number between 1 and 10 permanently"
        )

    def initialize_effect(self) -> Effect:
        return Effect(
            name="Resolve",
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

    def activate(self, won_round: bool) -> Optional[Effect]:
        if not self.can_activate(won_round):
            return None
        self._effect = self.initialize_effect()
        return self._effect

class GothamPillz(Pillz):
    """Implementation of Gotham pillz (Weakness effect)"""
    def __init__(self):
        super().__init__(
            type=PillzType.GOTHAM,
            name="Gotham",
            activation_type=PillzActivationType.ANY_MOVE,
            description="Decreases opponent's Resistance value by a random number between 1 and 10 permanently"
        )

    def initialize_effect(self) -> Effect:
        return Effect(
            name="Weakness",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.OPPONENT,
            activation=ActivationCondition.ANY,
            modifiers=[
                StatModifier(
                    stat_type=StatType.RESISTANCE,
                    value=10,
                    is_random=True
                )
            ]
        )

    def activate(self, won_round: bool) -> Optional[Effect]:
        if not self.can_activate(won_round):
            return None
        self._effect = self.initialize_effect()
        return self._effect

class AlienAttackPillz(Pillz):
    """Implementation of Alien Attack pillz (Rust effect)"""
    def __init__(self):
        super().__init__(
            type=PillzType.ALIEN_ATTACK,
            name="Alien Attack",
            activation_type=PillzActivationType.ANY_MOVE,
            description="Decreases opponent's Damage value by a random number between 1 and 10 permanently"
        )

    def initialize_effect(self) -> Effect:
        return Effect(
            name="Rust",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.OPPONENT,
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
        if not self.can_activate(won_round):
            return None
        self._effect = self.initialize_effect()
        return self._effect

class OctoberPillz(Pillz):
    """Implementation of October pillz (Sadness effect)"""
    def __init__(self):
        super().__init__(
            type=PillzType.OCTOBER,
            name="October",
            activation_type=PillzActivationType.ANY_MOVE,
            description="Takes a random effect out of: Rust, Weakness and applies on Opponent"
        )
        self.available_effects = [
            ("Rust", self._create_rust_effect),
            ("Weakness", self._create_weakness_effect)
        ]

    def _create_rust_effect(self) -> Effect:
        return Effect(
            name="Sadness(Rust)",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.OPPONENT,
            activation=ActivationCondition.ANY,
            modifiers=[
                StatModifier(
                    stat_type=StatType.DAMAGE,
                    value=10,
                    is_random=True
                )
            ]
        )

    def _create_weakness_effect(self) -> Effect:
        return Effect(
            name="Sadness(Weakness)",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.OPPONENT,
            activation=ActivationCondition.ANY,
            modifiers=[
                StatModifier(
                    stat_type=StatType.RESISTANCE,
                    value=10,
                    is_random=True
                )
            ]
        )

    def initialize_effect(self) -> Effect:
        effect_name, effect_creator = random.choice(self.available_effects)
        return effect_creator()

    def activate(self, won_round: bool) -> Optional[Effect]:
        if not self.can_activate(won_round):
            return None
        self._effect = self.initialize_effect()
        return self._effect