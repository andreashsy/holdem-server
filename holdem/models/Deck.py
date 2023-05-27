import random
from ..models.Card import Card
from ..models.Rank import Rank
from ..models.Suit import Suit

class Deck:
    def __init__(self) -> None:
        self.cards = [Card(r, s) for r in Rank for s in Suit]

    def get_cards(self) -> list[Card]:
        return self.cards.copy()

    def size(self) -> int:
        return len(self.cards)

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw_card(self) -> Card:
        if not self.cards:
            raise AttributeError('No more cards in deck')
        return self.cards.pop()