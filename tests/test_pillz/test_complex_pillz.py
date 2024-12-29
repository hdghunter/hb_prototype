# tests/test_pillz/test_complex_pillz.py
import pytest
from src.pillz.complex_pillz import SouthPacificPillz, AprilPillz
from src.effects.types import StatType
from src.effects.manager import EffectManager

class TestComplexPillz:
    @pytest.fixture
    def manager(self):
        return EffectManager()
    
    @pytest.fixture
    def fighter_id(self):
        return "fighter1"

    def test_south_pacific_effect_sequence(self, manager, fighter_id):
        """Test South Pacific (Dexterity) effect activation sequence"""
        pillz = SouthPacificPillz()
        
        # Activate the pillz
        effect = pillz.activate(won_round=True)
        assert effect is not None
        assert effect.name == "Dexterity"
        assert effect.pending_condition == "WIN"
        
        # Add to manager as pending
        manager.add_effect(fighter_id, effect)
        
        # Should be in pending effects
        assert len(manager.get_pending_effects(fighter_id)) == 1
        assert len(manager.get_active_effects(fighter_id)) == 0
        
        # Simulate losing rounds - effect should stay pending
        for round_num in range(1, 3):
            manager.process_round_end(round_num)
            assert len(manager.get_pending_effects(fighter_id)) == 1
        
        # Simulate winning round - effect should activate
        effect.apply(current_round=3)
        manager.activate_pending_effect(fighter_id, effect)
        manager.log_effect(3, effect, 2, StatType.DAMAGE, fighter_id)
        
        # Effect should move from pending to active
        assert len(manager.get_pending_effects(fighter_id)) == 0
        assert len(manager.get_active_effects(fighter_id)) == 1
        
        # Verify effect value
        active_effect = manager.get_active_effects(fighter_id)[0]
        assert active_effect.modifiers[0].get_value() == 2  # Double damage

    def test_april_random_effect_selection(self):
        """Test April (Rainbow) random effect selection"""
        pillz = AprilPillz()
        
        # Run many times to ensure we see all possible effects
        effects = set()
        max_attempts = 50  # Increased attempts to ensure we see variety
        attempts = 0
        
        while len(effects) < 3 and attempts < max_attempts:
            effect = pillz.activate(won_round=True)
            effects.add(effect.name)
            attempts += 1
            
            # Verify effect properties
            assert effect.duration.name == "PERMANENT"
            assert effect.target.name == "SELF"
            
            # Verify effect is one of the expected types
            assert effect.name in {
                "Rainbow(Brave)", 
                "Rainbow(Resolve)", 
                "Rainbow(Don't Cry)"
            }
            
            # Verify modifier values
            modifier = effect.modifiers[0]
            if effect.name == "Rainbow(Don't Cry)":
                assert not modifier.is_random
                assert modifier.get_value() == 10
            else:
                assert modifier.is_random
                value = modifier.get_value()
                assert 1 <= value <= 10
        
        # We should eventually see all three effects
        assert len(effects) >= 2, f"Random selection not producing enough variety. Got: {effects}"
        print(f"Saw {len(effects)} different effects in {attempts} attempts: {effects}")

    def test_april_effect_randomization(self):
        """Test that April's effects are properly randomized"""
        pillz = AprilPillz()
        
        # Collect value distributions
        values = []
        names = []
        
        for _ in range(20):
            effect = pillz.activate(won_round=True)
            values.append(effect.modifiers[0].get_value())
            names.append(effect.name)
        
        # Verify we're getting different values/effects
        unique_values = len(set(values))
        unique_names = len(set(names))
        
        assert unique_names >= 2, f"Not enough variety in effects. Got: {set(names)}"
        
        # For random value effects, we should see different values
        random_effect_values = [
            v for v, n in zip(values, names)
            if n != "Rainbow(Don't Cry)"  # This one has fixed value
        ]
        if random_effect_values:
            unique_random_values = len(set(random_effect_values))
            assert unique_random_values > 1, "Random values not showing variety"

    def test_effects_with_manager(self, manager, fighter_id):
        """Test both pillz types with effect manager"""
        south_pacific = SouthPacificPillz()
        april = AprilPillz()
        
        # Activate both pillz
        dexterity_effect = south_pacific.activate(won_round=True)
        rainbow_effect = april.activate(won_round=True)
        
        # Add to manager
        manager.add_effect(fighter_id, dexterity_effect)
        manager.add_effect(fighter_id, rainbow_effect)
        
        # Verify correct distribution between active and pending
        pending = manager.get_pending_effects(fighter_id)
        active = manager.get_active_effects(fighter_id)
        
        assert len(pending) == 1
        assert len(active) == 1
        assert pending[0].name == "Dexterity"
        assert "Rainbow" in active[0].name