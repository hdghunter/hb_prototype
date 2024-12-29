# src/effects/types.py
from enum import Enum, auto
from typing import Literal, Union

class EffectDuration(Enum):
    CURRENT = auto()    # Only current round
    NEXT = auto()       # Next round meeting condition
    PERMANENT = auto()  # Until end of match

class EffectTarget(Enum):
    SELF = auto()      # Effect applies to the user
    OPPONENT = auto()  # Effect applies to the opponent

class StatType(Enum):
    DAMAGE = auto()
    RESISTANCE = auto()

class ActivationCondition(Enum):
    ANY = auto()        # Can be used with any move
    WIN_ONLY = auto()   # Can only be used on winning moves
    LOSE_ONLY = auto()  # Can only be used on losing moves

EffectValue = Union[Literal["HALF"], int]  # For effects that either halve or modify by a fixed/random amount