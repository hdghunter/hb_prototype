import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum, auto

class PillzType(Enum):
    NONE = auto()
    SOUTH_PACIFIC = auto()
    NORDIC_SHIELD = auto()

@dataclass
class PillzEffect:
    """Represents the effect of a pillz on a fighter"""
    name: str
    damage_multiplier: float = 1.0
    resistance_multiplier: float = 1.0
    skip_round: bool = False
    next_round_damage_multiplier: float = 1.0
    next_round_resistance_multiplier: float = 1.0

class Pillz:
    """Defines all available pillz and their effects"""
    @staticmethod
    def get_effect(pillz_type: PillzType) -> PillzEffect:
        if pillz_type == PillzType.SOUTH_PACIFIC:
            return PillzEffect(
                name="South Pacific",
                damage_multiplier=0,  # Skip this round
                skip_round=True,
                next_round_damage_multiplier=2.0  # Double damage next round
            )
        elif pillz_type == PillzType.NORDIC_SHIELD:
            return PillzEffect(
                name="Nordic Shield",
                resistance_multiplier=2.0,  # Double resistance this round
                next_round_resistance_multiplier=0  # No resistance next round
            )
        return PillzEffect(name="None")

@dataclass
class Fighter:
    name: str
    damage: int
    resistance: int
    health: float = 100
    initial_health: float = 100
    current_effect: Optional[PillzEffect] = None
    next_round_effect: Optional[PillzEffect] = None
    
    def calculate_damage(self, opponent: 'Fighter') -> float:
        """Calculate effective damage considering opponent's resistance and pillz effects"""
        damage_multiplier = 1.0
        if self.current_effect:
            damage_multiplier *= self.current_effect.damage_multiplier
        
        base_damage = self.damage * damage_multiplier
        
        opponent_resistance = opponent.resistance
        if opponent.current_effect:
            opponent_resistance *= opponent.current_effect.resistance_multiplier
            
        return base_damage * (1 - min(opponent_resistance/100, 1))
    
    def apply_pillz(self, pillz_type: PillzType):
        """Apply a pillz effect to the fighter"""
        self.current_effect = Pillz.get_effect(pillz_type)
    
    def update_effects(self):
        """Update effects after each round"""
        if self.current_effect and self.current_effect.next_round_damage_multiplier != 1.0:
            self.next_round_effect = PillzEffect(
                name=f"{self.current_effect.name} (Next Round)",
                damage_multiplier=self.current_effect.next_round_damage_multiplier
            )
        elif self.current_effect and self.current_effect.next_round_resistance_multiplier != 1.0:
            self.next_round_effect = PillzEffect(
                name=f"{self.current_effect.name} (Next Round)",
                resistance_multiplier=self.current_effect.next_round_resistance_multiplier
            )
        
        self.current_effect = self.next_round_effect
        self.next_round_effect = None
    
    def reset(self):
        """Reset fighter's health and effects"""
        self.health = self.initial_health
        self.current_effect = None
        self.next_round_effect = None

