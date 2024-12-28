# tests/test_effects/test_complex_effects.py
import pytest
from src.effects.types import EffectDuration, EffectTarget, StatType, ActivationCondition
from src.effects.base import Effect, StatModifier
from src.effects.manager import EffectManager

class TestComplexEffectScenarios:
    @pytest.fixture
    def manager(self):
        return EffectManager()

    @pytest.fixture
    def fighter_id(self):
        return "fighter1"

    @pytest.fixture
    def opponent_id(self):
        return "fighter2"

    def test_effect_stacking_order(self, manager, fighter_id):
        """Test multiple effects stacking on the same stat"""
        # Create effects that modify resistance
        half_effect = Effect(
            name="Burn",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.OPPONENT,
            activation=ActivationCondition.WIN_ONLY,
            modifiers=[StatModifier(StatType.RESISTANCE, "HALF")]
        )
        
        decrease_effect = Effect(
            name="Weakness",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.OPPONENT,
            activation=ActivationCondition.ANY,
            modifiers=[StatModifier(StatType.RESISTANCE, 5, is_random=False)]
        )
        
        # Test Case 1: HALF then -5
        manager.add_effect(fighter_id, half_effect)
        manager.add_effect(fighter_id, decrease_effect)
        
        half_effect.apply(current_round=1)
        decrease_effect.apply(current_round=1)
        
        # Log the effects application
        manager.log_effect(1, half_effect, 50, StatType.RESISTANCE, fighter_id)  # 100 -> 50
        manager.log_effect(1, decrease_effect, 5, StatType.RESISTANCE, fighter_id)  # 50 -> 45
        
        # Verify effect history
        history = manager.effect_history
        assert len(history) == 2
        assert history[0].applied_value == 50  # First effect (HALF)
        assert history[1].applied_value == 5   # Second effect (-5)
        
        # Clear history for next test
        manager.effect_history.clear()
        manager.active_effects[fighter_id].clear()
        
        # Test Case 2: -5 then HALF
        manager.add_effect(fighter_id, decrease_effect)
        manager.add_effect(fighter_id, half_effect)
        
        decrease_effect.apply(current_round=2)
        half_effect.apply(current_round=2)
        
        # Log the effects application
        manager.log_effect(2, decrease_effect, 5, StatType.RESISTANCE, fighter_id)  # 100 -> 95
        manager.log_effect(2, half_effect, 47, StatType.RESISTANCE, fighter_id)     # 95 -> 47.5
        
        # Verify effect history
        history = manager.effect_history
        assert len(history) == 2
        assert history[0].applied_value == 5   # First effect (-5)
        assert history[1].applied_value == 47  # Second effect (HALF)

    def test_dexterity_conditional_timing(self, manager, fighter_id):
        """Test Dexterity effect with conditional next-win activation"""
        dexterity = Effect(
            name="Dexterity",
            duration=EffectDuration.NEXT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[
                StatModifier(StatType.DAMAGE, 2)  # Double damage
            ]
        )
        
        manager.add_effect(fighter_id, dexterity)
        
        # Should be in pending effects until win condition
        assert len(manager.get_pending_effects(fighter_id)) == 1
        assert len(manager.get_active_effects(fighter_id)) == 0
        
        # Simulate losing rounds - effect should stay pending
        for round_num in range(1, 4):
            manager.process_round_end(round_num)
            assert len(manager.get_pending_effects(fighter_id)) == 1
        
        # Simulate winning round - effect should activate
        dexterity.pending_condition = "WIN"
        dexterity.apply(current_round=4)
        manager.activate_pending_effect(fighter_id, dexterity)  # Move from pending to active
        manager.log_effect(4, dexterity, 2, StatType.DAMAGE, fighter_id)
        
        # Effect should move from pending to active
        assert len(manager.get_pending_effects(fighter_id)) == 0
        assert len(manager.get_active_effects(fighter_id)) == 1
        
        # Verify effect is properly registered in history
        history = manager.effect_history
        assert len(history) == 1
        assert history[0].round_number == 4
        assert history[0].effect_name == "Dexterity"
        assert history[0].applied_value == 2

    def test_spike_effect_copying(self, manager, fighter_id, opponent_id):
        """Test Spike effect copying opponent's effects"""
        # Set up opponent's effects
        damage_boost = Effect(
            name="Damage Boost",
            duration=EffectDuration.CURRENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[StatModifier(StatType.DAMAGE, 10)]
        )
        
        resistance_boost = Effect(
            name="Resistance Boost",
            duration=EffectDuration.CURRENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[StatModifier(StatType.RESISTANCE, 15)]
        )
        
        # Apply opponent's effects
        manager.add_effect(opponent_id, damage_boost)
        manager.add_effect(opponent_id, resistance_boost)
        damage_boost.apply(current_round=1)
        resistance_boost.apply(current_round=1)
        
        # Create Spike effect
        spike_effect = Effect(
            name="Spike",
            duration=EffectDuration.CURRENT,
            target=EffectTarget.OPPONENT,
            activation=ActivationCondition.LOSE_ONLY,
            modifiers=[]  # Will be filled with copied effects
        )
        
        # Copy opponent's active effects
        for effect in manager.get_active_effects(opponent_id):
            copied_modifier = StatModifier(
                stat_type=effect.modifiers[0].stat_type,
                value=effect.modifiers[0].get_value(),
                is_random=False  # Copied effects use the original's rolled value
            )
            spike_effect.modifiers.append(copied_modifier)
        
        manager.add_effect(fighter_id, spike_effect)
        spike_effect.apply(current_round=1)
        
        # Verify copied effects
        for i, modifier in enumerate(spike_effect.modifiers):
            manager.log_effect(
                1, 
                spike_effect,
                modifier.get_value(),
                modifier.stat_type,
                opponent_id
            )
        
        # Check history
        history = manager.effect_history
        assert len(history) == 2  # Two copied effects
        assert any(h.applied_value == 10 for h in history)  # Damage boost
        assert any(h.applied_value == 15 for h in history)  # Resistance boost