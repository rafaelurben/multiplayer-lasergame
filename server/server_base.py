import aiohttp
import logging
import json
import sys
from aiohttp import web

log = logging.getLogger()

class BasicServer:
    "Basic websocket and http server"

    def __init__(self) -> None:
        self.app = self.create_app()
        self.websockets = {}
        self._last_id = 0

        self.allow_reconnect = "--allow-reconnect" in sys.argv
        self._reconnectable_ids = []

    def get_next_id(self) -> int:
        """Get the next available id for a websocket."""

        self._last_id += 1
        return self._last_id

    async def send_to_one(self, data, wsid):
        """Send json data to a specific client."""

        if wsid not in self.websockets:
            log.warning('[WS] #%s: Client websocket not found!', wsid)
            return

        ws = self.websockets[wsid]
        try:
            await ws.send_json(data)
        except ConnectionResetError:
            log.warning('[WS] #%s: Connection reset by peer', wsid)
            await self.handle_disconnect(ws, wsid)

    async def send_to_ids(self, data, ids):
        """Send json data to a list of websocket ids."""

        for wsid in ids:
            await self.send_to_one(data, wsid)

    async def send_to_all(self, data):
        """Send json data to all connected clients."""

        for wsid in list(self.websockets.keys()):
            await self.send_to_one(data, wsid)

    async def handle_message(self, data, ws, wsid):
        """Handle incoming messages"""

        log.info('[WS] #%s sent a message: %s', wsid, data)

    async def handle_message_json(self, data, ws, wsid):
        """Handle incoming messages in json format."""

        log.info('[WS] #%s sent a JSON message: %s', wsid, str(data))

    async def handle_connect(self, ws, wsid):
        """Handle client connection."""

        self.websockets[wsid] = ws
        log.info('[WS] #%s connected!', wsid)

    async def handle_reconnect(self, ws, wsid):
        """Handle client reconnection."""

        self.websockets[wsid] = ws
        log.info('[WS] #%s reconnected!', wsid)

    async def handle_disconnect(self, ws, wsid):
        """Handle client disconnection."""

        del self.websockets[wsid]
        log.info('[WS] #%s disconnected!', wsid)

    async def _handle_message(self, msg, ws, wsid):
        """Handle incoming messages."""

        if msg.type == aiohttp.WSMsgType.text:
            try:
                data = json.loads(msg.data)
                await self.handle_message_json(data, ws, wsid)
            except json.JSONDecodeError:
                await self.handle_message(msg.data, ws, wsid)
        else:
            raise RuntimeError("[WS] #%s Unsupported message type: %s" % (wsid, msg.type))

    async def websocket_handler(self, request):
        """Handle incoming websocket connections."""

        # Setup the websocket connection

        ws_current = web.WebSocketResponse()

        wsid = None
        is_reconnected = False

        if self.allow_reconnect:
            old_wsid = request.cookies.get("multiplayergame_wsid", "")
            if old_wsid.isdigit() and int(old_wsid) in self._reconnectable_ids:
                wsid = int(old_wsid)
                self._reconnectable_ids.remove(wsid)
                is_reconnected = True

        if not is_reconnected:
            wsid = self.get_next_id()

        ws_current.set_cookie("multiplayergame_wsid", str(wsid), samesite="Strict")
        await ws_current.prepare(request)

        # Reconnect or connect

        if is_reconnected:
            await self.handle_reconnect(ws_current, wsid)
        else:
            await self.handle_connect(ws_current, wsid)

        # Main loop

        try:
            while True:
                msg = await ws_current.receive()

                if msg.type == aiohttp.WSMsgType.ERROR:
                    log.warning('[WS] #%s: Connection closed with exception %s', wsid, ws_current.exception())
                    break
                if msg.type == aiohttp.WSMsgType.CLOSE:
                    log.warning('[WS] #%s: Connection closed!', wsid)
                    break
                await self._handle_message(msg=msg, ws=ws_current, wsid=wsid)
        except (ConnectionResetError, ConnectionAbortedError, RuntimeError):
            log.warning('[WS] #%s: Connection failed:', wsid)

        # On disconnect / error

        if self.allow_reconnect:
            del self.websockets[wsid]
            self._reconnectable_ids.append(wsid)

            # Note: If reconnecting is enabled, handle_disconnect() won't be called.
            #       This is because otherwise the client data would be deleted.
        else:
            await self.handle_disconnect(ws_current, wsid)

    async def handle_cleanup(self, app):
        """Cleanup tasks tied to the application's cleanup."""

        log.info("[Server] Cleanup...")
        for ws in list(self.websockets.values()):
            await ws.close()
        self.websockets.clear()

    async def handle_shutdown(self, app):
        """Shutdown tasks tied to the application's shutdown."""

        log.info("[Server] Stopped!")

    async def handle_startup(self, app):
        """Startup tasks tied to the application's startup."""

        log.info("[Server] Started!")

    def get_routes(self) -> list:
        return []

    def create_app(self) -> web.Application:
        """Create the aiohttp application."""

        app = web.Application()
        app.add_routes([
            web.get('/ws', self.websocket_handler),
        ] + self.get_routes())
        app.on_cleanup.append(self.handle_cleanup)
        app.on_shutdown.append(self.handle_shutdown)
        app.on_startup.append(self.handle_startup)
        return app

    def run(self, host="0.0.0.0", port=80):
        """Run the server synchronously"""

        return web.run_app(self.app, host=host, port=port)

    async def start(self, host="0.0.0.0", port=80):
        """Start the server asynchronously."""

        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host=host, port=port)
        return await site.start()

    async def stop(self):
        """Stop the server asynchronously."""

        return await self.app.shutdown()
