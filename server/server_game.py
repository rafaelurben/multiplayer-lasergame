import logging
import os
import re
import random
import asyncio
from aiohttp import web

from server_base import BasicServer
from engine import Map

log = logging.getLogger()


class GameServer(BasicServer):
    "Game server"

    def __init__(self, clientdir, public_url = None, allow_reconnect = False) -> None:
        self.clientdir = clientdir
        self.public_url = public_url

        self.players = {}
        self.spectator_ids = []
        self.master_id = None

        self.game_state = "lobby"
        self.joining_allowed = True

        self.engine: Map = None

        self.game_params = {
            'mapWidth': 30,
            'mapHeight': 15,
        }

        super().__init__(allow_reconnect=allow_reconnect)

    async def shuffle_teams(self, only_unassigned = False):
        """Randomly assign teams to all players"""

        teamsizes = [0, 0]
        pids = list(self.players.keys())

        if only_unassigned:
            for pid, player in self.players.items():
                if player['team'] is not None:
                    teamsizes[player['team']] += 1
                    pids.remove(pid)

        random.shuffle(pids)

        for pid in pids:
            team = teamsizes.index(min(teamsizes)) # select team with least players

            self.players[pid]['team'] = team
            await self.send_to_joined({'action': 'player_updated', 'id': pid, 'player': self.players[pid]})
            teamsizes[team] += 1

    @property
    def in_lobby(self):
        "Returns True if the game is in a lobby state"
        return self.game_state.startswith('lobby')

    @property
    def in_game(self):
        "Returns True if the game is in a game state"
        return self.game_state == 'ingame'

    def name_check(self, name: str) -> bool:
        "Check if a name is valid"

        # Check for duplicate names
        for player in self.players.values():
            if player['name'] == name:
                return False

        # Validate name
        if not re.match(r'^[a-zA-Z0-9_\- ]{3,20}$', name):
            return False

        return True

    # Websocket actions

    async def send_to_spectators(self, data):
        """Send data to all spectators"""

        await self.send_to_ids(data, ids=self.spectator_ids)

    async def send_to_joined(self, data):
        """Send data to all clients who joined the game as player or spectator"""

        joined_ids = set(self.players) | set(self.spectator_ids)
        await self.send_to_ids(data, ids=joined_ids)

    async def send_to_unjoined(self, data):
        """Send data to all clients who haven't joined the game"""

        unjoined_ids = set(self.websockets.keys()) - \
            set(self.players.keys()) - set(self.spectator_ids)
        await self.send_to_ids(data, ids=unjoined_ids)

    # Websocket handlers

    async def handle_action_from_player(self, action, data, ws, wsid):
        """Handle action sent from a joined player"""

        if action == 'leave_room':
            log.info('[WS] #%s left the room! ("%s")',
                     wsid, self.players[wsid]['name'])
            del self.players[wsid]
            await self.send_to_joined({'action': 'player_left', 'id': wsid})
            return await ws.send_json({'action': 'room_left'})
        if action == 'select_team' and self.game_state == 'lobby':
            team = data['team']
            if team in [0, 1]:
                self.players[wsid]['team'] = team
            return await self.send_to_joined({'action': 'player_updated', 'id': wsid, 'player': self.players[wsid]})
        if action == 'player_controls' and self.game_state == 'ingame':
            button = data.get('button', None)
            if button is None or button not in ['move_up', 'move_down', 'move_left', 'move_right', 'rotate_left', 'rotate_right']:
                return await ws.send_json({'action': 'alert', 'message': '[Error] Something went wrong! (invalid control button)'})
            blockid = data.get('blockid', None)
            if blockid is None:
                return await ws.send_json({'action': 'alert', 'message': "[Error] Something went wrong! (no block id)"})

            if self.engine is None:
                return log.warning('Engine is not initialized!')

            self.engine.handle_controls(player_id=wsid, block_id=blockid, button=button)
            return True
        return False

    async def handle_action_from_master(self, action, data, ws, wsid):
        """Handle action sent from master"""

        if action == 'leave_room':
            self.spectator_ids.remove(wsid)
            self.master_id = None
            log.info('[WS] #%s: The game master left the room!', wsid)
            return await ws.send_json({'action': 'room_left'})
        if self.in_lobby:
            if action == 'toggle_joining':
                self.joining_allowed = not self.joining_allowed
                return await self.send_to_all({'action': 'joining_toggled', 'allowed': self.joining_allowed, 'reason': 'master'})
            if action == 'toggle_teamlock':
                self.game_state = 'lobby_teamlock' if self.game_state == 'lobby' else 'lobby'
                return await self.send_to_joined({'action': 'state_changed', 'state': self.game_state})
            if action == 'kick_player':
                player_id = str(data.get('id', None))
                if not player_id.isdigit():
                    return await ws.send_json({'action': 'alert', 'message': '[Error] Invalid player id format!'})
                player_id = int(player_id)
                if player_id not in self.players:
                    return await ws.send_json({'action': 'alert', 'message': '[Error] Invalid player id!'})
                log.info('[WS] #%s was kicked from the room! ("%s")',
                         player_id, self.players[player_id]['name'])
                del self.players[player_id]
                await self.send_to_joined({'action': 'player_left', 'id': player_id})
                await self.send_to_one({'action': 'room_left'}, player_id)
                return await self.send_to_one({'action': 'alert', 'message': '[Info] You have been kicked from the room!'}, player_id)
            if action == 'start_game':
                return await self.start_game(**data)
            if action == 'change_player_team':
                player_id = str(data.get('id', None))
                if not player_id.isdigit():
                    return await ws.send_json({'action': 'alert', 'message': '[Error] Invalid player id format!'})
                player_id = int(player_id)
                if player_id not in self.players:
                    return await ws.send_json({'action': 'alert', 'message': '[Error] Invalid player id!'})
                team = str(data.get('team', None))
                team = int(team) if team.isdigit() else None
                if team not in [None, 0, 1]:
                    return await ws.send_json({'action': 'alert', 'message': '[Error] Invalid team!'})
                
                self.players[player_id]['team'] = team
                return await self.send_to_joined({'action': 'player_updated', 'id': player_id, 'player': self.players[player_id]})
            if action == 'shuffle_teams':
                return await self.shuffle_teams()
        if self.in_game or self.game_state == 'leaderboard':
            if action == 'end_game':
                return await self.end_game()
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
                if not self.in_lobby:
                    return await ws.send_json({'action': 'alert', 'message': '[Error] Game already started!'})
                if not self.name_check(data['name']):
                    return await ws.send_json({'action': 'alert', 'message': 'Invalid name! Only alphanumeric characters, spaces, underscores and dashes are allowed. (min 3, max 20 characters)'})
                
                name = data['name']
                self.players[wsid] = {'name': name, 'team': None, 'id': wsid}
                log.info('[WS] #%s joined as player "%s"', wsid, name)
                await self.send_to_joined({'action': 'player_joined', 'id': wsid, 'player': self.players[wsid]})
            else:
                self.spectator_ids.append(wsid)
                log.info('[WS] #%s started spectating!', wsid)
                if self.master_id is None and mode == 'master':
                    self.master_id = wsid
                    log.info('[WS] #%s is now the game master!', wsid)
                else:
                    mode = "spectator"

            await self.on_join(ws, wsid, mode)
            return True
        return False

    async def handle_message_json(self, data, ws, wsid):
        """Handle incoming messages in json format."""

        await super().handle_message_json(data, ws, wsid)

        action = data.pop('action', None)

        if action == 'message':
            return await self.send_to_all({'action': 'message', 'id': wsid, 'message': data['message']})

        if wsid in self.players:
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

        await ws.send_json({
            'action': 'connected',
            'id': wsid,
            'joining_allowed': self.joining_allowed and self.in_lobby,
            'joining_allowed_reason': 'ingame' if not self.in_lobby else 'master',
            'public_url': self.public_url,
            'game_params': self.game_params,
        })

    async def handle_reconnect(self, ws, wsid):
        """Handle client reconnection."""

        await self.handle_connect(ws, wsid)
        await super().handle_reconnect(ws, wsid)

        if wsid in self.players or wsid in self.spectator_ids:
            mode = 'master' if wsid == self.master_id else 'spectator' if wsid in self.spectator_ids else 'player'
            await self.on_join(ws, wsid, mode)

    async def handle_disconnect(self, ws, wsid):
        """Handle client disconnection."""

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

    # Config

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

    # Game logic

    async def on_join(self, ws, wsid, mode):
        await ws.send_json({'action': 'room_joined', 'id': wsid, 'mode': mode, 'players': self.players, 'game_state': self.game_state})

        if self.in_game:
            await ws.send_json({
                'action': 'game_render_map',
                'blocks': self.engine.get_map(no_changes=True)[0]
            })
            await ws.send_json({
                'action': 'game_render_lasers',
                'lasers': self.engine.get_lasers(no_changes=True)[0]
            })
            await ws.send_json({
                'action': 'game_render_score',
                'score': self.engine.get_score(no_changes=True)[0]
            })
        if self.game_state == 'leaderboard':
            teamid = 0 if self.engine.score == 1 else 1
            await ws.send_json({
                'action': 'game_render_leaderboard',
                'winning_team_id': teamid,
                'winning_team_players': [p for p in self.players.values() if p['team'] == teamid],
            })

    async def start_game(self, **params):
        """Start the game"""

        self.game_params = {**self.game_params, **params}

        await self.send_to_all({'action': 'joining_toggled', 'allowed': False, 'reason': 'ingame'})
        await self.send_to_all({'action': 'game_params_set', 'params': self.game_params})
        await self.shuffle_teams(only_unassigned=True)
        await self.send_to_joined({'action': 'state_changed', 'state': 'ingame'})

        self.engine = Map(
            mapwidth=self.game_params['mapWidth'],
            mapheight=self.game_params['mapHeight'],
            players=self.players.values()
        )
        self.game_state = 'ingame'

    async def end_game(self):
        """End the game"""

        self.engine = None
        self.game_state = 'lobby'

        await self.send_to_all({'action': 'joining_toggled', 'allowed': self.joining_allowed, 'reason': 'master'})
        return await self.send_to_joined({'action': 'state_changed', 'state': 'lobby'})

    async def tick(self, ticknum):
        """Called every tick"""

        # Don't do anything if the game isn't running
        if not self.in_game:
            return

        # Log a warning if the game engine isn't initialized
        if self.engine is None:
            return log.warning("Game engine is not initialized!")

        # Main actions
        self.engine.tick()

        # Send updates
        game_map, has_changed = self.engine.get_map()
        if has_changed:
            await self.send_to_joined({
                'action': 'game_render_map',
                'blocks': game_map
            })

        lasers, has_changed = self.engine.get_lasers()
        if has_changed:
            await self.send_to_joined({
                'action': 'game_render_lasers',
                'lasers': lasers
            })

        score, has_changed = self.engine.get_score()
        if has_changed:
            await self.send_to_joined({
                'action': 'game_render_score',
                'score': score
            })

            if score in [0, 1]:
                self.game_state = 'leaderboard'
                await self.send_to_joined({'action': 'state_changed', 'state': 'leaderboard'})
                teamid = 0 if self.engine.score == 1 else 1
                await self.send_to_spectators({
                    'action': 'game_render_leaderboard',
                    'winning_team_id': teamid,
                    'winning_team_players': [p for p in self.players.values() if p['team'] == teamid],
                })

    async def gameloop(self):
        """The main game loop"""

        ticknum = 0

        while True:
            await asyncio.gather(
                asyncio.sleep(1/10),
                self.tick(ticknum=ticknum),
            )
            ticknum += 1
