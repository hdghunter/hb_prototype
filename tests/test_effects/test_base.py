import pytest
from src.effects.types import EffectDuration, EffectTarget, StatType, ActivationCondition
from src.effects.base import Effect, StatModifier
from src.effects.manager import EffectManager

class TestStatModifier:
    def test_fixed_value_modifier(self):
        modifier = StatModifier(StatType.DAMAGE, 10)
        assert modifier.get_value() == 10
        # Should return same value on multiple calls
        assert modifier.get_value() == 10
    
    def test_random_value_modifier(self):
        modifier = StatModifier(StatType.DAMAGE, 10, is_random=True)
        value1 = modifier.get_value()
        assert 1 <= value1 <= 10
        # Should cache random value
        assert modifier.get_value() == value1
    
    def test_half_value_modifier(self):
        modifier = StatModifier(StatType.RESISTANCE, "HALF")
        assert modifier.get_value() == -1  # Special value indicating HALF
        
class TestEffect:
    @pytest.fixture
    def basic_effect(self):
        return Effect(
            name="Test Effect",
            duration=EffectDuration.CURRENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[StatModifier(StatType.DAMAGE, 10)]
        )
    
    def test_effect_activation_conditions(self, basic_effect):
        # Test ANY activation condition
        assert basic_effect.can_activate(won_round=True)
        assert basic_effect.can_activate(won_round=False)
        
        # Test WIN_ONLY activation
        win_effect = Effect(
            name="Win Effect",
            duration=EffectDuration.CURRENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.WIN_ONLY,
            modifiers=[StatModifier(StatType.DAMAGE, 10)]
        )
        assert win_effect.can_activate(won_round=True)
        assert not win_effect.can_activate(won_round=False)
        
        # Test LOSE_ONLY activation
        lose_effect = Effect(
            name="Lose Effect",
            duration=EffectDuration.CURRENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.LOSE_ONLY,
            modifiers=[StatModifier(StatType.DAMAGE, 10)]
        )
        assert lose_effect.can_activate(won_round=False)
        assert not lose_effect.can_activate(won_round=True)
    
    def test_effect_duration_handling(self, basic_effect):
        # Test CURRENT duration
        basic_effect.apply(current_round=1)
        assert basic_effect.is_active
        assert basic_effect.should_expire(current_round=1)
        assert not basic_effect.should_expire(current_round=2)
        
        # Test PERMANENT duration
        perm_effect = Effect(
            name="Permanent Effect",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[StatModifier(StatType.DAMAGE, 10)]
        )
        perm_effect.apply(current_round=1)
        assert perm_effect.is_active
        assert not perm_effect.should_expire(current_round=1)
        assert not perm_effect.should_expire(current_round=100)

class TestEffectManager:
    @pytest.fixture
    def manager(self):
        return EffectManager()
    
    @pytest.fixture
    def current_effect(self):
        return Effect(
            name="Current Effect",
            duration=EffectDuration.CURRENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[StatModifier(StatType.DAMAGE, 10)]
        )
    
    @pytest.fixture
    def permanent_effect(self):
        return Effect(
            name="Permanent Effect",
            duration=EffectDuration.PERMANENT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[StatModifier(StatType.DAMAGE, 10)]
        )
    
    def test_effect_addition(self, manager, current_effect, permanent_effect):
        fighter_id = "fighter1"
        
        # Add current effect
        manager.add_effect(fighter_id, current_effect)
        assert len(manager.get_active_effects(fighter_id)) == 1
        assert len(manager.get_pending_effects(fighter_id)) == 0
        
        # Add permanent effect
        manager.add_effect(fighter_id, permanent_effect)
        assert len(manager.get_active_effects(fighter_id)) == 2
        assert len(manager.get_pending_effects(fighter_id)) == 0
    
    def test_effect_expiration(self, manager, current_effect, permanent_effect):
        fighter_id = "fighter1"
        
        # Add both effects
        manager.add_effect(fighter_id, current_effect)
        manager.add_effect(fighter_id, permanent_effect)
        
        # Apply effects
        current_effect.apply(current_round=1)
        permanent_effect.apply(current_round=1)
        
        # Process round end
        manager.process_round_end(round_number=1)
        active_effects = manager.get_active_effects(fighter_id)
        assert len(active_effects) == 1
        assert active_effects[0].name == "Permanent Effect"
    
    def test_effect_history_logging(self, manager, current_effect):
        fighter_id = "fighter1"
        manager.add_effect(fighter_id, current_effect)
        
        # Log effect application
        manager.log_effect(
            round_number=1,
            effect=current_effect,
            applied_value=10,
            stat_modified=StatType.DAMAGE,
            target_fighter=fighter_id
        )
        
        assert len(manager.effect_history) == 1
        log_entry = manager.effect_history[0]
        assert log_entry.round_number == 1
        assert log_entry.effect_name == "Current Effect"
        assert log_entry.applied_value == 10
        assert log_entry.stat_modified == StatType.DAMAGE
        assert log_entry.target_fighter == fighter_id

    def test_next_round_effect_handling(self, manager):
        fighter_id = "fighter1"
        next_round_effect = Effect(
            name="Next Round Effect",
            duration=EffectDuration.NEXT,
            target=EffectTarget.SELF,
            activation=ActivationCondition.ANY,
            modifiers=[StatModifier(StatType.DAMAGE, 10)]
        )
        
        # Add next round effect
        manager.add_effect(fighter_id, next_round_effect)
        assert len(manager.get_pending_effects(fighter_id)) == 1
        assert len(manager.get_active_effects(fighter_id)) == 0