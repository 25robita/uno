from enum import StrEnum
import re
from typing import Callable, Optional
import random


class Colour(StrEnum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    WILD = "wild"

class ColourValue(StrEnum):
    ZERO = "0"
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    DRAW_TWO = "Draw 2"
    SKIP = "Skip"
    REVERSE = "Reverse"

class WildValue(StrEnum):
    WILD = "Wild"
    DRAW_4 = "Draw 4"

def prettify(string: str) -> str:
    return re.sub('\\b\\w', lambda x: x.group().upper(), string)

def pretty(inner: Callable[..., str]) -> Callable[..., str]:
    def wrapper(*args, **kwargs):
        return prettify(inner(*args, **kwargs))
    return wrapper


class Card:
    colour: Colour
    value: ColourValue | WildValue
    wild_colour: Optional[Colour]

    def __init__(self, colour: Colour, value: WildValue | ColourValue):
        if colour == Colour.WILD:
            assert type(value) == WildValue
        else:
            assert type(value) == ColourValue

        self.value = value
        self.colour = colour
        self.wild_colour = None

    def __repr__(self):
        return f"Card<{self.colour.name}, {self.value.name}>"

    @pretty
    def __str__(self):
        if self.colour == Colour.WILD:
            return self.value
        return f"{self.colour} {self.value}"
    
    def terminal_str(self):
        if self.colour == Colour.WILD:
            return self.value
        colour = {
            Colour.RED: '\033[31m', 
            Colour.GREEN: '\033[32m',
            Colour.YELLOW: '\033[33m',
            Colour.BLUE: '\033[34m',
        }

        return f"{colour[self.colour]}{self.value}\033[00m"
    
    def __eq__(self, __value: object):
        if not isinstance(object, Card):
            return False
        
        return self.value == self.value and self.colour == self.colour

    def from_data(data):
        card = Card(Colour(data['colour']), (WildValue if data['colour'] == Colour.WILD else ColourValue)(data['value']))
        if 'wild_colour' in data:
            card.wild_colour = data['wild_colour']
        return card

class Deck:
    cards: list[Card] = []

    def __init__(self):
        self.cards = []
        for colour in Colour:
            if colour == Colour.WILD:
                for value in WildValue:
                    for i in range (4):
                        self.cards.append(Card(colour, value))
                continue

            for value in ColourValue:
                self.cards.append(Card(colour, value))
                if value != ColourValue.ZERO:
                    self.cards.append(Card(colour, value))

    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw(self, n: int = 1) -> list[Card]:
        return [self.cards.pop() for i in range(n)]