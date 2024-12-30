# src/game/round.py
from dataclasses import dataclass
from typing import Optional, Tuple
from src.effects.manager import EffectManager
from src.effects.base import Effect
from src.effects.types import StatType
from src.game_mechanics import Move, MOVE_ADVANTAGES
from src.pillz.pillz import Pillz

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'

def color_move(move_name: str, is_winner: bool) -> str:
    """Color the move name based on whether it is a winning move"""
    if is_winner:
        return f"{Colors.GREEN}{move_name}{Colors.RESET}"
    return f"{Colors.RED}{move_name}{Colors.RESET}"
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
            # Update points
            attacker.points += self.state.damage_dealt

        # Process round end in effect manager
        self.effect_manager.process_round_end(self.round_number)

        return self.get_round_summary()

    def get_round_summary(self) -> str:
        """Generate a detailed formatted summary of the round"""
        # Constants for box formatting
        BOX_WIDTH = 36  # Standard width for all boxes
        INNER_WIDTH = BOX_WIDTH - 2  # Width excluding borders
        
        def center_text(text: str, width: int) -> str:
            return text.center(width)

        def pad_line(text: str) -> str:
            return f"║ {text:<{INNER_WIDTH-2}} ║"

        lines = []
        # Top border
        lines.append("╔" + "═" * INNER_WIDTH + "╗")
        # Round number centered
        lines.append(pad_line(center_text(f"Round {self.round_number} Summary", INNER_WIDTH-2)))
        lines.append("╠" + "═" * INNER_WIDTH + "╣")
        
        # Score section
        lines.append(pad_line("Current Score:"))
        lines.append(pad_line(f"{self.fighter1.name}: {self.fighter1.points}"))
        lines.append(pad_line(f"{self.fighter2.name}: {self.fighter2.points}"))
        lines.append("╠" + "═" * INNER_WIDTH + "╣")
        
        # Moves section
        lines.append(pad_line("Moves:"))
        f1_move = color_move(self.state.fighter1_move.name, self.state.round_winner == self.fighter1.name)
        f2_move = color_move(self.state.fighter2_move.name, self.state.round_winner == self.fighter2.name)
        lines.append(pad_line(f"{self.fighter1.name}: {f1_move}"))
        lines.append(pad_line(f"{self.fighter2.name}: {f2_move}"))
        
        # Pillz section
        if self.state.fighter1_pillz or self.state.fighter2_pillz:
            lines.append("╠" + "═" * INNER_WIDTH + "╣")
            lines.append(pad_line("Pillz Used:"))
            if self.state.fighter1_pillz:
                lines.append(pad_line(f"{self.fighter1.name}: {self.state.fighter1_pillz.name}"))
            if self.state.fighter2_pillz:
                lines.append(pad_line(f"{self.fighter2.name}: {self.state.fighter2_pillz.name}"))
        
        # Outcome section
        lines.append("╠" + "═" * INNER_WIDTH + "╣")
        if self.state.round_winner:
            winner_text = f"{Colors.GREEN}{self.state.round_winner}{Colors.RESET}"
            lines.append(pad_line(f"Winner: {winner_text}"))
            lines.append(pad_line(f"Damage: {self.state.damage_dealt}"))
        else:
            lines.append(pad_line(center_text("Round Drawn", INNER_WIDTH-2)))
        
        # Effects section
        f1_effects = self.effect_manager.get_active_effects(self.fighter1.name)
        f2_effects = self.effect_manager.get_active_effects(self.fighter2.name)
        if f1_effects or f2_effects:
            lines.append("╠" + "═" * INNER_WIDTH + "╣")
            lines.append(pad_line("Active Effects:"))
            if f1_effects:
                lines.append(pad_line(f"{self.fighter1.name}'s effects:"))
                for effect in f1_effects:
                    lines.append(pad_line(f"  - {effect.name}"))
            if f2_effects:
                lines.append(pad_line(f"{self.fighter2.name}'s effects:"))
                for effect in f2_effects:
                    lines.append(pad_line(f"  - {effect.name}"))

        # Bottom border
        lines.append("╚" + "═" * INNER_WIDTH + "╝")
        
        return "\n".join(lines)