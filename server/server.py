import aiohttp
import logging
import os.path
import asyncio
from aiohttp import web

log = logging.getLogger(__name__)

class BasicServer:
    "Basic websocket and http server"

    def __init__(self) -> None:
        self.app = self.create_app()
        self.websockets = {}

    async def index_view(self, request):
        """Index page"""

        if request.method == 'POST':
            return web.Response(text="POST")

        return web.FileResponse(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client', 'index.html'))

    async def send_all_json(self, data, exclude=None):
        """Send json data to all connected clients."""

        for ws in self.websockets.values():
            if ws != exclude:
                await ws.send_json(data)

    async def onmessage(self, ws, msg, name):
        """Handle incoming messages."""

        if msg.type == aiohttp.WSMsgType.text:
            await self.send_all_json({'action': 'sent', 'name': name, 'text': msg.data}, exclude=ws)
            # data = json.loads(msg.data)
            # if data['action'] == 'connect':
            #     await self.onconnect(ws, data)
            # elif data['action'] == 'sent':
            #     await self.onsent(ws, data)
            # elif data['action'] == 'disconnect':
            #     await self.ondisconnect(ws, data)
            # else:
            #     log.warning('Unknown action: %s', data['action'])
        elif msg.type == aiohttp.WSMsgType.error:
            log.warning('ws connection closed with exception %s', ws.exception())
        else:
            raise RuntimeError("Unsupported message type: %s" % msg.type)

    async def websocket_handler(self, request):
        """Handle incoming websocket connections."""

        ws_current = web.WebSocketResponse()
        await ws_current.prepare(request)

        # Join

        name = "anyone"
        log.info('%s joined.', name)
        await ws_current.send_json({'action': 'connect', 'name': name})

        # Inform others and add to list

        for ws in self.websockets.values():
            await ws.send_json({'action': 'join', 'name': name})
        self.websockets[name] = ws_current

        # Main loop

        try:
            while True:
                msg = await ws_current.receive()

                await self.onmessage(ws_current, msg, name)
        except RuntimeError:
            pass

        # On disconnect / error

        del self.websockets[name]
        log.info('%s disconnected.', name)
        for ws in self.websockets.values():
            await ws.send_json({'action': 'disconnect', 'name': name})

        return ws_current

    async def onshutdown(self, app):
        """Cleanup tasks tied to the application's shutdown."""

        for ws in self.websockets.values():
            await ws.close()
        self.websockets.clear()

    def get_routes(self) -> list:
        return [
            web.view('/', self.index_view),
            web.static('/static', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client', 'static')),
        ]

    def create_app(self) -> web.Application:
        """Create the aiohttp application."""

        app = web.Application()
        app.add_routes([
            web.get('/ws', self.websocket_handler),
        ] + self.get_routes())
        app.on_shutdown.append(self.onshutdown)
        return app

    def run(self, host="0.0.0.0", port=80) -> None:
        """Run the server."""

        web.run_app(self.app, host=host, port=port)

if __name__ == "__main__":
    server = BasicServer()
    server.run()
