import aiohttp
import logging
import os.path
from aiohttp import web

log = logging.getLogger(__name__)

def serve_file(*path):
    """Serve a file from the client directory."""

    abs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client', *path)
    return lambda request: web.FileResponse(abs_path)

async def websocket_handler(request):
    """Handle incoming websocket connections."""

    ws_current = web.WebSocketResponse()
    await ws_current.prepare(request)

    # Join

    name = "anyone"
    log.info('%s joined.', name)
    await ws_current.send_json({'action': 'connect', 'name': name})

    # Inform others and add to list

    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'join', 'name': name})
    request.app['websockets'][name] = ws_current

    # Main loop

    try:
        while True:
            msg = await ws_current.receive()

            if msg.type == aiohttp.WSMsgType.text:
                for ws in request.app['websockets'].values():
                    if ws is not ws_current:
                        await ws.send_json(
                            {'action': 'sent', 'name': name, 'text': msg.data})
            else:
                break
    except RuntimeError:
        pass

    # On disconnect / error

    del request.app['websockets'][name]
    log.info('%s disconnected.', name)
    for ws in request.app['websockets'].values():
        await ws.send_json({'action': 'disconnect', 'name': name})

    return ws_current

async def shutdown(app):
    """Cleanup tasks tied to the application's shutdown."""

    for ws in app['websockets'].values():
        await ws.close()
    app['websockets'].clear()

async def init_app():
    """Create the aiohttp application."""

    app = web.Application()
    app.add_routes([
        web.get('/ws', websocket_handler),
        web.get('/', serve_file("index.html")),
        web.get('/static/js/connection.js', serve_file("static", "js", "connection.js")),
    ])
    app['websockets'] = {}
    app.on_shutdown.append(shutdown)
    return app


if __name__ == "__main__":
    web.run_app(init_app(), host="0.0.0.0", port=80)
