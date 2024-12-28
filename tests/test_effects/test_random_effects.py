import pytest, random
from src.effects.types import EffectDuration, EffectTarget, StatType, ActivationCondition
from src.effects.base import Effect, StatModifier
from src.effects.manager import EffectManager

class TestRandomEffects:
    @pytest.fixture
    def manager(self):
        return EffectManager()

    @pytest.fixture
    def fighter_id(self):
        return "fighter1"

    def test_rainbow_effect_selection(self, manager, fighter_id):
        """Test Rainbow random effect selection"""
        # Define possible effects for Rainbow
        rainbow_effects = [
            Effect(
                name="Brave",
                duration=EffectDuration.PERMANENT,
                target=EffectTarget.SELF,
                activation=ActivationCondition.ANY,
                modifiers=[StatModifier(StatType.DAMAGE, 10, is_random=True)]
            ),
            Effect(
                name="Resolve",
                duration=EffectDuration.PERMANENT,
                target=EffectTarget.SELF,
                activation=ActivationCondition.ANY,
                modifiers=[StatModifier(StatType.RESISTANCE, 10, is_random=True)]
            ),
            Effect(
                name="Don't cry",
                duration=EffectDuration.PERMANENT,
                target=EffectTarget.SELF,
                activation=ActivationCondition.LOSE_ONLY,
                modifiers=[StatModifier(StatType.RESISTANCE, 10, is_random=False)]
            )
        ]
        
        # Create Rainbow effect
        rainbow_effect = Effect(
            name="Rainbow",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[]
        )
        
        # Simulate random selection and application
        import random
        selected_effect = random.choice(rainbow_effects)
        rainbow_effect.modifiers = selected_effect.modifiers
        rainbow_effect.name = f"Rainbow({selected_effect.name})"
        
        manager.add_effect(fighter_id, rainbow_effect)
        rainbow_effect.apply(current_round=1)
        
        # Log the applied effect
        for modifier in rainbow_effect.modifiers:
            value = modifier.get_value()
            manager.log_effect(1, rainbow_effect, value, modifier.stat_type, fighter_id)
        
        # Verify one effect was chosen and applied
        assert len(manager.get_active_effects(fighter_id)) == 1
        history = manager.effect_history
        assert len(history) == 1

    def test_sadness_effect_selection(self, manager, fighter_id):
        """Test Sadness random effect selection"""
        sadness_effects = [
            Effect(
                name="Rust",
                duration=EffectDuration.PERMANENT,
                target=EffectTarget.OPPONENT,
                activation=ActivationCondition.ANY,
                modifiers=[StatModifier(StatType.DAMAGE, 10, is_random=True)]
            ),
            Effect(
                name="Weakness",
                duration=EffectDuration.PERMANENT,
                target=EffectTarget.OPPONENT,
                activation=ActivationCondition.ANY,
                modifiers=[StatModifier(StatType.RESISTANCE, 10, is_random=True)]
            )
        ]
        
        # Create Sadness effect
        sadness_effect = Effect(
            name="Sadness",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.OPPONENT,
            activation=ActivationCondition.ANY,
            modifiers=[]
        )
        
        # Simulate random selection and application
        selected_effect = random.choice(sadness_effects)
        sadness_effect.modifiers = selected_effect.modifiers
        sadness_effect.name = f"Sadness({selected_effect.name})"
        
        manager.add_effect(fighter_id, sadness_effect)
        sadness_effect.apply(current_round=1)
        
        # Log the applied effect
        for modifier in sadness_effect.modifiers:
            value = modifier.get_value()
            manager.log_effect(1, sadness_effect, value, modifier.stat_type, fighter_id)
        
        # Verify one effect was chosen and applied
        assert len(manager.get_active_effects(fighter_id)) == 1
        history = manager.effect_history
        assert len(history) == 1