# tests/test_pillz/test_random_pillz.py
import pytest
from src.pillz.types import PillzType
from src.pillz.factory import PillzFactory
from src.effects.types import StatType

class TestRandomPillz:
    def test_random_value_distribution(self):
        """Test pillz that generate random values in range 1-10"""
        # Pillz with random value generation
        random_value_pillz = [
            (PillzType.GODZILLA_CAKE, StatType.DAMAGE),      # Brave
            (PillzType.SAILOR_MOON, StatType.RESISTANCE),    # Resolve
            (PillzType.GOTHAM, StatType.RESISTANCE),         # Weakness
            (PillzType.ALIEN_ATTACK, StatType.DAMAGE)        # Rust
        ]

        for pillz_type, stat_type in random_value_pillz:
            # Create pillz instance
            pillz = PillzFactory.create_pillz(pillz_type)
            
            # Collect values from multiple activations
            values = []
            for _ in range(20):
                effect = pillz.activate(won_round=True)
                values.append(effect.modifiers[0].get_value())
                
                # Verify each value is in correct range
                assert 1 <= values[-1] <= 10, f"{pillz.name} generated value outside 1-10 range"
            
            # Verify value distribution
            unique_values = len(set(values))
            assert unique_values > 1, f"{pillz.name} not generating varied values"
            
            # Verify modifier affects correct stat
            assert effect.modifiers[0].stat_type == stat_type

    def test_october_sadness_effect_selection(self):
        """Test October (Sadness) random effect selection"""
        pillz = PillzFactory.create_pillz(PillzType.OCTOBER)
        
        # Collect effects from multiple activations
        effects = set()
        attempts = 0
        max_attempts = 50

        while len(effects) < 2 and attempts < max_attempts:
            effect = pillz.activate(won_round=True)
            effects.add(effect.name)
            attempts += 1

            # Verify effect properties
            assert effect.target.name == "OPPONENT"
            assert effect.duration.name == "PERMANENT"
            assert effect.name in {"Sadness(Rust)", "Sadness(Weakness)"}
            
            # Verify random value range
            value = effect.modifiers[0].get_value()
            assert 1 <= value <= 10

        # Should see both effect types
        assert len(effects) == 2, f"Not enough variety in effects. Got: {effects}"
        print(f"Saw {len(effects)} different effects in {attempts} attempts: {effects}")

    def test_random_value_consistency(self):
        """Test that random values remain consistent after generation"""
        for pillz_type in [PillzType.GODZILLA_CAKE, PillzType.SAILOR_MOON, 
                          PillzType.GOTHAM, PillzType.ALIEN_ATTACK]:
            pillz = PillzFactory.create_pillz(pillz_type)
            effect = pillz.activate(won_round=True)
            
            # Get initial value
            initial_value = effect.modifiers[0].get_value()
            
            # Value should remain consistent in subsequent calls
            for _ in range(5):
                assert effect.modifiers[0].get_value() == initial_value, \
                    f"{pillz.name} random value changed after initial generation"