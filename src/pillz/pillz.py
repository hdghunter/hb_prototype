# src/pillz/pillz.py
from dataclasses import dataclass
from typing import Optional
from .types import PillzType, PillzActivationType
from src.effects.base import Effect

@dataclass
class Pillz:
    """Base class for all pillz"""
    type: PillzType
    name: str
    activation_type: PillzActivationType
    description: str
    _effect: Optional[Effect] = None

    @property
    def effect(self) -> Optional[Effect]:
        """Get the effect associated with this pillz"""
        return self._effect

    def can_activate(self, won_round: bool) -> bool:
        """Check if pillz can be activated based on round outcome"""
        if self.activation_type == PillzActivationType.ANY_MOVE:
            return True
        elif self.activation_type == PillzActivationType.WIN_MOVE_ONLY:
            return won_round
        elif self.activation_type == PillzActivationType.LOSE_MOVE_ONLY:
            return not won_round
        return False

    def initialize_effect(self) -> Effect:
        """Initialize and return the effect for this pillz.
        Must be implemented by concrete pillz classes."""
        raise NotImplementedError("Concrete pillz classes must implement initialize_effect")

    def activate(self, won_round: bool) -> Optional[Effect]:
        """Attempt to activate the pillz and get its effect"""
        if not self.can_activate(won_round):
            return None
            
        if self._effect is None:
            self._effect = self.initialize_effect()
            
        return self._effect

    def __str__(self) -> str:
        return f"{self.name} ({self.description})"