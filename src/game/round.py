# src/game/round.py
from dataclasses import dataclass
from typing import Optional, Tuple
from src.effects.manager import EffectManager
from src.effects.base import Effect
from src.effects.types import StatType
from src.game_mechanics import Move, MOVE_ADVANTAGES
from src.pillz.pillz import Pillz

@dataclass
class RoundState:
    """Tracks the state of a round"""
    fighter1_move: Optional[Move] = None
    fighter2_move: Optional[Move] = None
    fighter1_pillz: Optional[Pillz] = None
    fighter2_pillz: Optional[Pillz] = None
    round_winner: Optional[str] = None
    damage_dealt: int = 0

class Round:
    def __init__(self, fighter1, fighter2, round_number: int, effect_manager: EffectManager):
        self.fighter1 = fighter1
        self.fighter2 = fighter2
        self.round_number = round_number
        self.effect_manager = effect_manager
        self.state = RoundState()

    def set_move(self, fighter_id: str, move: Move) -> None:
        """Set a fighter's move"""
        if fighter_id == self.fighter1.name:
            self.state.fighter1_move = move
        elif fighter_id == self.fighter2.name:
            self.state.fighter2_move = move
        else:
            raise ValueError(f"Unknown fighter: {fighter_id}")

    def set_pillz(self, fighter_id: str, pillz: Pillz) -> None:
        """Set a fighter's pillz for the round"""
        if fighter_id == self.fighter1.name:
            self.state.fighter1_pillz = pillz
        elif fighter_id == self.fighter2.name:
            self.state.fighter2_pillz = pillz
        else:
            raise ValueError(f"Unknown fighter: {fighter_id}")

    def _resolve_moves(self) -> Tuple[str, str]:
        """Resolve moves and return winner and loser IDs"""
        move1 = self.state.fighter1_move
        move2 = self.state.fighter2_move
        
        # Check move advantages based on predefined relationships
        if move1 == move2:
            return None, None  # Draw
            
        if move2 in MOVE_ADVANTAGES[move1]:
            return self.fighter1.name, self.fighter2.name
        elif move1 in MOVE_ADVANTAGES[move2]:
            return self.fighter2.name, self.fighter1.name
            
        return None, None  # No advantage

    def _apply_effects(self, winner_id: Optional[str]) -> None:
        """Apply pillz effects based on round outcome"""
        if self.state.fighter1_pillz:
            effect = self.state.fighter1_pillz.activate(won_round=(winner_id == self.fighter1.name))
            if effect:
                self.effect_manager.add_effect(self.fighter1.name, effect)

        if self.state.fighter2_pillz:
            effect = self.state.fighter2_pillz.activate(won_round=(winner_id == self.fighter2.name))
            if effect:
                self.effect_manager.add_effect(self.fighter2.name, effect)

    def _calculate_damage(self, attacker, defender) -> int:
        """Calculate damage with effects applied"""
        # Get active effects for both fighters
        attacker_effects = self.effect_manager.get_active_effects(attacker.name)
        defender_effects = self.effect_manager.get_active_effects(defender.name)

        # Apply damage modifiers from effects
        modified_damage = attacker.damage
        modified_resistance = defender.resistance

        for effect in attacker_effects:
            for modifier in effect.modifiers:
                if modifier.stat_type == StatType.DAMAGE:
                    if modifier.get_value() == -1:  # HALF effect
                        modified_damage //= 2
                    else:
                        modified_damage += modifier.get_value()

        for effect in defender_effects:
            for modifier in effect.modifiers:
                if modifier.stat_type == StatType.RESISTANCE:
                    if modifier.get_value() == -1:  # HALF effect
                        modified_resistance //= 2
                    else:
                        modified_resistance += modifier.get_value()

        # Calculate final damage
        return round(modified_damage * (1 - modified_resistance/100))

    def resolve(self) -> str:
        """Resolve the round including moves, pillz, and effects"""
        if not (self.state.fighter1_move and self.state.fighter2_move):
            raise ValueError("Both fighters must select moves before resolution")

        # Resolve moves
        winner_id, loser_id = self._resolve_moves()
        self.state.round_winner = winner_id

        # Apply effects
        self._apply_effects(winner_id)

        # Calculate and apply damage if there's a winner
        if winner_id:
            attacker = self.fighter1 if winner_id == self.fighter1.name else self.fighter2
            defender = self.fighter2 if winner_id == self.fighter1.name else self.fighter1
            self.state.damage_dealt = self._calculate_damage(attacker, defender)

        # Process round end in effect manager
        self.effect_manager.process_round_end(self.round_number)

        return self.get_round_summary()

    def get_round_summary(self) -> str:
        """Generate a detailed summary of the round"""
        summary = [f"\nRound {self.round_number} Summary:"]
        
        # Moves
        summary.append(f"{self.fighter1.name}: {self.state.fighter1_move.name}")
        summary.append(f"{self.fighter2.name}: {self.state.fighter2_move.name}")
        
        # Pillz
        if self.state.fighter1_pillz:
            summary.append(f"{self.fighter1.name} used {self.state.fighter1_pillz.name}")
        if self.state.fighter2_pillz:
            summary.append(f"{self.fighter2.name} used {self.state.fighter2_pillz.name}")
        
        # Outcome
        if self.state.round_winner:
            summary.append(f"\nWinner: {self.state.round_winner}")
            summary.append(f"Damage Dealt: {self.state.damage_dealt}")
        else:
            summary.append("\nRound Drawn")

        # Active Effects
        for fighter in [self.fighter1, self.fighter2]:
            active_effects = self.effect_manager.get_active_effects(fighter.name)
            if active_effects:
                summary.append(f"\n{fighter.name}'s Active Effects:")
                for effect in active_effects:
                    summary.append(f"- {effect.name}")

        return "\n".join(summary)