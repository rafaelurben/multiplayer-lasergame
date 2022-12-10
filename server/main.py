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

def main(clientdir, url=None):
    server = GameServer(clientdir)

    loop.run_until_complete(server.start())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(server.stop())
        loop.close()

if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    clientdir = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'client')

    if is_ngrok_available():
        with NgrokTunnel() as ngrok_url:
            log.info("[Server] Tunnel URL: %s", ngrok_url)
            main(clientdir, ngrok_url)
    else:
        log.warning("[Server] ngrok is not in PATH! Please install it from https://ngrok.com/download or add it to PATH.")
        main(clientdir)
