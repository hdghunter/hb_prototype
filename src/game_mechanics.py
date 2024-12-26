from enum import Enum
from typing import Set, Dict, Optional
import random

class Move(Enum):
    RUSH = 1
    STRIKE = 2
    SWEEP = 3
    GUARD = 4
    GRAPPLE = 5

    def get_winning_moves(self) -> Set['Move']:
        return MOVE_ADVANTAGES[self]

    def get_move_description(self) -> str:
        winning_moves = ', '.join([move.name for move in self.get_winning_moves()])
        return f"{self.value}:{self.name} (beats {winning_moves})"

# Define move advantages
MOVE_ADVANTAGES: Dict[Move, Set[Move]] = {
    Move.RUSH: {Move.STRIKE, Move.SWEEP},
    Move.STRIKE: {Move.SWEEP, Move.GRAPPLE},
    Move.SWEEP: {Move.GUARD, Move.GRAPPLE},
    Move.GUARD: {Move.RUSH, Move.STRIKE},
    Move.GRAPPLE: {Move.RUSH, Move.GUARD}
}

class Fighter:
    def __init__(self, name: str, damage: int, resistance: int):
        self.validate_stats(damage, resistance)
        self.name = name
        self.damage = damage
        self.resistance = resistance
        self.points = 0
        
    @staticmethod
    def validate_stats(damage: int, resistance: int):
        if not (0 <= damage <= 100 and 0 <= resistance <= 100):
            raise ValueError("Damage and Resistance must be between 0 and 100")
    
    def calculate_effective_damage(self, defender: 'Fighter') -> int:
        return round(self.damage * (1 - defender.resistance/100))

class GameRound:
    def __init__(self, fighter1: Fighter, fighter2: Fighter):
        self.fighter1 = fighter1
        self.fighter2 = fighter2
        self.move1: Optional[Move] = None
        self.move2: Optional[Move] = None
        
    def resolve_round(self) -> str:
        if not (self.move1 and self.move2):
            raise ValueError("Moves must be set before resolving round")
            
        if self.move1 == self.move2:
            return f"Draw! Both fighters chose {self.move1.name}"
            
        if self.move2 in self.move1.get_winning_moves():
            damage = self.fighter1.calculate_effective_damage(self.fighter2)
            self.fighter1.points += damage
            return f"{self.fighter1.name} wins with {self.move1.name} against {self.move2.name}, dealing {damage} points!"
        elif self.move1 in self.move2.get_winning_moves():
            damage = self.fighter2.calculate_effective_damage(self.fighter1)
            self.fighter2.points += damage
            return f"{self.fighter2.name} wins with {self.move2.name} against {self.move1.name}, dealing {damage} points!"
        else:
            return "No advantage - Round drawn!"

def display_move_guide():
    print("\nAvailable moves:")
    for move in Move:
        print(move.get_move_description())

def get_player_move() -> Move:
    while True:
        try:
            display_move_guide()
            choice = int(input("\nSelect your move (1-5): "))
            return Move(choice)
        except (ValueError, KeyError):
            print("Invalid input! Please enter a number between 1 and 5.")

def get_ai_move() -> Move:
    return random.choice(list(Move))

def display_score(fighter1: Fighter, fighter2: Fighter):
    print(f"\nCurrent score:")
    print(f"{fighter1.name}: {fighter1.points}")
    print(f"{fighter2.name}: {fighter2.points}")