from pile import Pile
from deck import Deck, Card, Colour, ColourValue, WildValue
from hand import Hand
from typing import Optional
from uuid import uuid4 as uuid, UUID
from server.base import RequestType, BroadcastManager

class Player:
    name: str
    hand: Hand
    uuid: UUID

    uno_called: bool

    def __init__(self, name: str, deck: Deck):
        self.name = name
        self.hand = Hand.from_deck(deck)
        self.uno_called = False
        self.uuid = uuid()

    


class Game:
    pile: Pile
    deck: Deck
    players: list[Player]

    player_index: int = 0
    ongoing: bool = False
    direction: int = 1

    broadcast_manager: Optional[BroadcastManager]

    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()

        self.players = []
        self.player_index = 0
        self.ongoing = False
        self.direction = 1

        self.pile = Pile(self.deck.draw())
        self.broadcast_manager = None

    def add_player(self, player: Player):
        if self.ongoing:
            raise RuntimeError("Cannot join an ongoing game")
        
        self.players.append(player)

    def start(self):
        assert not self.ongoing

        self.ongoing = True

        self.broadcast_manager.broadcast({
            "type": "game_start",
            "players": dict(map(lambda arg: (lambda index, player: (player.uuid, {
                "hand": player.hand.as_data(),
                "index": index,
                "name": player.name
            }))(*arg), enumerate(self.players))),
            "current_player": {
                "index": self.player_index,
                "uuid": self.current_player().uuid
            },
            "top_card": self.pile.top_card(),
        })

    def increment(self):
        self.player_index += self.direction
        self.player_index %= len(self.players)

        top_card = self.pile.top_card()

        self.broadcast_manager.broadcast({
            "type": "broadcast",
            "current_player": {
                "index": self.player_index,
                "uuid": self.current_player().uuid
            }
        })

    def current_player(self) -> Player:
        return self.players[self.player_index]
    
    def broadcast_pile(self):
        self.broadcast_manager.broadcast({
            "type": "broadcast",
            "top_card": self.pile.top_card()
        })

    def broadcast_card_counts(self):
        self.broadcast_manager.broadcast({
            "type": "broadcast",
            "card_counts": dict(map(lambda player: (player.uuid, len(player.hand.cards)), self.players))
        })

    def play(self, player: Player, index: Optional[int]):
        assert self.ongoing
        assert player in self.players
        assert self.players.index(player) == self.player_index

        if index is None:
            self.give_player(player)
            self.increment()
            return

        if player.hand.cards[index].colour == Colour.WILD:
            assert player.hand.cards[index].wild_colour != None

        player.hand.play(index, self.pile)

        self.broadcast_pile()

        card: Card = self.pile.top_card()

        if card.value in (WildValue.DRAW_4, ColourValue.DRAW_TWO):
            self.increment()
            self.give_player(n = 2 if card.value == ColourValue.DRAW_TWO else 4)
            self.increment()
            return
        
        if card.value == ColourValue.REVERSE:
            self.direction *= -1

        if card.value == ColourValue.SKIP:
            self.increment()
            self.increment()
            return
        
        self.increment()

    def give_player(self, player: Optional[Player] = None, n: int = 1):
        if player is None:
            player = self.current_player()
        player.hand.cards.extend(self.deck.draw(n))
        self.broadcast_manager.broadcast({
            "type": "broadcast",
            "uuid": player.uuid,
            "cards": player.hand.as_data()
        })

    def say_uno(self, player: Player):
        assert len(self.current_player().hand.cards) == 1

        if player == self.current_player():
            player.uno_called = True
        elif not self.current_player().uno_called:
            self.give_player(n=2)
    
    def get_player_by_uuid(self, uuid: UUID) -> Optional[Player]:
        for player in self.players:
            if player.uuid.hex == uuid or player.uuid == uuid:
                return player
            
        return None
    
    def process(self, data: dict) -> dict:
        if 'type' not in data:
            return {"status": "error", "message": "type not specified."}
        
        try:
            t = RequestType(data["type"])
        except ValueError:
            return {"status": "error", "message": "invalid type."}

        match t:
            case RequestType.JOIN:
                p = Player(data["name"], self.deck)
                self.add_player(p)
                return {"status": "done", "uuid": p.uuid}
            case RequestType.LEAVE:
                if 'uuid' not in data:
                    return {"status": "error", "message": "uuid not specified."}
                player = self.get_player_by_uuid(data["uuid"])
                if player is None:
                    return {"status": "error", "message": "player does not exist."}
                self.players.remove(player)
                return {"status": "done"}
            case RequestType.START_GAME:
                try:
                    self.start()
                    return {"status": "done"}
                except AssertionError:
                    return {"status": "no action"}
            case RequestType.CALL_UNO:
                if not 'uuid' in data:
                    return {"status": "error", "message": "uuid not specified."}
                try:
                    self.say_uno(self.get_player_by_uuid(data["uuid"]))
                    return {"status": "done"}
                except AssertionError:
                    return {"status": "no action"}
            case RequestType.PLAY:
                if 'uuid' not in data:
                    return {"status": "error", "message": "uuid not specified."}
                if 'index' not in data:
                    return {"status": "error", "message": "index not specified."}
                if type(data['index']) != int:
                    return {"status": "error", "message": "index must be an integer."}

                player = self.get_player_by_uuid(data['uuid'])
                if player is None:
                    return {"status": "error", "message": "player does not exist."}

                if 0 > data['index'] or data['index'] > len(player.hand.cards):
                    return {"status": "erorr", "message": "card index out of range."}
                
                try:
                    self.play(player, data['index'])
                except AssertionError:
                    return {"status": "error", "message": "play action failed."}

                return {"status": "done"}
            case RequestType.DRAW:
                if not 'uuid' in data:
                    return {"status": "error", "message": "uuid not specified."}
                
                player = self.get_player_by_uuid(data['uuid'])

                if player is None:
                    return {"status": "error", "message": "player does not exist."}

                try:
                    self.play(player, None)
                except AssertionError:
                    return {"status": "error", "message": "draw action failed."}
                
                return {"status": "done", "card": {"value": player.hand.cards[-1].value, "colour": player.hand.cards[-1].colour}}
            case RequestType.SET_WILD_COLOUR:
                if not 'uuid' in data:
                    return {"status": "error", "message": "uuid not specified."}
                if 'index' not in data:
                    return {"status": "error", "message": "index not specified."}
                if type(data['index']) != int:
                    return {"status": "error", "message": "index must be an integer."}
                
                if 'wild_colour' not in data:
                    return {"status": "error", "message": "wild_colour not specified."}
                try:
                    wild_colour = Colour(data['wild_colour'])
                    assert wild_colour != Colour.WILD
                except AssertionError:
                    return {"status": "error", "message": "wild_colour cannot be wild."}
                except ValueError:
                    return {"status": "error", "message": "invalid wild_colour."}
                
                player = self.get_player_by_uuid(data['uuid'])

                if player is None:
                    return {"status": "error", "message": "player does not exist."}
                
                if 0 > data['index'] or data['index'] > len(player.hand.cards):
                    return {"status": "erorr", "message": "card index out of range."}

                card = player.hand.cards[data['index']]

                if card.colour != Colour.WILD:
                    return {"status": "error", "message": "specified card is not wild."}
                
                card.wild_colour = wild_colour
                return {"status": "done"}
            case RequestType.QUERY_TOP_CARD:
                if not self.ongoing:
                    return {"status": "error", "message": "game not running."}
                
                card = self.pile.top_card()

                if card is None:
                    return {"status": "done", "card": {}}

                return {"status": "done", "card": {
                    "value": card.value,
                    "colour": card.colour,
                    "wild_colour": card.wild_colour
                }}
            case RequestType.QUERY_HAND:
                if not 'uuid' in data:
                    return {"status": "error", "message": "uuid not specified."}
                
                player = self.get_player_by_uuid(data['uuid'])

                if player is None:
                    return {"status": "error", "message": "player does not exist."}
                
                return {"status": "done", "hand": player.hand.as_data()}
            case RequestType.QUERY_NAMES:
                if not 'uuid' in data:
                    return {"status": "error", "message": "uuid not specified."}
                
                player = self.get_player_by_uuid(data['uuid'])

                if player is None:
                    return {"status": "error", "message": "player does not exist."}
                
                return {"status": "done", "players": list(map(lambda p: p.name, filter(lambda p: p != player, self.players)))}
            case RequestType.QUERY_CARD_COUNTS:
                if not 'uuid' in data:
                    return {"status": "error", "message": "uuid not specified."}
                
                player = self.get_player_by_uuid(data['uuid'])

                if player is None:
                    return {"status": "error", "message": "player does not exist."}
                
                return {"status": "done", "players": list(map(lambda p: len(p.hand.cards), filter(lambda p: p != player, self.players)))}
        return {"status": "error", "message": "unknown"}

# Game loop:
# - Turn (wait for player to play)
# - Check for special functions of played card
# - Increment player index
# - If a draw card was played the previous turn, give the player the number of cards and increment player index again