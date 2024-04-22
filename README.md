# Multiplayer laser game

A simple 2-team laser game. Made to be played with friends in the same room.

Note: While the possible amount of players is two or more, the game is not recommended to be played
by more than 8 people.

## Setup

Someone needs to use their device as a server.

### Server

The server can be started by running the `server/main.py` file.

#### Server requirements

- Python 3.9 or newer (required)
- Ngrok (highly recommended)
- Internet connection

#### Command arguments

- `--public`: Start the server and use the PUBLIC_URL environment variable
- `--ngrok`: Use a ngrok tunnel and use its URL
- `--no-reconnect`: Disable the reconnect feature

#### Without ngrok

To run the game without ngrok, all players need to be in the same network or port forwarding needs
to be set up. Also, some firewall settings might have to be changed.

### Host

One device has to connect as the host. Practically, this should be the same device as the server.

To do this, the host has to open the ngrok URL printed to the console or `localhost` (if it's the
same device as the server). Then, select "Join as spectator".

### Join

Players and other spectators can then join via QR code or URL provided by the host.
