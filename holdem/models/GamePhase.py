from enum import Enum

class HoldemGamePhase(Enum):
    PREGAME = 'pregame'
    PREFLOP = 'preflop'
    FLOP = 'flop'
    TURN = 'turn'
    RIVER = 'river'
    SHOWDOWN = 'showdown'