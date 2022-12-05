import logging
import sys
import os.path
import asyncio
from aiohttp import web
from server import BasicServer

log = logging.getLogger()
log.setLevel(logging.DEBUG)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
log.addHandler(stream)

clientdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client')

class GameServer(BasicServer):
    "Game server"

    def __init__(self) -> None:
        super().__init__()

        self.players = {}
        self.spectatorIds = []
        self.masterId = None

    async def handle_message_json(self, data, ws, wsid):
        """Handle incoming messages in json format."""

        await super().handle_message_json(data, ws, wsid)

        action = data['action']
        if action == 'setup':
            mode = data['mode']
            if mode == 'player':
                name = data['name']
                log.info('[WS] Websocket %s connected as player with name %s', wsid, name)
                self.players[wsid] = {'name': name}
                await self.send_all_json({'action': 'player_connected', 'id': wsid, 'name': name}, exclude=ws)
            elif mode == 'spectator':
                log.info('[WS] Websocket %s connected as spectator!', wsid)
                self.spectatorIds.append(wsid)
                if self.masterId is None:
                    self.masterId = wsid
                    log.info('[WS] Websocket %s is now the game master!', wsid)
            await ws.send_json({'action': 'connection_established', 'id': wsid, 'players': self.players})
        elif action == 'message':
            await self.send_all_json({'action': 'message', 'wsid': wsid, 'data': data}, exclude=ws)

    async def handle_connect(self, ws, wsid):
        """Handle client connection."""

        await super().handle_connect(ws, wsid)

    async def handle_disconnect(self, ws, wsid):
        """Handle client disconnection."""

        await super().handle_disconnect(ws, wsid)

        if wsid in self.players:
            log.info('[WS] Player %s using websocket %s disconnected', self.players[wsid]['name'], wsid)
            del self.players[wsid]
            await self.send_all_json({'action': 'player_disconnected', 'id': wsid})
        elif wsid in self.spectatorIds:
            log.info('[WS] Spectator using websocket %s disconnected', wsid)
            self.spectatorIds.remove(wsid)
        if wsid == self.masterId:
            log.info('[WS] Master using websocket %s disconnected!', wsid)
            self.masterId = None

    def get_routes(self) -> list:
        """Get the routes for the http server"""

        async def handle_index_page(request):
            return web.FileResponse(os.path.join(clientdir, 'index.html'))

        return [
            web.get(
                '/', handle_index_page),
            web.static(
                '/static', os.path.join(clientdir, 'static')),
        ]

if __name__ == "__main__":
    server = GameServer()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.start())

    loop.run_forever()
