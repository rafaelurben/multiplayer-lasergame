class GameSocket {
    constructor() {
        this.socket = undefined;
        this.mode = undefined;
        this.game = {
            "state": undefined,
            "players": {},
        }

        this.connect();
    }

    connect() {
        let prot = location.protocol === "http:" ? "ws://" : "wss://";
        
        let newthis = this; // Ugly hack to get around the fact that "this" is not the same in the callback
        let newsock = new WebSocket(prot + location.host + "/ws");

        newsock.onopen = function (event) {
            console.log("[WS] Connection established!");
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
            case "connection_established": {
                this.mode = json.mode;
                this.game.state = json.game_state;
                this.game.players = json.players;
                document.getElementById("block_connect").classList.add("hidden");
                if (this.mode === "player") document.getElementById("block_teamselect").classList.remove("hidden");
                break;
            }
            case "player_updated": {
                this.game.players[json.id] = json.player;
                break;
            }
            case "player_connected": {
                this.game.players[json.id] = json.player;
                break;
            }
            case "player_disconnected": {
                delete this.game.players[json.id];
                break;
            }
            default: {
                console.warning("[WS] Unknown action received:", json);
            }
        }
    }

    send(json) {
        this.socket.send(JSON.stringify(json));
        console.debug(`[WS] Sent:`, json);
    }

    joinAsPlayer(name) {
        if (this.mode !== undefined) {
            console.error("[WS] Cannot setup twice!");
            return;
        } else if (name === undefined) {
            name = document.getElementById("nameinput").value;
        }

        if (name === "") {
            alert("Please enter a name!");
            return;
        }

        this.send({"action": "setup", "mode": "player", "name": name})
    }

    joinAsSpectator() {
        if (this.mode !== undefined) {
            console.error("[WS] Cannot setup twice!");
            return;
        }
        this.send({"action": "setup", "mode": "spectator"})
    }

    selectTeam(team) {
        this.send({"action": "select_team", "team": team});
    }
}
