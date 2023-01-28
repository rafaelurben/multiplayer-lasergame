class GameSocket {
    constructor(game) {
        this.socket = undefined;
        this.wsid = undefined;
        this.game = game;

        this.connect();
        this.setupKeybinds();
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
                console.warn('[WS] Connection died! Code:', event, 'Reason:', event.reason);
                alert(`[Error] Connection died! Code: ${event.code} - Reason: ${event.reason}`);
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
                this.game.joining_allowed = json.joining_allowed;
                this.game.joining_allowed_reason = json.joining_allowed_reason;
                this.game.public_url = json.public_url;
                break;
            }
            case "room_joined": {
                this.game.client.mode = json.mode;
                this.game.players = json.players;
                if (json.mode === "player") {
                    this.game.player = json.players[this.game.client.id];
                }
                this.game.state = json.game_state;
                break;
            }
            case "room_left": {
                this.game.client.mode = "connected";
                this.game.players = {};
                this.game.player = {};
                this.game.state = undefined;
                break;
            }
            case "joining_toggled": {
                this.game.joining_allowed = json.allowed;
                this.game.joining_allowed_reason = json.reason;
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
                if (json.id === this.game.client.id) {
                    this.game.player = json.player;
                }
                break;
            }
            case "player_left": {
                delete this.game.players[json.id];
                break;
            }
            case "state_changed": {
                this.game.state = json.state;
                break;
            }
            case "game_params_set": {
                this.game.mapWidth = json.mapWidth;
                this.game.mapHeight = json.mapHeight;
                break;
            }
            default: {
                console.warn("[WS] Unknown action received:", json);
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

    leave() {
        if (this.game.client.mode === "connected") {
            console.error("[WS] Not joined!");
            return;
        }
        if (this.game.client.mode.startsWith("lobby") || confirm("Are you sure you want to leave?")) {
            this.send({"action": "leave_room"});
        }
    }

    selectTeam(team) {
        this.send({"action": "select_team", "team": team});
    }

    action(action, data) {
        this.send({"action": action, ...data});
    }

    setupKeybinds() {
        let newthis = this;
        document.addEventListener("keydown", function (event) {
            if (event.ctrlKey || event.altKey || event.metaKey) {
                // Ignore keybinds if ctrl/alt/meta is pressed
                return;
            }
            if ($("input").is(":focus")) {
                // Ignore keybinds if input is focused
                return;
            }

            if (newthis.game.client.mode === 'master') {
                if (event.key === "s") {
                    // s: Start/stop game
                    event.preventDefault();
                    if (newthis.game.state === 'ingame') {
                        newthis.action('end_game');
                    } else {
                        newthis.action('start_game');
                    }
                } else if (event.key === "j") {
                    // j: Toggle joining
                    if (newthis.game.state !== 'ingame') {
                        event.preventDefault();
                        newthis.action('toggle_joining');
                    }
                } else if (event.key === "t") {
                    // t: Toggle teamlock
                    if (newthis.game.state !== 'ingame') {
                        event.preventDefault();
                        newthis.action('toggle_teamlock');
                    }
                } else if (event.key === "h") {
                    // h: Shuffle teams
                    if (newthis.game.state !== 'ingame') {
                        event.preventDefault();
                        newthis.action('shuffle_teams');
                    }
                } else if (event.key === "c") {
                    // c: Toggle controls
                    if (newthis.game.state !== 'ingame') {
                        event.preventDefault();
                        $('#master-controls').toggleClass('userhidden');
                        if (newthis.game.canvas) newthis.game.canvas.resize();
                    }
                }
            } else if (newthis.game.client.mode === 'player') {
                if (newthis.game.state === 'ingame') {
                    if (event.key === "i") {
                        // i: Toggle inventory
                        event.preventDefault();
                        $('#player-inventory').toggleClass('userhidden');
                        if (newthis.game.canvas) newthis.game.canvas.resize();
                    } else if (event.key === "c") {
                        // c: Toggle controls
                        event.preventDefault();
                        $('#player-controls').toggleClass('userhidden');
                        if (newthis.game.canvas) newthis.game.canvas.resize();
                    }
                }
            }

            if (event.key === "f") {
                // f: Toggle soft full screen (toggle menubar)
                event.preventDefault();
                $("#menubar").toggleClass("hidden");

                if (newthis.game.canvas) {
                    newthis.game.canvas.resize();
                }
            } else if (event.key === "F") {
                // F: Toggle full screen
                event.preventDefault();
                if (document.fullscreenElement === null) {
                    document.documentElement.requestFullscreen();
                } else {
                    document.exitFullscreen();
                }

                if (newthis.game.canvas) {
                    newthis.game.canvas.resize();
                }
            } else if (event.key === "l") {
                // l: Leave room
                event.preventDefault();
                newthis.leave();
            } else if (event.key === "q") {
                // q: Show QR code
                event.preventDefault();
                $("#show_qrcode").click();
            }
        });
    }
}
