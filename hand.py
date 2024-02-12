from deck import Card, Deck
from typing import Iterable, Optional, Self
from pile import Pile
from pick import pick

class Hand:
    cards: list[Card] = []

    def __init__(self, cards: Optional[Iterable[Card]]):
        self.cards = []
        if cards is not None:
            self.cards.extend(cards)
    
    def from_deck(deck: Deck, n: int = 7) -> Self:
        return Hand(deck.draw(n))
    
    def play(self, index: int, pile: Pile) -> None:
        """Plays a card at an index from the hand. """
        if not 0 <= index < len(self.cards):
            raise IndexError(f"Card does not exist at index {index}")
        
        pile.play(self.cards[index]) # such that if pile.play errors, the card does not leave the hand
        self.cards.pop(index)

    def terminal_print(self):
        print(*map(lambda x:x.terminal_str(), self.cards), sep="\t")
    
    def terminal_pick(self, title: str) -> tuple[Card, int]:
        
        index = pick([*map(lambda x:x.terminal_str(), self.cards)], title)[1]

        return (self.cards[index], index)
    
    def __contains__(self, a: Card) -> bool:
        return a in self.cards
    
    def as_data(self) -> list[dict]:
        return list(map(lambda card: {"value":card.value, "colour": card.colour}, self.cards))