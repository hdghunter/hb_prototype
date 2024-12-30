# tests/test_pillz/test_factory.py
import pytest
from src.pillz.types import PillzType
from src.pillz.factory import PillzFactory
from src.pillz.simple_pillz import GodzillaCakePillz

class TestPillzFactory:
    def test_create_valid_pillz(self):
        """Test creation of valid pillz type"""
        pillz = PillzFactory.create_pillz(PillzType.GODZILLA_CAKE)
        assert isinstance(pillz, GodzillaCakePillz)
        assert pillz.type == PillzType.GODZILLA_CAKE
        
    def test_create_invalid_pillz(self):
        """Test error handling for invalid pillz type"""
        # Temporarily unregister GODZILLA_CAKE
        registry_backup = PillzFactory._pillz_registry.copy()
        PillzFactory._pillz_registry.clear()
        
        with pytest.raises(ValueError):
            PillzFactory.create_pillz(PillzType.GODZILLA_CAKE)
            
        # Restore registry
        PillzFactory._pillz_registry.update(registry_backup)
        
    def test_register_new_pillz(self):
        """Test registration of new pillz type"""
        class TestPillz(GodzillaCakePillz):
            pass
            
        # Register new pillz type
        PillzFactory.register_pillz(PillzType.BURNING_MAN, TestPillz)
        
        # Try creating the new pillz type
        pillz = PillzFactory.create_pillz(PillzType.BURNING_MAN)
        assert isinstance(pillz, TestPillz)
        
        # Clean up registration
        PillzFactory._pillz_registry.pop(PillzType.BURNING_MAN)
        
    def test_get_available_pillz(self):
        """Test getting list of available pillz"""
        available_pillz = PillzFactory.get_available_pillz()
        
        assert PillzType.GODZILLA_CAKE in available_pillz
        assert available_pillz[PillzType.GODZILLA_CAKE] == "Godzilla Cake"
        
    def test_pillz_creation_independence(self):
        """Test that each pillz creation is independent"""
        pillz1 = PillzFactory.create_pillz(PillzType.GODZILLA_CAKE)
        pillz2 = PillzFactory.create_pillz(PillzType.GODZILLA_CAKE)
        
        assert pillz1 is not pillz2  # Should be different instances
        assert pillz1.effect is None and pillz2.effect is None  # Both should start with no effect
        
        # Activating one shouldn't affect the other
        effect1 = pillz1.activate(won_round=True)
        assert pillz1.effect is effect1
        assert pillz2.effect is None