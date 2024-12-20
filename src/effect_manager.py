"""
Effect management module that handles the processing, interaction,
and resolution of pillz effects during battle.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from .game_core import Fighter, PillzEffect, EffectType
from .battle_state import BattleState

@dataclass
class ProcessedEffect:
    """Represents a processed effect with final values after all modifications"""
    original_effect: PillzEffect
    final_values: Dict[str, float]
    is_countered: bool = False
    counter_source: Optional[PillzEffect] = None

class EffectManager:
    """
    Manages the processing and interaction of effects during battle.
    Handles effect countering, combining, and resolution order.
    """
    
    def __init__(self):
        """Initialize the effect manager with default parameters"""
        # Base effect parameters that can be modified
        self.effect_parameters = [
            'damage_multiplier',
            'resistance_multiplier',
            'skip_round',
            'counter_bonus'
        ]
        
        # Effect interaction rules
        self.interaction_rules = {
            (EffectType.DAMAGE, EffectType.RESISTANCE): self._resolve_damage_resistance,
            (EffectType.COUNTER, EffectType.DAMAGE): self._resolve_counter_damage,
            # Add more interaction rules as needed
        }
    
    def process_effects(self, battle_state: BattleState) -> Dict[str, Dict[str, float]]:
        """Process all active effects and return final modified stats"""
        fighter1_effects = self._get_sorted_effects(battle_state.fighter1)
        fighter2_effects = self._get_sorted_effects(battle_state.fighter2)
        
        processed_effects1 = self._process_fighter_effects(
            fighter1_effects, fighter2_effects, battle_state
        )
        processed_effects2 = self._process_fighter_effects(
            fighter2_effects, fighter1_effects, battle_state
        )
        
        return {
            'fighter1': self._calculate_final_stats(processed_effects1),
            'fighter2': self._calculate_final_stats(processed_effects2)
        }
    
    def _get_sorted_effects(self, fighter: Fighter) -> List[PillzEffect]:
        """Sort effects by priority"""
        return sorted(
            fighter.active_effects,
            key=lambda x: x.priority,
            reverse=True  # Higher priority first
        )
    
    def _process_fighter_effects(
        self,
        fighter_effects: List[PillzEffect],
        opponent_effects: List[PillzEffect],
        battle_state: BattleState
    ) -> List[ProcessedEffect]:
        """Process all effects for one fighter, considering opponent's effects"""
        processed_effects = []
        
        for effect in fighter_effects:
            # Check if effect is countered by any opponent effects
            countered_by = self._check_counters(effect, opponent_effects)
            
            if countered_by:
                # Effect is countered
                processed_effect = ProcessedEffect(
                    original_effect=effect,
                    final_values=self._get_countered_values(),
                    is_countered=True,
                    counter_source=countered_by
                )
            else:
                # Process normal effect values
                processed_effect = ProcessedEffect(
                    original_effect=effect,
                    final_values=self._calculate_effect_values(
                        effect, opponent_effects, battle_state
                    )
                )
            
            processed_effects.append(processed_effect)
        
        return processed_effects
    
    def _check_counters(
        self,
        effect: PillzEffect,
        opponent_effects: List[PillzEffect]
    ) -> Optional[PillzEffect]:
        """Check if an effect is countered by any opponent effects"""
        for opp_effect in opponent_effects:
            if effect.effect_type in opp_effect.counters:
                return opp_effect
        return None
    
    def _get_countered_values(self) -> Dict[str, float]:
        """Get default values for a countered effect"""
        return {
            'damage_multiplier': 1.0,
            'resistance_multiplier': 1.0,
            'skip_round': False,
            'counter_bonus': 1.0
        }
    
    def _calculate_effect_values(
        self,
        effect: PillzEffect,
        opponent_effects: List[PillzEffect],
        battle_state: BattleState
    ) -> Dict[str, float]:
        """Calculate final effect values considering battle state and opponent effects"""
        # Get base values for current round
        activation_round = battle_state.current_round
        rounds_active = len(battle_state.round_history)
        base_values = effect.get_effect_values(rounds_active)
        
        # Apply any effect modifiers
        modified_values = base_values.copy()
        for param, modifier in effect.effect_modifiers.items():
            if param in modified_values:
                modified_values[param] = modifier(
                    modified_values[param],
                    battle_state,
                    opponent_effects
                )
        
        return modified_values
    
    def _calculate_final_stats(
        self,
        processed_effects: List[ProcessedEffect]
    ) -> Dict[str, float]:
        """Calculate final stat modifications from processed effects"""
        final_stats = {
            'damage_multiplier': 1.0,
            'resistance_multiplier': 1.0,
            'skip_round': False,
            'counter_bonus': 1.0
        }
        
        for proc_effect in processed_effects:
            if not proc_effect.is_countered:
                for param, value in proc_effect.final_values.items():
                    if param in final_stats:
                        if isinstance(value, bool):
                            final_stats[param] = final_stats[param] or value
                        else:
                            final_stats[param] *= value
        
        return final_stats
    
    def _resolve_damage_resistance(
        self,
        damage_effect: PillzEffect,
        resistance_effect: PillzEffect
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Resolve interaction between damage and resistance effects"""
        # Example resolution logic
        damage_values = {'damage_multiplier': damage_effect.get_effect_values(0)['damage_multiplier']}
        resistance_values = {'resistance_multiplier': resistance_effect.get_effect_values(0)['resistance_multiplier']}
        
        return damage_values, resistance_values
    
    def _resolve_counter_damage(
        self,
        counter_effect: PillzEffect,
        damage_effect: PillzEffect
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Resolve interaction between counter and damage effects"""
        # Example resolution logic
        counter_values = {'counter_bonus': 2.0}  # Counter effect gets bonus
        damage_values = {'damage_multiplier': 0.5}  # Damage effect is reduced
        
        return counter_values, damage_values
    
    def cleanup_expired_effects(self, battle_state: BattleState):
        """Remove expired effects from fighters"""
        fighter1_result = battle_state.get_round_result_for_fighter(battle_state.fighter1)
        fighter2_result = battle_state.get_round_result_for_fighter(battle_state.fighter2)
        
        battle_state.fighter1.update_effects(
            battle_state.current_round,
            fighter1_result
        )
        battle_state.fighter2.update_effects(
            battle_state.current_round,
            fighter2_result
        )
    
    @staticmethod
    def create_effect_modifier(
        condition: callable,
        modification: callable
    ) -> callable:
        """
        Create a custom effect modifier function.
        
        Args:
            condition: Function that determines if modification should apply
            modification: Function that modifies the effect value
            
        Returns:
            Modifier function that can be used in effect_modifiers
        """
        def modifier(
            base_value: float,
            battle_state: BattleState,
            opponent_effects: List[PillzEffect]
        ) -> float:
            if condition(battle_state, opponent_effects):
                return modification(base_value)
            return base_value
        return modifier