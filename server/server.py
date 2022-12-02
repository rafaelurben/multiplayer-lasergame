import aiohttp
import logging
import os.path
import json
from aiohttp import web

log = logging.getLogger()

class BasicServer:
    "Basic websocket and http server"

    def __init__(self) -> None:
        self.app = self.create_app()
        self.websockets = {}
        self._last_id = 0

    async def index_view(self, request):
        """Index page"""

        return web.FileResponse(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client', 'index.html'))

    async def send_all_json(self, data, exclude=None):
        """Send json data to all connected clients."""

        for ws in self.websockets.values():
            if ws != exclude:
                await ws.send_json(data)

    async def handle_message(self, data, ws, wsid):
        """Handle incoming messages"""

    async def handle_message_json(self, data, ws, wsid):
        """Handle incoming messages in json format."""

    async def _handle_message(self, msg, ws, wsid):
        """Handle incoming messages."""

        if msg.type == aiohttp.WSMsgType.text:
            try:
                data = json.loads(msg.data)
                await self.handle_message_json(data, ws, wsid)
            except json.JSONDecodeError:
                await self.handle_message(msg.data, ws, wsid)
        elif msg.type == aiohttp.WSMsgType.error:
            log.warning('ws connection closed with exception %s',
                        ws.exception())
        else:
            raise RuntimeError("Unsupported message type: %s" % msg.type)

    async def websocket_handler(self, request):
        """Handle incoming websocket connections."""

        ws_current = web.WebSocketResponse()
        await ws_current.prepare(request)

        # Join

        self._last_id += 1
        wsid = self._last_id
        log.info('%s joined.', wsid)
        await ws_current.send_json({'action': 'connect', 'id': wsid})

        # Inform others and add to list

        for ws in self.websockets.values():
            await ws.send_json({'action': 'join', 'id': wsid})
        self.websockets[wsid] = ws_current

        # Main loop

        try:
            while True:
                msg = await ws_current.receive()

                await self._handle_message(msg=msg, ws=ws_current, wsid=wsid)
        except RuntimeError:
            pass

        # On disconnect / error

        del self.websockets[wsid]
        log.info('%s disconnected.', wsid)
        for ws in self.websockets.values():
            await ws.send_json({'action': 'disconnect', 'id': wsid})

        return ws_current

    async def onshutdown(self, app):
        """Cleanup tasks tied to the application's shutdown."""

        for ws in list(self.websockets.values()):
            await ws.close()
        self.websockets.clear()

    def get_routes(self) -> list:
        return [
            web.view(
                '/', self.index_view),
            web.static(
                '/static', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client', 'static')),
        ]

    def create_app(self) -> web.Application:
        """Create the aiohttp application."""

        app = web.Application()
        app.add_routes([
            web.get('/ws', self.websocket_handler),
        ] + self.get_routes())
        app.on_shutdown.append(self.onshutdown)
        return app

    def run(self, host="0.0.0.0", port=80):
        """Run the server."""

        return web.run_app(self.app, host=host, port=port)

    async def start(self, host="0.0.0.0", port=80):
        """Start the server."""

        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host=host, port=port)
        return await site.start()
