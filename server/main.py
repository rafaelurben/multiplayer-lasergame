import logging
import time
from server import BasicServer

log = logging.getLogger()


class GameServer(BasicServer):
    async def handle_message_json(self, data, ws, wsid):
        """Handle incoming messages in json format."""

        await self.send_all_json({'action': 'sent', 'wsid': wsid, 'data': data}, exclude=ws)
        # if data['action'] == 'connect':
        #     await self.onconnect(ws, data)
        # elif data['action'] == 'sent':
        #     await self.onsent(ws, data)
        # elif data['action'] == 'disconnect':
        #     await self.ondisconnect(ws, data)
        # else:
        #     log.warning('Unknown action: %s', data['action'])


if __name__ == "__main__":
    server = BasicServer()
    server.run()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(server.start())
