# src/pillz/types.py
from enum import Enum, auto

class PillzType(Enum):
    """Defines all available pillz types"""
    SOUTH_PACIFIC = auto()    # Dexterity effect
    JURASSIC = auto()         # Spike effect
    GODZILLA_CAKE = auto()    # Brave effect
    NORDIC_SHIELD = auto()    # Shield effect
    KISS = auto()             # Don't cry effect
    SAILOR_MOON = auto()      # Resolve effect
    APRIL = auto()            # Rainbow effect
    OCTOBER = auto()          # Sadness effect
    GOTHAM = auto()           # Weakness effect
    ALIEN_ATTACK = auto()     # Rust effect
    BURNING_MAN = auto()      # Burn effect
    HAWAII_HORROR = auto()    # Infect effect

class PillzActivationType(Enum):
    """Defines when a pillz can be activated"""
    ANY_MOVE = auto()         # Can be used with any move
    WIN_MOVE_ONLY = auto()    # Can only be used with winning moves
    LOSE_MOVE_ONLY = auto()   # Can only be used with losing moves