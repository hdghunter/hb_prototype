import pytest
from src.effects.types import EffectDuration, EffectTarget, StatType, ActivationCondition
from src.effects.base import Effect, StatModifier
from src.effects.manager import EffectManager

class TestPermanentEffects:
    @pytest.fixture
    def manager(self):
        return EffectManager()

    @pytest.fixture
    def fighter_id(self):
        return "fighter1"
        
    def test_multiple_brave_accumulation(self, manager, fighter_id):
        """Test accumulation of multiple Brave effects"""
        brave_effects = []
        for i in range(3):
            brave_effect = Effect(
                name=f"Brave_{i}",
                duration=EffectDuration.PERMANENT,
                target=EffectTarget.SELF,
                activation=ActivationCondition.ANY,
                modifiers=[StatModifier(StatType.DAMAGE, 10, is_random=True)]
            )
            brave_effects.append(brave_effect)
            manager.add_effect(fighter_id, brave_effect)
            brave_effect.apply(current_round=1)
            
            # Log initial effect application
            value = brave_effect.modifiers[0].get_value()
            manager.log_effect(1, brave_effect, value, StatType.DAMAGE, fighter_id)
        
        # Verify all effects are active
        active_effects = manager.get_active_effects(fighter_id)
        assert len(active_effects) == 3
        
        # Verify each effect maintained its random value
        history = manager.effect_history
        assert len(history) == 3
        initial_values = [h.applied_value for h in history]
        
        # Process several rounds to ensure permanence
        for round_num in range(2, 5):
            manager.process_round_end(round_num)
            
            # Verify effects are still active
            active_effects = manager.get_active_effects(fighter_id)
            assert len(active_effects) == 3
            
            # Verify random values remained cached
            for effect, initial_value in zip(active_effects, initial_values):
                current_value = effect.modifiers[0].get_value()
                assert current_value == initial_value, "Random value changed"

    def test_halving_effects_accumulation(self, manager, fighter_id):
        """Test accumulation of effects that halve stats"""
        # Create multiple burn effects (halving resistance)
        burn_effects = []
        for i in range(2):
            burn_effect = Effect(
                name=f"Burn_{i}",
                duration=EffectDuration.PERMANENT,
                target=EffectTarget.OPPONENT,
                activation=ActivationCondition.WIN_ONLY,
                modifiers=[StatModifier(StatType.RESISTANCE, "HALF")]
            )
            burn_effects.append(burn_effect)
            manager.add_effect(fighter_id, burn_effect)
            burn_effect.apply(current_round=i+1)
            manager.log_effect(i+1, burn_effect, -1, StatType.RESISTANCE, fighter_id)
        
        # Verify all effects remain active
        active_effects = manager.get_active_effects(fighter_id)
        assert len(active_effects) == 2
        
        # Process multiple rounds
        for round_num in range(3, 6):
            manager.process_round_end(round_num)
            assert len(manager.get_active_effects(fighter_id)) == 2

    def test_mixed_permanent_effects(self, manager, fighter_id):
        """Test interaction of different types of permanent effects"""
        # Create Brave effect (random damage boost)
        brave_effect = Effect(
            name="Brave",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[StatModifier(StatType.DAMAGE, 10, is_random=True)]
        )
        
        # Create Don't Cry effect (fixed resistance boost)
        dont_cry_effect = Effect(
            name="Don't Cry",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.LOSE_ONLY,
            modifiers=[StatModifier(StatType.RESISTANCE, 10, is_random=False)]
        )
        
        # Add and apply both effects
        for effect in [brave_effect, dont_cry_effect]:
            manager.add_effect(fighter_id, effect)
            effect.apply(current_round=1)
            
            # Log effect application
            value = effect.modifiers[0].get_value()
            manager.log_effect(1, effect, value, effect.modifiers[0].stat_type, fighter_id)
        
        # Verify both effects are active
        active_effects = manager.get_active_effects(fighter_id)
        assert len(active_effects) == 2
        
        # Process multiple rounds
        history = manager.effect_history
        initial_values = {h.effect_name: h.applied_value for h in history}
        
        for round_num in range(2, 5):
            manager.process_round_end(round_num)
            
            active_effects = manager.get_active_effects(fighter_id)
            assert len(active_effects) == 2
            
            # Verify values remain consistent
            for effect in active_effects:
                current_value = effect.modifiers[0].get_value()
                assert current_value == initial_values[effect.name]