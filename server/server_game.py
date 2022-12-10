import logging
import os
from aiohttp import web

from server_base import BasicServer

log = logging.getLogger()


class GameServer(BasicServer):
    "Game server"

    def __init__(self, clientdir) -> None:
        self.clientdir = clientdir

        self.players = {}
        self.spectator_ids = []
        self.master_id = None

        self.game_state = "lobby"
        self.joining_allowed = True

        super().__init__()

    async def send_to_spectators(self, data):
        """Send data to all spectators"""

        await self.send_to_ids(data, ids=self.spectator_ids)

    async def send_to_joined(self, data):
        """Send data to all clients who joined the game as player or spectator"""

        joined_ids = self.players.keys()+self.spectator_ids
        await self.send_to_ids(data, ids=joined_ids)

    async def send_to_unjoined(self, data):
        """Send data to all clients who haven't joined the game"""

        unjoined_ids = set(self.websockets.keys()) - \
            set(self.players.keys()) - set(self.spectator_ids)
        await self.send_to_ids(data, ids=unjoined_ids)

    async def handle_action_from_player(self, action, data, ws, wsid):
        """Handle action sent from a joined player"""

        if action == 'leave_room':
            log.info('[WS] #%s left the room! ("%s")',
                     wsid, self.players[wsid]['name'])
            del self.players[wsid]
            await self.send_to_all({'action': 'player_left', 'id': wsid})
            return await ws.send_json({'action': 'room_left'})
        if action == 'select_team' and self.game_state == 'lobby':
            team = data['team']
            if team in [0, 1]:
                self.players[wsid]['team'] = team
            return await self.send_to_all({'action': 'player_updated', 'id': wsid, 'player': self.players[wsid]})
        return False

    async def handle_action_from_master(self, action, data, ws, wsid):
        """Handle action sent from master"""

        if action == 'leave_room':
            self.spectator_ids.remove(wsid)
            self.master_id = None
            log.info(
                '[WS] #%s: The game master left the room! The next spectator will become the new game master!', wsid)
            return await ws.send_json({'action': 'room_left'})
        if action == 'toggle_joining':
            self.joining_allowed = not self.joining_allowed
            return await self.send_to_all({'action': 'joining_toggled', 'allowed': self.joining_allowed})
        return False

    async def handle_action_from_spectator(self, action, data, ws, wsid):
        """Handle action sent from spectators (except master)"""

        if action == 'leave_room':
            self.spectator_ids.remove(wsid)
            log.info('[WS] #%s stopped spectating!', wsid)
            return await ws.send_json({'action': 'room_left'})
        return False

    async def handle_action_from_unjoined(self, action, data, ws, wsid):
        """Handle action sent from a player that hasn't joined"""

        if action == 'join_room':
            mode = data['mode']
            if mode == 'player':
                if self.game_state != 'lobby':
                    return await ws.send_json({'action': 'alert', 'message': '[Error] Game already started!'})
                name = data['name']
                self.players[wsid] = {'name': name, 'team': None, 'id': wsid}
                log.info('[WS] #%s joined as player "%s"', wsid, name)
                await self.send_to_all({'action': 'player_joined', 'id': wsid, 'player': self.players[wsid]})
            else:
                self.spectator_ids.append(wsid)
                log.info('[WS] #%s started spectating!', wsid)
                if self.master_id is None:
                    self.master_id = wsid
                    mode = 'master'
                    log.info('[WS] #%s is now the game master!', wsid)
            return await ws.send_json({'action': 'room_joined', 'id': wsid, 'mode': mode, 'players': self.players, 'game_state': self.game_state})
        return False

    async def handle_message_json(self, data, ws, wsid):
        """Handle incoming messages in json format."""

        await super().handle_message_json(data, ws, wsid)

        action = data.pop('action', None)

        if action == 'message':
            await self.send_to_all({'action': 'message', 'id': wsid, 'message': data['message']})
        elif wsid in self.players:
            if await self.handle_action_from_player(action, data, ws, wsid) is not False:
                return
        elif wsid == self.master_id:
            if await self.handle_action_from_master(action, data, ws, wsid) is not False:
                return
        elif wsid in self.spectator_ids:
            if await self.handle_action_from_spectator(action, data, ws, wsid) is not False:
                return
        else:
            if await self.handle_action_from_unjoined(action, data, ws, wsid) is not False:
                return

        await ws.send_json({'action': 'alert', 'message': '[Error] Invalid action!'})

    async def handle_connect(self, ws, wsid):
        """Handle client connection."""

        await super().handle_connect(ws, wsid)

        await ws.send_json({'action': 'connected', 'id': wsid, 'joining_allowed': self.joining_allowed})

    async def handle_disconnect(self, ws, wsid):
        """Handle client disconnection."""

        await super().handle_disconnect(ws, wsid)

        if wsid in self.players:
            log.info('[WS] #%s ("%s") disconnected!',
                     wsid, self.players[wsid]['name'])
            del self.players[wsid]
            await self.send_to_all({'action': 'player_left', 'id': wsid})
        elif wsid in self.spectator_ids:
            log.info('[WS] #%s (spectator) disconnected!', wsid)
            self.spectator_ids.remove(wsid)

            if wsid == self.master_id:
                log.info(
                    '[WS] Master disconnected! The next spectator will become the new game master!')
                self.master_id = None

    def get_routes(self) -> list:
        """Get the routes for the http server"""

        async def handle_index_page(request):
            return web.FileResponse(os.path.join(self.clientdir, 'index.html'))

        return [
            web.get(
                '/', handle_index_page),
            web.static(
                '/static', os.path.join(self.clientdir, 'static')),
        ]
