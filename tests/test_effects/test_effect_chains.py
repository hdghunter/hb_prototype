import pytest
from src.effects.types import EffectDuration, EffectTarget, StatType, ActivationCondition
from src.effects.base import Effect, StatModifier
from src.effects.manager import EffectManager

class TestEffectChains:
    @pytest.fixture
    def manager(self):
        return EffectManager()

    @pytest.fixture
    def fighter_id(self):
        return "fighter1"

    def test_shield_effect_chain(self, manager, fighter_id):
        """Test Shield effect chain across multiple rounds"""
        shield_effect = Effect(
            name="Shield",
            duration=EffectDuration.NEXT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.LOSE_ONLY,
            modifiers=[StatModifier(StatType.RESISTANCE, 2)]  # Double resistance
        )
        
        manager.add_effect(fighter_id, shield_effect)
        
        # Round 1: Lose and activate shield
        shield_effect.pending_condition = "LOSE"
        shield_effect.apply(current_round=1)
        manager.activate_pending_effect(fighter_id, shield_effect)
        manager.log_effect(1, shield_effect, 2, StatType.RESISTANCE, fighter_id)
        
        # Verify shield is active
        assert len(manager.get_active_effects(fighter_id)) == 1
        assert len(manager.get_pending_effects(fighter_id)) == 0
        
        # Round 2: Shield is active
        manager.process_round_end(2)
        history = manager.effect_history
        assert len(history) == 1
        assert history[0].round_number == 1
        assert history[0].effect_name == "Shield"

    def test_multiple_effect_chain(self, manager, fighter_id):
        """Test multiple effects chaining together"""
        # Create Shield effect
        shield_effect = Effect(
            name="Shield",
            duration=EffectDuration.NEXT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.LOSE_ONLY,
            modifiers=[StatModifier(StatType.RESISTANCE, 2)]
        )
        
        # Create Dexterity effect
        dexterity = Effect(
            name="Dexterity",
            duration=EffectDuration.NEXT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[StatModifier(StatType.DAMAGE, 2)]
        )
        
        # Round 1: Add and activate Shield
        manager.add_effect(fighter_id, shield_effect)
        shield_effect.pending_condition = "LOSE"
        shield_effect.apply(current_round=1)
        manager.activate_pending_effect(fighter_id, shield_effect)
        manager.log_effect(1, shield_effect, 2, StatType.RESISTANCE, fighter_id)
        
        # Round 2: Add Dexterity while Shield is active
        manager.add_effect(fighter_id, dexterity)
        
        # Round 3: Activate Dexterity on win
        dexterity.pending_condition = "WIN"
        dexterity.apply(current_round=3)
        manager.activate_pending_effect(fighter_id, dexterity)
        manager.log_effect(3, dexterity, 2, StatType.DAMAGE, fighter_id)
        
        # Verify effect history
        history = manager.effect_history
        assert len(history) == 2
        assert history[0].effect_name == "Shield"
        assert history[1].effect_name == "Dexterity"
        
        # Verify timing of effects
        assert history[0].round_number == 1
        assert history[1].round_number == 3

    def test_effect_expiration_chain(self, manager, fighter_id):
        """Test effect chain with expiration"""
        # Create a chain of effects with different durations
        current_effect = Effect(
            name="Current",
            duration=EffectDuration.CURRENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[StatModifier(StatType.DAMAGE, 5)]
        )
        
        next_effect = Effect(
            name="Next",
            duration=EffectDuration.NEXT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[StatModifier(StatType.RESISTANCE, 3)]
        )
        
        # Add and apply both effects
        manager.add_effect(fighter_id, current_effect)
        manager.add_effect(fighter_id, next_effect)
        
        current_effect.apply(current_round=1)
        next_effect.apply(current_round=1)
        manager.activate_pending_effect(fighter_id, next_effect)
        
        manager.log_effect(1, current_effect, 5, StatType.DAMAGE, fighter_id)
        manager.log_effect(1, next_effect, 3, StatType.RESISTANCE, fighter_id)
        
        # Verify both effects are active
        assert len(manager.get_active_effects(fighter_id)) == 2
        
        # Process round end
        manager.process_round_end(1)
        
        # Verify current effect expired but next effect remains
        active_effects = manager.get_active_effects(fighter_id)
        assert len(active_effects) == 1
        assert active_effects[0].name == "Next"