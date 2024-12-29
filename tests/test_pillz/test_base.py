# tests/test_pillz/test_base.py
import pytest
from src.pillz.types import PillzType, PillzActivationType
from src.pillz.pillz import Pillz, GodzillaCakePillz
from src.effects.types import EffectDuration, EffectTarget, StatType

class TestPillzBase:
    @pytest.fixture
    def godzilla_cake(self):
        return GodzillaCakePillz()
    
    def test_pillz_initialization(self, godzilla_cake):
        """Test basic pillz properties"""
        assert godzilla_cake.type == PillzType.GODZILLA_CAKE
        assert godzilla_cake.name == "Godzilla Cake"
        assert godzilla_cake.activation_type == PillzActivationType.ANY_MOVE
        assert godzilla_cake.effect is None  # Effect should be None until activated
        
    def test_pillz_activation_conditions(self, godzilla_cake):
        """Test pillz activation under different conditions"""
        # Godzilla Cake can be activated on any move
        assert godzilla_cake.can_activate(won_round=True)
        assert godzilla_cake.can_activate(won_round=False)
        
    def test_effect_initialization(self, godzilla_cake):
        """Test effect creation when pillz is activated"""
        # Activate pillz
        effect = godzilla_cake.activate(won_round=True)
        
        # Verify effect properties
        assert effect is not None
        assert effect.name == "Brave"
        assert effect.duration == EffectDuration.PERMANENT
        assert effect.target == EffectTarget.SELF
        
        # Verify modifier
        assert len(effect.modifiers) == 1
        modifier = effect.modifiers[0]
        assert modifier.stat_type == StatType.DAMAGE
        assert modifier.is_random == True
        
        # Verify same effect is returned on subsequent activations
        same_effect = godzilla_cake.activate(won_round=True)
        assert same_effect is effect  # Should be the same instance

    def test_invalid_activation(self, godzilla_cake):
        """Test that activate() handles invalid conditions gracefully"""
        # Even though Godzilla Cake can always activate, this tests the mechanism
        godzilla_cake.activation_type = PillzActivationType.WIN_MOVE_ONLY
        
        # Attempt to activate on lose
        effect = godzilla_cake.activate(won_round=False)
        assert effect is None
        assert godzilla_cake.effect is None

    def test_effect_value_consistency(self, godzilla_cake):
        """Test that random effect values remain consistent"""
        effect = godzilla_cake.activate(won_round=True)
        first_value = effect.modifiers[0].get_value()
        
        # Value should be in range 1-10
        assert 1 <= first_value <= 10
        
        # Value should remain consistent
        assert effect.modifiers[0].get_value() == first_value