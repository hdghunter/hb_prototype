# src/effects/manager.py
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from .base import Effect
from .types import StatType, EffectDuration 

@dataclass
class EffectHistoryEntry:
    round_number: int
    effect_name: str
    applied_value: int
    stat_modified: StatType
    target_fighter: str

@dataclass
class EffectManager:
    active_effects: Dict[str, List[Effect]] = field(default_factory=dict)
    pending_effects: Dict[str, List[Effect]] = field(default_factory=dict)
    effect_history: List[EffectHistoryEntry] = field(default_factory=list)

    def add_effect(self, fighter_id: str, effect: Effect) -> None:
        if fighter_id not in self.active_effects:
            self.active_effects[fighter_id] = []
        if fighter_id not in self.pending_effects:
            self.pending_effects[fighter_id] = []

        if effect.duration == EffectDuration.CURRENT or effect.duration == EffectDuration.PERMANENT:
            self.active_effects[fighter_id].append(effect)
        else:
            self.pending_effects[fighter_id].append(effect)

    def log_effect(self, round_number: int, effect: Effect, applied_value: int, 
                  stat_modified: StatType, target_fighter: str) -> None:
        entry = EffectHistoryEntry(
            round_number=round_number,
            effect_name=effect.name,
            applied_value=applied_value,
            stat_modified=stat_modified,
            target_fighter=target_fighter
        )
        self.effect_history.append(entry)

    def process_round_end(self, round_number: int) -> None:
        # Remove expired effects
        for fighter_id in self.active_effects:
            self.active_effects[fighter_id] = [
                effect for effect in self.active_effects[fighter_id]
                if not effect.should_expire(round_number)
            ]

    def get_active_effects(self, fighter_id: str) -> List[Effect]:
        return self.active_effects.get(fighter_id, [])

    def get_pending_effects(self, fighter_id: str) -> List[Effect]:
        return self.pending_effects.get(fighter_id, [])
    
    def activate_pending_effect(self, fighter_id: str, effect: Effect) -> None:
        """Move an effect from pending to active when its condition is met"""
        if fighter_id in self.pending_effects:
            if effect in self.pending_effects[fighter_id]:
                self.pending_effects[fighter_id].remove(effect)
                self.active_effects[fighter_id].append(effect)