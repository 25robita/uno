from enum import StrEnum
from socket import socket
import json


class RequestType(StrEnum):
    JOIN = "join"
    LEAVE = "leave"
    START_GAME = "start_game"
    CALL_UNO = "call_uno"
    PLAY = "play"
    DRAW = "draw"
    SET_WILD_COLOUR = "set_wild_colour"
    QUERY_TOP_CARD = "query_top_card"
    QUERY_HAND = "query_hand"
    QUERY_CARD_COUNTS = "query_card_counts"
    QUERY_NAMES = "query_names"


class BroadcastManager:
    def __init__(self, *sockets: socket):
        self.sockets = sockets
    
    def broadcast_bytes(self, data: bytes):
        for sock in self.sockets:
            sock.sendall(data)

    def broadcast(self, data: object):
        self.broadcast_bytes(bytes(json.dumps(data), 'utf-8'))