class BattleSystem:
    def __init__(self):
        self.move_relationships = {
            'Rush': ['Strike', 'Sweep'],
            'Strike': ['Sweep', 'Grapple'],
            'Sweep': ['Guard', 'Grapple'],
            'Guard': ['Rush', 'Strike'],
            'Grapple': ['Rush', 'Guard']
        }
        self.moves = list(self.move_relationships.keys())
    
    def does_move_win(self, move1: str, move2: str) -> bool:
        return move2 in self.move_relationships[move1]
    
    def simulate_single_battle(self, fighter1: Fighter, fighter2: Fighter) -> List[Dict]:
        battle_log = []
        
        for round_num in range(1, 7):
            # Randomly decide if fighters use pillz (for simulation purposes)
            if random.random() < 0.2:  # 20% chance to use South Pacific
                fighter1.apply_pillz(PillzType.SOUTH_PACIFIC)
            if random.random() < 0.2:  # 20% chance to use Nordic Shield
                fighter2.apply_pillz(PillzType.NORDIC_SHIELD)
            
            move1 = random.choice(self.moves)
            move2 = random.choice(self.moves)
            
            # Check if either fighter is skipping due to pillz effect
            fighter1_skip = fighter1.current_effect and fighter1.current_effect.skip_round
            fighter2_skip = fighter2.current_effect and fighter2.current_effect.skip_round
            
            if fighter1_skip and fighter2_skip:
                round_result = 'Both fighters skip (Pillz effect)'
            elif fighter1_skip:
                round_result = f'{fighter2.name} wins (Opponent used {fighter1.current_effect.name})'
                damage = fighter2.calculate_damage(fighter1)
                fighter1.health -= damage
            elif fighter2_skip:
                round_result = f'{fighter1.name} wins (Opponent used {fighter2.current_effect.name})'
                damage = fighter1.calculate_damage(fighter2)
                fighter2.health -= damage
            else:
                if move1 == move2:
                    round_result = 'Draw'
                elif self.does_move_win(move1, move2):
                    damage = fighter1.calculate_damage(fighter2)
                    fighter2.health -= damage
                    round_result = f'{fighter1.name} wins'
                elif self.does_move_win(move2, move1):
                    damage = fighter2.calculate_damage(fighter1)
                    fighter1.health -= damage
                    round_result = f'{fighter2.name} wins'
                else:
                    round_result = 'No effect'
            
            # Record round results
            battle_log.append({
                'round': round_num,
                'move1': move1,
                'move2': move2,
                'fighter1_effect': fighter1.current_effect.name if fighter1.current_effect else 'None',
                'fighter2_effect': fighter2.current_effect.name if fighter2.current_effect else 'None',
                'result': round_result,
                'fighter1_health': max(0, fighter1.health),
                'fighter2_health': max(0, fighter2.health)
            })
            
            # Update effects for next round
            fighter1.update_effects()
            fighter2.update_effects()
        
        return battle_log

def run_battle_simulation(num_simulations: int = 1000) -> Tuple[int, int, int]:
    battle_system = BattleSystem()
    fighter1 = Fighter("HighDamage Fighter", damage=30, resistance=20)
    fighter2 = Fighter("HighResistance Fighter", damage=20, resistance=30)
    
    fighter1_wins = 0
    fighter2_wins = 0
    draws = 0
    
    for _ in range(num_simulations):
        fighter1.reset()
        fighter2.reset()
        
        battle_log = battle_system.simulate_single_battle(fighter1, fighter2)
        final_health1 = battle_log[-1]['fighter1_health']
        final_health2 = battle_log[-1]['fighter2_health']
        
        if final_health1 > final_health2:
            fighter1_wins += 1
        elif final_health2 > final_health1:
            fighter2_wins += 1
        else:
            draws += 1
    
    return fighter1_wins, fighter2_wins, draws

def print_example_battle():
    battle_system = BattleSystem()
    fighter1 = Fighter("HighDamage Fighter", damage=30, resistance=20)
    fighter2 = Fighter("HighResistance Fighter", damage=20, resistance=30)
    
    battle_log = battle_system.simulate_single_battle(fighter1, fighter2)
    
    print("\nExample Battle with Pillz Effects:")
    for round_data in battle_log:
        print(f"\nRound {round_data['round']}:")
        print(f"Effects - {fighter1.name}: {round_data['fighter1_effect']}, "
              f"{fighter2.name}: {round_data['fighter2_effect']}")
        print(f"{fighter1.name} uses {round_data['move1']} vs {fighter2.name} uses {round_data['move2']}")
        print(f"Result: {round_data['result']}")
        print(f"Health - {fighter1.name}: {round_data['fighter1_health']:.1f}, "
              f"{fighter2.name}: {round_data['fighter2_health']:.1f}")

if __name__ == "__main__":
    num_simulations = 1000
    fighter1_wins, fighter2_wins, draws = run_battle_simulation(num_simulations)
    
    print(f"After {num_simulations} simulations with Pillz:")
    print(f"HighDamage Fighter (30 damage, 20 resistance) wins: {fighter1_wins/num_simulations*100:.2f}%")
    print(f"HighResistance Fighter (20 damage, 30 resistance) wins: {fighter2_wins/num_simulations*100:.2f}%")
    print(f"Draws: {draws/num_simulations*100:.2f}%")
    
    print_example_battle()
