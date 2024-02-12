from asyncio import open_connection, StreamReader, StreamWriter
import json
from uuid import uuid4 as uuid
from ..deck import Card
class Game:

    """
    
    Has access to: 
    - own hand
    - self uuid
    - other names and card counts
    - order of play


    Accept broadcasts:
    - if uuid present, only if uuid = self.uuid
    
    
    """

    uuid: str
    name: str
    initiated: bool
    game_started: bool
    hand: list[Card]
    players: list[(str, str, int)] #(uuid, name, cards)
    top_card: Card
    current_player: str

    def __init__(self, player_name: str):
        self.name = player_name

        self.connection_manager: ConnectionManager = ConnectionManager(self)
        self.connection_manager.connect(("127.0.0.1", 60001))
        self.initiated = False
        self.game_started = False

    def on_connection(self):
        response = json.loads(self.connection_manager.sendrecv({"type": "join", "name": self.name}))
        self.uuid = response['uuid']
        self.initiated = True

    def _handle_turn_start(self):
        self._handle_hand(json.loads(self.connection_manager.sendrecv({"type":"query_hand", "uuid": self.uuid}))['cards'])
        # wait for input, either play or draw
        

    def _handle_current_player_broadcast(self, data: dict):
        self.current_player = data['current_player']['uuid']

        if self.current_player == self.uuid:
            self._handle_turn_start()

    def _handle_top_card_broadcast(self, data: dict):
        self.top_card = Card.from_data(data['top_card'])

    def _handle_hand(self, hand: list):
        self.hand = list(map(lambda x: Card.from_data(x), hand))

    def _handle_card_counts(self, data: dict):
        for i in self.players:
            i[2] = data['card_counts'][i[0]]

    def process(self, data: dict):
        if data['type'] == "game_start":
            self.players = list(map(lambda x: (x[0], x[1]['name'], len(data['hand'])), data['players'].items()))
            self._handle_hand(data['players'][self.uuid]['hand'])
            self._handle_top_card_broadcast()
            self._handle_current_player_broadcast(data)
            return
        
        if 'top_card' in data:
            self._handle_top_card_broadcast(data)

        if 'current_player' in data:
            self._handle_current_player_broadcast(data)

        if 'cards' in data:
            self._handle_hand(data['cards'])    

        if 'card_counts' in data:
            self._handle_card_counts(data)

class ConnectionManager:

    reader: StreamReader
    writer: StreamWriter
    game: Game
    def __init__(self, game: Game):
        self.game = game

    def process(self, data: bytes):
        try:
            info = json.loads(data)
        except json.decoder.JSONDecodeError:
            print("Invalid JSON")
            return
        
        if 'uuid' in info and info['uuid'] != self.game.uuid:
            return
        
        self.game.process(info)

    def send(self, data: object):
        b['message_uuid'] = uuid().hex
        b = json.dumps(data).encode()

        self.writer.write(b)

    def sendrecv(self, data: object) -> bytes:
        self.send(data)
        return self.reader.readuntil()

    async def connect(self, server: tuple[str, int]):
        connection = await open_connection(*server)
        self.reader: StreamReader = connection[0] 
        self.writer: StreamWriter = connection[1]

        while True:
            d = await self.reader.readuntil()
            try:
                self.process(d)
            except Exception as e:
                print(e)