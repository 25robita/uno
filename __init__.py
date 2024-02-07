from deck import Deck
from hand import Hand
from pile import Pile
from pick import pick
from game import Game, Player


if __name__ == "__main__":
    game = Game()

    game.add_player(Player("Luna", game.deck))
    game.add_player(Player("Rose", game.deck))
    game.add_player(Player("Skye", game.deck))

    game.start()

