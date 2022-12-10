class GameSocket {
    constructor(game) {
        this.socket = undefined;
        this.wsid = undefined;
        this.game = game;

        this.connect();
    }

    connect() {
        let prot = location.protocol === "http:" ? "ws://" : "wss://";
        
        let newthis = this; // Ugly hack to get around the fact that "this" is not the same in the callback
        let newsock = new WebSocket(prot + location.host + "/ws");

        newsock.onopen = function (event) {
            console.log("[WS] Connection established!");
            newthis.game.updateUi();
        };

        newsock.onmessage = function (event) {
            let json = JSON.parse(event.data);
            console.debug("[WS] Data received:", json);
            newthis.onreceive(json);
        };

        newsock.onclose = function (event) {
            if (event.wasClean) {
                console.log(`[WS] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
            } else {
                // e.g. server process killed or network down
                // event.code is usually 1006 in this case
                console.warn('[WS] Connection died', event);
                alert('[Error] Connection died');
                location.reload();
            }
        };

        newsock.onerror = function (error) {
            console.warn("[WS] Error:", error);
        };

        this.socket = newsock;
    }

    onreceive(json) {
        switch (json.action) {
            case "message": {
                console.log("Message received from " + json.id + ": " + json.message);
                break;
            }
            case "alert": {
                alert(json.message);
                break;
            }
            case "connected": {
                this.wsid = json.id;
                this.game.client.id = json.id;
                this.game.client.mode = "connected";
                break;
            }
            case "room_joined": {
                this.game.client.mode = json.mode;
                this.game.state = json.game_state;
                this.game.players = json.players;
                break;
            }
            case "room_left": {
                this.game.client.mode = "connected";
                this.game.state = undefined;
                this.game.players = {};
                this.game.player = {};
                break;
            }
            case "player_updated": {
                this.game.players[json.id] = json.player;
                if (json.id === this.game.client.id) {
                    this.game.player = json.player;
                }
                break;
            }
            case "player_joined": {
                this.game.players[json.id] = json.player;
                break;
            }
            case "player_left": {
                delete this.game.players[json.id];
                break;
            }
            default: {
                console.warning("[WS] Unknown action received:", json);
            }
        }
        this.game.updateUi();
    }

    send(json) {
        this.socket.send(JSON.stringify(json));
        console.debug(`[WS] Sent:`, json);
    }

    joinAsPlayer(name) {
        if (this.game.client.mode !== "connected") {
            console.error("[WS] Already joined!");
            return;
        } else if (name === undefined) {
            name = document.getElementById("nameinput").value;
        }

        if (name === "") {
            alert("Please enter a name!");
            return;
        }

        this.game.player.name = name;
        this.send({"action": "join_room", "mode": "player", "name": name})
    }

    joinAsSpectator() {
        if (this.game.client.mode !== "connected") {
            console.error("[WS] Already joined!");
            return;
        }
        this.send({"action": "join_room", "mode": "spectator"})
    }

    selectTeam(team) {
        this.send({"action": "select_team", "team": team});
    }
}
