import logging
import sys
import os.path
import asyncio
from aiohttp import web

from server import BasicServer
from ngrok_helpers import NgrokTunnel

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
        self.spectator_ids = []
        self.master_id = None

        self.game_state = "lobby"

    async def send_to_spectators(self, data):
        """Send data to all spectators."""

        await self.send_to_ids(data, ids=self.spectator_ids)

    async def send_to_joined(self, data):
        """Send data to all clients who joined the game as player or spectator."""

        await self.send_to_ids(data, ids=self.players.keys()+self.spectator_ids)

    async def handle_action_by_player(self, action, data, ws, wsid):
        """Handle player action."""

        if action == 'select_team' and self.game_state == 'lobby':
            team = data['team']
            if team in [0, 1]:
                self.players[wsid]['team'] = team
                await self.send_to_all({'action': 'player_updated', 'id': wsid, 'player': self.players[wsid]})
        else:
            await ws.send_json({'action': 'alert', 'message': '[Error] Invalid action!'})

    async def handle_action_by_master(self, action, data, ws, wsid):
        """Handle master action."""

    async def handle_message_json(self, data, ws, wsid):
        """Handle incoming messages in json format."""

        await super().handle_message_json(data, ws, wsid)

        action = data.pop('action', None)

        if action == 'setup':
            mode = data['mode']
            if mode == 'player':
                if self.game_state != 'lobby':
                    await ws.send_json({'action': 'alert', 'message': '[Error] Game already started!'})
                    return
                name = data['name']
                log.info('[WS] #%s joined as player "%s"', wsid, name)
                self.players[wsid] = {'name': name, 'team': None, 'id': wsid}
                await self.send_to_all({'action': 'player_connected', 'id': wsid, 'player': self.players[wsid]})
            else:
                log.info('[WS] #%s joined as spectator!', wsid)
                self.spectator_ids.append(wsid)
                if self.master_id is None:
                    self.master_id = wsid
                    log.info('[WS] #%s is now the game master!', wsid)
                    mode = 'master'
            await ws.send_json({'action': 'connection_established', 'id': wsid, 'mode': mode, 'players': self.players, 'game_state': self.game_state})
        elif action == 'message':
            await self.send_to_all({'action': 'message', 'id': wsid, 'message': data['message']})
        elif wsid in self.players:
            await self.handle_action_by_player(action, data, ws, wsid)
        elif wsid == self.master_id:
            await self.handle_action_by_master(action, data, ws, wsid)
        else:
            await ws.send_json({'action': 'alert', 'message': '[Error] Invalid action!'})

    async def handle_connect(self, ws, wsid):
        """Handle client connection."""

        await super().handle_connect(ws, wsid)

    async def handle_disconnect(self, ws, wsid):
        """Handle client disconnection."""

        await super().handle_disconnect(ws, wsid)

        if wsid in self.players:
            log.info('[WS] #%s ("%s") disconnected!', wsid, self.players[wsid]['name'])
            del self.players[wsid]
            await self.send_to_all({'action': 'player_disconnected', 'id': wsid})
        elif wsid in self.spectator_ids:
            log.info('[WS] #%s (spectator) disconnected!', wsid)
            self.spectator_ids.remove(wsid)

            if wsid == self.master_id:
                log.info('[WS] Master disconnected! The next spectator will become the new game master!')
                self.master_id = None


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
    with NgrokTunnel() as url:
        log.info("Tunnel URL: %s", url)

        server = GameServer()

        loop = asyncio.new_event_loop()
        loop.run_until_complete(server.start())

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(server.stop())
            loop.close()
