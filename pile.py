from deck import Card, Colour
from typing import Iterable

class Pile:
    cards: list[Card] = []
    def __init__(self, cards: Iterable[Card] = None):
        self.cards = []
        if cards is not None:
            self.cards.extend(cards)
    
    def top_card(self) -> Card | None:
        """Returns the top card on the deck. If the deck is empty, None is returned."""
        try:
            return self.cards[-1]
        except IndexError:
            return None
    
    def is_valid(self, card: Card) -> bool:
        "Checks if it is valid to play a specified card on the deck."
        top_card = self.top_card()
        
        if top_card is None:
            return True
        
        if card.colour == Colour.WILD:
            return True
        
        colour = top_card.wild_colour if top_card.colour == Colour.WILD else top_card.colour
        if colour == card.colour:
            return True
        if top_card.colour == Colour.WILD:
            return False
        return card.value == top_card.value
    
    def play(self, card: Card) -> None:
        """Attempts to play a card on the pile. If the card cannot be played, an error is raised."""
        if not self.is_valid(card):
            raise ValueError("Card cannot be played")
        
        self.cards.append(card)