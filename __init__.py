from game import Game, Player
from server.server import async_host_game
from asyncio import run

if __name__ == "__main__":
    game = Game()

    # game.add_player(Player("Luna", game.deck))
    # game.add_player(Player("Rose", game.deck))
    # game.add_player(Player("Skye", game.deck))

    # game.start()

    run(async_host_game(game))
