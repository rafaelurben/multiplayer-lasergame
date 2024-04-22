import logging
import sys
import os.path
import asyncio

from server_game import GameServer
from ngrok_helpers import NgrokTunnel, is_ngrok_available

log = logging.getLogger()
log.setLevel(logging.DEBUG)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
log.addHandler(stream)


def main(*args, **kwargs):
    allow_reconnect = "--no-reconnect" not in sys.argv

    log.info("[Server] Starting server with reconnect %s...",
             "enabled" if allow_reconnect else "disabled")

    server = GameServer(*args, allow_reconnect=allow_reconnect, **kwargs)

    try:
        loop.run_until_complete(server.start())
        loop.run_until_complete(server.gameloop())
    except KeyboardInterrupt:
        loop.run_until_complete(server.stop())
        loop.close()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    clientdir = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'client')

    if "--ngrok" in sys.argv:
        if is_ngrok_available():
            log.info("[Server] Opening ngrok tunnel...")
            with NgrokTunnel() as ngrok_url:
                log.info("[Server] Tunnel URL: %s", ngrok_url)
                main(clientdir, public_url=ngrok_url)
        else:
            log.warning(
                "[Server] ngrok is not in PATH! Please install it from https://ngrok.com/download or add it to PATH.")
            log.info("[Server] Starting server without ngrok tunnel.")

    url = os.environ.get('PUBLIC_URL', 'http://localhost')
    log.info(f"[Server] URL: {url}")
    main(clientdir, public_url=url if "--public" in sys.argv else None)
