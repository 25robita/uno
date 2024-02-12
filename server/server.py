import socket
import json
from .base import BroadcastManager
from game import Game
from uuid import UUID
from functools import partial

from asyncio import start_server, StreamReader, StreamWriter


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex
        return json.JSONEncoder.default(self, obj)

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 60001  # The port used by the server


def process(data: bytes, game: Game) -> bytes:
    try:
        info = json.loads(data)
    except json.decoder.JSONDecodeError as w:
        print(w)
        return # silently fail?

    try:
        response = game.process(info)
    except Exception as f:
        print(f)


    if response is None: 
        print("response: none")
        return
    response["type"] = "response"
    if "message_uuid" in response:
        response["responding_to"] = info["message_uuid"]

    print(f"response: {response}")

    return bytes(json.dumps(response, cls=UUIDEncoder), 'utf-8') + b'\x00'

def host_game(game: Game):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                r = process(data, game)
                if r is not None:
                    conn.sendto(r, addr)

    
async def handle_connection(game: Game, reader: StreamReader, writer: StreamWriter):
    print(f"Connection on {writer.transport.get_extra_info('peername')}")
    while True:
        data = await reader.readuntil()
        print(data)
        r = process(data, game)
        if r is not None:
            writer.write(r)

async def async_host_game(game: Game):


    server = await start_server(partial(handle_connection, game), HOST, PORT)
    
    broadcast_manager = BroadcastManager(*server.sockets)
    game.broadcast_manager = broadcast_manager
    
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()