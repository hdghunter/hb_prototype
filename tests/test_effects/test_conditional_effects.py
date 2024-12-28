import pytest
from src.effects.types import EffectDuration, EffectTarget, StatType, ActivationCondition
from src.effects.base import Effect, StatModifier
from src.effects.manager import EffectManager

class TestConditionalEffects:
    @pytest.fixture
    def manager(self):
        return EffectManager()

    @pytest.fixture
    def fighter_id(self):
        return "fighter1"

    def test_win_condition_effects(self, manager, fighter_id):
        """Test effects that require win condition"""
        # Create effects that only activate on win
        burn_effect = Effect(
            name="Burn",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.OPPONENT,
            activation=ActivationCondition.WIN_ONLY,
            modifiers=[StatModifier(StatType.RESISTANCE, "HALF")]
        )
        
        infect_effect = Effect(
            name="Infect",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.OPPONENT,
            activation=ActivationCondition.WIN_ONLY,
            modifiers=[StatModifier(StatType.DAMAGE, "HALF")]
        )
        
        manager.add_effect(fighter_id, burn_effect)
        manager.add_effect(fighter_id, infect_effect)
        
        # Test activation on lose (should fail)
        assert not burn_effect.can_activate(won_round=False)
        assert not infect_effect.can_activate(won_round=False)
        
        # Test activation on win
        assert burn_effect.can_activate(won_round=True)
        assert infect_effect.can_activate(won_round=True)
        
        # Apply effects on win
        burn_effect.apply(current_round=1)
        infect_effect.apply(current_round=1)
        
        # Log effects
        manager.log_effect(1, burn_effect, -1, StatType.RESISTANCE, fighter_id)
        manager.log_effect(1, infect_effect, -1, StatType.DAMAGE, fighter_id)
        
        assert len(manager.get_active_effects(fighter_id)) == 2

    def test_lose_condition_effects(self, manager, fighter_id):
        """Test effects that require lose condition"""
        # Create effects that only activate on lose
        shield_effect = Effect(
            name="Shield",
            duration=EffectDuration.NEXT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.LOSE_ONLY,
            modifiers=[StatModifier(StatType.RESISTANCE, 2)]
        )
        
        dont_cry_effect = Effect(
            name="Don't Cry",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.LOSE_ONLY,
            modifiers=[StatModifier(StatType.RESISTANCE, 10)]
        )
        
        manager.add_effect(fighter_id, shield_effect)
        manager.add_effect(fighter_id, dont_cry_effect)
        
        # Test activation on win (should fail)
        assert not shield_effect.can_activate(won_round=True)
        assert not dont_cry_effect.can_activate(won_round=True)
        
        # Test activation on lose
        assert shield_effect.can_activate(won_round=False)
        assert dont_cry_effect.can_activate(won_round=False)
        
        # Apply effects on lose
        shield_effect.apply(current_round=1)
        dont_cry_effect.apply(current_round=1)
        manager.activate_pending_effect(fighter_id, shield_effect)
        
        # Log effects
        manager.log_effect(1, shield_effect, 2, StatType.RESISTANCE, fighter_id)
        manager.log_effect(1, dont_cry_effect, 10, StatType.RESISTANCE, fighter_id)
        
        assert len(manager.get_active_effects(fighter_id)) == 2

    def test_mixed_condition_interactions(self, manager, fighter_id):
        """Test interaction between effects with different conditions"""
        # Create mixed condition effects
        win_effect = Effect(
            name="Burn",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.OPPONENT,
            activation=ActivationCondition.WIN_ONLY,
            modifiers=[StatModifier(StatType.RESISTANCE, "HALF")]
        )
        
        lose_effect = Effect(
            name="Shield",
            duration=EffectDuration.NEXT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.LOSE_ONLY,
            modifiers=[StatModifier(StatType.RESISTANCE, 2)]
        )
        
        any_effect = Effect(
            name="Brave",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[StatModifier(StatType.DAMAGE, 10, is_random=True)]
        )
        
        # Add all effects to manager
        manager.add_effect(fighter_id, win_effect)
        manager.add_effect(fighter_id, lose_effect)
        manager.add_effect(fighter_id, any_effect)
        
        # Verify ANY condition effect can always activate
        assert any_effect.can_activate(won_round=True)
        assert any_effect.can_activate(won_round=False)
        
        # Round 1: Win - apply win_effect and any_effect
        assert win_effect.can_activate(won_round=True)
        
        # Apply and log Round 1 effects
        win_effect.apply(current_round=1)
        any_effect.apply(current_round=1)
        
        manager.log_effect(1, win_effect, -1, StatType.RESISTANCE, fighter_id)  # -1 represents HALF
        
        # Get and log the random value from any_effect
        brave_value = any_effect.modifiers[0].get_value()
        manager.log_effect(1, any_effect, brave_value, StatType.DAMAGE, fighter_id)
        
        # Round 2: Lose - apply lose_effect
        assert lose_effect.can_activate(won_round=False)
        lose_effect.apply(current_round=2)
        manager.activate_pending_effect(fighter_id, lose_effect)
        manager.log_effect(2, lose_effect, 2, StatType.RESISTANCE, fighter_id)
        
        # Verify effect history
        history = manager.effect_history
        win_effects = [h for h in history if h.round_number == 1]
        lose_effects = [h for h in history if h.round_number == 2]
        
        # Should have two effects from Round 1 (win_effect and any_effect)
        assert len(win_effects) == 2
        assert any(h.effect_name == "Burn" for h in win_effects)
        assert any(h.effect_name == "Brave" for h in win_effects)
        
        # Should have one effect from Round 2 (lose_effect)
        assert len(lose_effects) == 1
        assert lose_effects[0].effect_name == "Shield"