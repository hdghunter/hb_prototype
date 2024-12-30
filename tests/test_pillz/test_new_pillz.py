# tests/test_pillz/test_new_pillz.py

import pytest
from src.pillz.types import PillzType, PillzActivationType
from src.pillz.factory import PillzFactory
from src.effects.types import StatType, EffectDuration, EffectTarget
from src.effects.manager import EffectManager
from src.game_mechanics import Fighter

class TestNewPillz:
    @pytest.fixture
    def manager(self):
        return EffectManager()

    @pytest.fixture
    def fighters(self):
        return (Fighter("Player", damage=30, resistance=20),
                Fighter("AI", damage=40, resistance=30))

    def test_kiss_pillz(self, manager):
        """Test Kiss pillz (Don't Cry effect)"""
        pillz = PillzFactory.create_pillz(PillzType.KISS)
        
        # Test pillz properties
        assert pillz.name == "Kiss"
        assert pillz.activation_type == PillzActivationType.LOSE_MOVE_ONLY
        
        # Test activation conditions
        assert not pillz.can_activate(won_round=True)
        assert pillz.can_activate(won_round=False)
        
        # Test effect creation
        effect = pillz.activate(won_round=False)
        assert effect is not None
        assert effect.name == "Don't Cry"
        assert effect.duration == EffectDuration.PERMANENT
        assert effect.target == EffectTarget.SELF
        
        # Test modifier values
        assert len(effect.modifiers) == 1
        modifier = effect.modifiers[0]
        assert modifier.stat_type == StatType.RESISTANCE
        assert modifier.get_value() == 10
        assert not modifier.is_random

    def test_hawaii_horror_pillz(self, manager):
        """Test Hawaii Horror pillz (Infect effect)"""
        pillz = PillzFactory.create_pillz(PillzType.HAWAII_HORROR)
        
        # Test pillz properties
        assert pillz.name == "Hawaii Horror"
        assert pillz.activation_type == PillzActivationType.WIN_MOVE_ONLY
        
        # Test activation conditions
        assert pillz.can_activate(won_round=True)
        assert not pillz.can_activate(won_round=False)
        
        # Test effect creation
        effect = pillz.activate(won_round=True)
        assert effect is not None
        assert effect.name == "Infect"
        assert effect.duration == EffectDuration.PERMANENT
        assert effect.target == EffectTarget.OPPONENT
        
        # Test modifier values
        assert len(effect.modifiers) == 1
        modifier = effect.modifiers[0]
        assert modifier.stat_type == StatType.DAMAGE
        assert modifier.get_value() == -1  # Special value for HALF
        assert not modifier.is_random

    def test_burning_man_pillz(self, manager):
        """Test Burning Man pillz (Burn effect)"""
        pillz = PillzFactory.create_pillz(PillzType.BURNING_MAN)
        
        # Test pillz properties
        assert pillz.name == "Burning Man"
        assert pillz.activation_type == PillzActivationType.WIN_MOVE_ONLY
        
        # Test effect creation
        effect = pillz.activate(won_round=True)
        assert effect is not None
        assert effect.name == "Burn"
        assert effect.duration == EffectDuration.PERMANENT
        assert effect.target == EffectTarget.OPPONENT
        
        # Test modifier values
        assert len(effect.modifiers) == 1
        modifier = effect.modifiers[0]
        assert modifier.stat_type == StatType.RESISTANCE
        assert modifier.get_value() == -1  # Special value for HALF
        assert not modifier.is_random

    def test_jurassic_pillz(self, manager, fighters):
        """Test Jurassic pillz (Spike effect)"""
        fighter1, fighter2 = fighters
        pillz = PillzFactory.create_pillz(PillzType.JURASSIC)
        
        # Test pillz properties
        assert pillz.name == "Jurassic"
        assert pillz.activation_type == PillzActivationType.LOSE_MOVE_ONLY
        
        # Test effect creation
        effect = pillz.activate(won_round=False)
        assert effect is not None
        assert effect.name == "Spike"
        assert effect.duration == EffectDuration.CURRENT
        assert effect.target == EffectTarget.OPPONENT
        
        # Add effect to manager
        manager.add_effect(fighter1.name, effect)
        effect.apply(current_round=1)
        
        # Test copying mechanics
        active_effects = manager.get_active_effects(fighter1.name)
        assert len(active_effects) == 1
        assert active_effects[0].name == "Spike"
        
        # Test effect expiration
        manager.process_round_end(1)
        assert len(manager.get_active_effects(fighter1.name)) == 0

    def test_factory_registration(self):
        """Test that all new pillz are properly registered in factory"""
        new_pillz_types = [
            PillzType.JURASSIC,
            PillzType.KISS,
            PillzType.BURNING_MAN,
            PillzType.HAWAII_HORROR
        ]
        
        for pillz_type in new_pillz_types:
            pillz = PillzFactory.create_pillz(pillz_type)
            assert pillz is not None
            assert pillz.type == pillz_type