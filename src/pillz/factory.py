# src/pillz/factory.py
from typing import Dict, Type
from .types import PillzType
from .pillz import Pillz
from .simple_pillz import GodzillaCakePillz
from .complex_pillz import SouthPacificPillz, AprilPillz
from .random_pillz import SailorMoonPillz, GothamPillz, AlienAttackPillz, OctoberPillz
from .defense_pillz import NordicShieldPillz

class PillzFactory:
    """Factory for creating pillz instances"""
    
    _pillz_registry: Dict[PillzType, Type[Pillz]] = {
        PillzType.GODZILLA_CAKE: GodzillaCakePillz,
        PillzType.SOUTH_PACIFIC: SouthPacificPillz,
        PillzType.APRIL: AprilPillz,
        PillzType.SAILOR_MOON: SailorMoonPillz,
        PillzType.GOTHAM: GothamPillz,
        PillzType.ALIEN_ATTACK: AlienAttackPillz,
        PillzType.OCTOBER: OctoberPillz,
        PillzType.NORDIC_SHIELD: NordicShieldPillz
    }

    @classmethod
    def register_pillz(cls, pillz_type: PillzType, pillz_class: Type[Pillz]) -> None:
        """Register a new pillz type with its implementation"""
        cls._pillz_registry[pillz_type] = pillz_class

    @classmethod
    def create_pillz(cls, pillz_type: PillzType) -> Pillz:
        """Create a new pillz instance of the specified type"""
        if pillz_type not in cls._pillz_registry:
            raise ValueError(f"Unknown pillz type: {pillz_type}")
            
        pillz_class = cls._pillz_registry[pillz_type]
        return pillz_class()

    @classmethod
    def get_available_pillz(cls) -> Dict[PillzType, str]:
        """Get a dictionary of available pillz types and their names"""
        return {
            pillz_type: cls._pillz_registry[pillz_type]().name
            for pillz_type in cls._pillz_registry
        }