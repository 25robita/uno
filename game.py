from pile import Pile
from deck import Deck, Card, Colour, ColourValue, WildValue
from hand import Hand
from typing import Optional

class Player:
    name: str
    hand: Hand

    uno_called: bool

    def __init__(self, name: str, deck: Deck):
        self.name = name
        self.hand = Hand.from_deck(deck)
        self.uno_called = False

class Game:
    pile: Pile
    deck: Deck
    players: list[Player]

    player_index: int = 0
    ongoing: bool = False
    direction: int = 1

    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()

        self.players = []
        self.player_index = 0
        self.ongoing = False
        self.direction = 1

        self.pile = Pile(self.deck.draw())

    def add_player(self, player: Player):
        if self.ongoing:
            raise RuntimeError("Cannot join an ongoing game")
        
        self.players.append(player)

    def start(self):
        if self.ongoing:
            raise RuntimeError("Game already running")
        
        self.ongoing = True

    def increment(self):
        self.player_index += self.direction
        self.player_index %= len(self.players)

    def current_player(self) -> Player:
        return self.players[self.player_index]

    def play(self, player: Player, index: Optional[int]):
        assert self.ongoing
        assert player in self.players
        assert self.players.index(player) == self.player_index

        if index is None:
            player.hand.cards.extend(self.deck.draw())

        if player.hand.cards[index].colour == Colour.WILD:
            assert player.hand.cards[index].wild_colour != None

        player.hand.play(index, self.pile)

        card: Card = self.pile.top_card()

        if card.value in (WildValue.DRAW_4, ColourValue.DRAW_TWO):
            self.increment()
            self.current_player() \
                .hand \
                .cards \
                .extend(
                    self.deck.draw(2 if card.value == ColourValue.DRAW_TWO else 4)
                )
            self.increment()
            return
        
        if card.value == ColourValue.REVERSE:
            self.direction *= -1

        if card.value == ColourValue.SKIP:
            self.increment()
            self.increment()
            return
        
        self.increment()

    def say_uno(self, player: Player):
        assert len(self.current_player().hand.cards) == 1

        if player == self.current_player():
            player.uno_called = True
        elif not self.current_player().uno_called:
            self.current_player().hand.cards.extend(self.deck.draw(2))
        

# Game loop:
# - Turn (wait for player to play)
# - Check for special functions of played card
# - Increment player index
# - If a draw card was played the previous turn, give the player the number of cards and increment player index again