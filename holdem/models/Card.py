from dataclasses import dataclass

from ..models.Rank import Rank
from ..models.Suit import Suit
from ..models.Constants import RANK_VALUE_MAP

@dataclass(frozen=True, slots=True)
class Card:
    rank: Rank
    suit: Suit

    def __post_init__(self) -> None:
        if not isinstance(self.rank, Rank):
            raise ValueError(f'Rank should be of type Rank, got {type(self.rank)}')
        if not isinstance(self.suit, Suit):
            raise ValueError(f'Suit should be of type Suit, got {type(self.suit)}')

    def __str__(self) -> str:
        return f'{self.rank.name} OF {self.suit.name}S'

    def __repr__(self) -> str:
        return f'{self.rank.value}{self.suit.value}'
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Card):
            raise NotImplementedError(f'Card cannot be compared with {type(other)}')
        return RANK_VALUE_MAP[self.rank] < RANK_VALUE_MAP[other.rank]
    
    def __gt__(self, other) -> bool:
        if not isinstance(other, Card):
            raise NotImplementedError(f'Card cannot be compared with {type(other)}')
        return RANK_VALUE_MAP[self.rank] > RANK_VALUE_MAP[other.rank]