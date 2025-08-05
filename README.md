# Multiplayer laser game

A simple 2-team laser game. Made to be played with friends in the same room.

Note: While the possible amount of players is two or more, the game is not recommended to be played
by more than 8 people.

## Setting up a server

### Server requirements

- Python 3.9 or newer (required)
- Git (optional, for cloning the repository)
- A networking setup where all players can connect to the server
- Internet connection

### Installation

- Clone the repository: (alternatively, you can download the ZIP file and extract it)
    ```bash
    git clone https://github.com/rafaelurben/multiplayer-lasergame.git
    ```
- Change into the directory:
    ```bash
    cd multiplayer-lasergame
    ```
- Install the requirements:
    ```bash
    python -m pip install -r requirements.txt
    ```
- Start the server:
    ```bash
    python server/main.py
    ```

### Command arguments

- `--public`: Use the PUBLIC_URL environment variable as the join URL.
- `--ngrok`: Use a ngrok tunnel and use its URL
- `--no-reconnect`: Disable the reconnect feature

## Controlling & Playing the game

### Host

One device has to connect as the host. The host should share their screen with the other players.

The host has to open the game URL in a web browser with `?master` appended to the URL. Then, they have to select "Join
as spectator".

### Join

Players and other spectators can then join via QR code or URL provided by the host.
